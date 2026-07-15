#!/usr/bin/env python3
import argparse
import csv
import datetime
import json
import time
from pathlib import Path
from typing import Optional

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Run Set-B evaluation against backend API.")
    parser.add_argument("--csv", required=True, help="Input CSV path.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="Backend API base URL.")
    parser.add_argument("--output", default="eval_results", help="Output prefix.")
    parser.add_argument("--limit", type=int, default=None, help="Optional question limit.")
    parser.add_argument("--skip-sts", action="store_true", help="Accepted for compatibility.")
    parser.add_argument("--skip-ragas", action="store_true", help="Accepted for compatibility.")
    return parser.parse_args()


def _parse_sse_stream(response):
    event_type = "message"
    data_lines: list[str] = []
    for raw_line in response.iter_lines(decode_unicode=True):
        line = raw_line if raw_line is not None else ""
        if line == "":
            if data_lines:
                data_str = "\n".join(data_lines)
                yield event_type, data_str
                data_lines = []
                event_type = "message"
            continue
        if line.startswith("event:"):
            event_type = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].strip())


def load_eval_rows(csv_path: str) -> list[dict]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "question_id": int((row.get("QID") or "0").strip() or "0"),
                    "question_title": (row.get("Title") or "").strip(),
                    "question": (row.get("QUESTION") or row.get("Title") or "").strip(),
                    "cutoff_date": (row.get("Created") or "").strip(),
                    "ground_truth": (row.get("GROUND_TRUTH") or "").strip(),
                }
            )
    return rows


def call_rag_api(question: str, cutoff_date: str, api_base: str, question_id: Optional[int] = None) -> dict:
    form_data = {
        "user_query": question,
        "search_pubmed": "true",
        "search_pmid": "false",
        "pmids": "[]",
        "search_pdf": "false",
        "max_date": cutoff_date,
        "benchmark_mode": "true",
    }
    if question_id is not None:
        form_data["question_id"] = str(question_id)
    post_resp = requests.post(
        f"{api_base}/process_detailed_combined_query",
        data=form_data,
        timeout=None,
    )
    post_resp.raise_for_status()
    session_id = post_resp.json().get("session_id")
    if not session_id:
        raise ValueError("No session_id in response")

    sse_resp = requests.get(
        f"{api_base}/sse",
        params={"session_id": session_id},
        stream=True,
        timeout=(10, None),
    )
    sse_resp.raise_for_status()

    for _evt, data_str in _parse_sse_stream(sse_resp):
        if not data_str:
            continue
        try:
            payload = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        final_payload = None
        if isinstance(payload, dict) and "end_output" in payload:
            final_payload = payload
        elif isinstance(payload, dict) and isinstance(payload.get("update"), dict):
            inner = payload.get("update") or {}
            if "end_output" in inner:
                final_payload = inner

        if final_payload is not None:
            return final_payload

    return {}


def save_results(records: list[dict], output_prefix: str) -> None:
    json_path = f"{output_prefix}.json"
    csv_path = f"{output_prefix}.csv"
    out_dir = Path(json_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "question_id",
        "question_title",
        "question",
        "cutoff_date",
        "ground_truth",
        "retrieval_mode",
        "generated_answer",
        "runtime_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost_usd",
        "llm_calls",
        "duration_seconds",
        "llm_calls_count",
        "llm_prompt_tokens",
        "llm_completion_tokens",
        "llm_total_tokens",
        "llm_cost_usd_estimate",
        "llm_cost_by_stage",
        "api_error",
        "eval_timestamp",
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            row = dict(rec)
            if isinstance(row.get("llm_calls"), list):
                row["llm_calls"] = json.dumps(row["llm_calls"], ensure_ascii=False)
            writer.writerow(row)

    benchmark_rows = []
    for rec in records:
        benchmark_rows.append(
            {
                "question_id": rec.get("question_id"),
                "retrieval_mode": rec.get("retrieval_mode"),
                "runtime_seconds": float(rec.get("runtime_seconds") or rec.get("duration_seconds") or 0.0),
                "input_tokens": int(rec.get("input_tokens") or rec.get("llm_prompt_tokens") or 0),
                "output_tokens": int(rec.get("output_tokens") or rec.get("llm_completion_tokens") or 0),
                "total_tokens": int(rec.get("total_tokens") or rec.get("llm_total_tokens") or 0),
                "estimated_cost_usd": float(rec.get("estimated_cost_usd") or rec.get("llm_cost_usd_estimate") or 0.0),
            }
        )

    benchmark_json_path = out_dir / "benchmark_results.json"
    benchmark_csv_path = out_dir / "benchmark_results.csv"
    with open(benchmark_json_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_rows, f, ensure_ascii=False, indent=2)

    benchmark_fields = [
        "question_id",
        "retrieval_mode",
        "runtime_seconds",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "estimated_cost_usd",
    ]
    with open(benchmark_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=benchmark_fields, extrasaction="ignore")
        writer.writeheader()
        for row in benchmark_rows:
            writer.writerow(row)


def run():
    args = parse_args()
    health = requests.get(f"{args.api_url}/health", timeout=5)
    health.raise_for_status()

    rows = load_eval_rows(args.csv)
    if args.limit is not None:
        rows = rows[: args.limit]

    records: list[dict] = []
    for i, row in enumerate(rows, start=1):
        print(f"[{i}/{len(rows)}] Q#{row['question_id']}: {row['question_title'][:80]}")
        t0 = time.time()
        try:
            result = call_rag_api(
                question=row["question"],
                cutoff_date=row["cutoff_date"],
                api_base=args.api_url,
                question_id=row.get("question_id"),
            )
            record = {
                **row,
                "generated_answer": result.get("end_output") or "",
                "retrieval_mode": result.get("retrieval_mode"),
                "runtime_seconds": float(result.get("runtime_seconds") or round(time.time() - t0, 3)),
                "input_tokens": int(result.get("input_tokens") or 0),
                "output_tokens": int(result.get("output_tokens") or 0),
                "total_tokens": int(result.get("total_tokens") or 0),
                "estimated_cost_usd": float(result.get("estimated_cost_usd") or 0.0),
                "llm_calls": result.get("llm_calls") or [],
                # Backward-compatible aliases:
                "duration_seconds": float(result.get("runtime_seconds") or result.get("duration_seconds") or 0.0),
                "llm_calls_count": int(len(result.get("llm_calls") or [])),
                "llm_prompt_tokens": int(result.get("input_tokens") or result.get("llm_prompt_tokens") or 0),
                "llm_completion_tokens": int(result.get("output_tokens") or result.get("llm_completion_tokens") or 0),
                "llm_total_tokens": int(result.get("total_tokens") or result.get("llm_total_tokens") or 0),
                "llm_cost_usd_estimate": float(result.get("estimated_cost_usd") or result.get("llm_cost_usd_estimate") or 0.0),
                "api_error": None,
                "eval_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        except Exception as exc:
            record = {
                **row,
                "generated_answer": "",
                "duration_seconds": round(time.time() - t0, 3),
                "llm_calls_count": 0,
                "llm_prompt_tokens": 0,
                "llm_completion_tokens": 0,
                "llm_total_tokens": 0,
                "llm_cost_usd_estimate": 0.0,
                "runtime_seconds": round(time.time() - t0, 3),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "llm_calls": [],
                "api_error": str(exc),
                "eval_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        records.append(record)
        save_results(records, args.output)

    save_results(records, args.output)
    print(f"[OUTPUT] Saved {len(records)} rows -> {args.output}.json/.csv")


if __name__ == "__main__":
    run()
