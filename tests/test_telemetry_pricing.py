"""Regression tests: models without a known price must not be reported as free."""

import sys
import unittest
import uuid
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "customnerd-backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from benchmarking import telemetry as t  # noqa: E402

USAGE = {"prompt_tokens": 1000, "completion_tokens": 1000}


def run_calls(*calls):
    rid = "req-" + uuid.uuid4().hex
    t.begin_request(rid)
    for provider, model in calls:
        t.record_llm_call(provider=provider, model=model, usage=USAGE, request_id=rid)
    return t.finalize_request(rid)


class LookupRates(unittest.TestCase):
    def test_exact_known_model(self):
        self.assertEqual(t._lookup_rates("openai", "gpt-4o-mini"), {"input": 0.00015, "output": 0.0006})

    def test_prefix_match_known_model(self):
        self.assertEqual(t._lookup_rates("openai", "gpt-4o-mini-2024-07-18")["input"], 0.00015)

    def test_unknown_model_is_none(self):
        self.assertIsNone(t._lookup_rates("openai", "gpt-6.1-sol"))

    def test_unknown_provider_is_none(self):
        self.assertIsNone(t._lookup_rates("mystery", "x"))

    def test_ollama_default_stays_free(self):
        self.assertEqual(t._lookup_rates("ollama", "llama3"), {"input": 0.0, "output": 0.0})

    def test_default_key_is_not_a_model_name(self):
        self.assertIsNone(t._lookup_rates("openai", "__default__"))

    def test_resolve_rates_legacy_contract_unchanged(self):
        self.assertEqual(t._resolve_rates("openai", "gpt-6.1-sol"), {"input": 0.0, "output": 0.0})


class Finalize(unittest.TestCase):
    def test_known_model_cost_and_not_partial(self):
        r = run_calls(("openai", "gpt-4o-mini"))
        self.assertAlmostEqual(r["estimated_cost_usd"], 0.00075)
        self.assertFalse(r["cost_is_partial"])
        self.assertEqual(r["unpriced_models"], [])
        self.assertTrue(r["llm_calls"][0]["priced"])

    def test_unknown_model_flagged_not_free(self):
        r = run_calls(("openai", "gpt-6.1-sol"))
        self.assertTrue(r["cost_is_partial"])
        self.assertEqual(r["unpriced_models"], ["openai:gpt-6.1-sol"])
        call = r["llm_calls"][0]
        self.assertFalse(call["priced"])
        self.assertIsNone(call["estimated_cost_usd"])

    def test_unknown_model_tokens_still_counted(self):
        r = run_calls(("openai", "gpt-6.1-sol"))
        self.assertEqual(r["input_tokens"], 1000)
        self.assertEqual(r["output_tokens"], 1000)

    def test_mixed_cost_is_lower_bound_and_partial(self):
        r = run_calls(("openai", "gpt-4o-mini"), ("openai", "gpt-6.1-sol"))
        self.assertAlmostEqual(r["estimated_cost_usd"], 0.00075)
        self.assertTrue(r["cost_is_partial"])
        self.assertEqual(r["total_tokens"], 4000)

    def test_unpriced_models_deduplicated_and_sorted(self):
        r = run_calls(("openai", "zz-new"), ("openai", "aa-new"), ("openai", "zz-new"))
        self.assertEqual(r["unpriced_models"], ["openai:aa-new", "openai:zz-new"])

    def test_ollama_call_priced_zero_not_partial(self):
        r = run_calls(("ollama", "llama3"))
        self.assertFalse(r["cost_is_partial"])
        self.assertTrue(r["llm_calls"][0]["priced"])
        self.assertEqual(r["estimated_cost_usd"], 0.0)

    def test_unknown_request_id_finalize_has_no_crash(self):
        r = t.finalize_request("never-started")
        self.assertEqual(r["estimated_cost_usd"], 0.0)

    def test_requests_do_not_leak_flags_between_each_other(self):
        run_calls(("openai", "gpt-6.1-sol"))
        r = run_calls(("openai", "gpt-4o-mini"))
        self.assertFalse(r["cost_is_partial"])


class EvalExport(unittest.TestCase):
    """eval_rag exports must not present a partial cost as a complete one."""

    def _export(self, records):
        import csv
        import json
        import tempfile

        import eval_rag

        with tempfile.TemporaryDirectory() as d:
            prefix = str(Path(d) / "out")
            eval_rag.save_results(records, prefix)
            with open(prefix + ".csv", encoding="utf-8") as f:
                main_rows = list(csv.DictReader(f))
            with open(str(Path(d) / "benchmark_results.csv"), encoding="utf-8") as f:
                bench_rows = list(csv.DictReader(f))
            with open(str(Path(d) / "benchmark_results.json"), encoding="utf-8") as f:
                bench_json = json.load(f)
        return main_rows, bench_rows, bench_json

    def _rec(self, partial, models):
        return {
            "question_id": "1", "retrieval_mode": "x", "runtime_seconds": 1.0,
            "input_tokens": 10, "output_tokens": 5, "total_tokens": 15,
            "estimated_cost_usd": 0.001, "llm_calls": [],
            "cost_is_partial": partial, "unpriced_models": models,
        }

    def test_benchmark_csv_marks_partial_and_names_models(self):
        _, bench, _ = self._export([self._rec(True, ["openai:gpt-6.1-sol"])])
        self.assertEqual(bench[0]["cost_is_partial"], "True")
        self.assertEqual(bench[0]["unpriced_models"], "openai:gpt-6.1-sol")

    def test_benchmark_csv_complete_row_not_partial(self):
        _, bench, _ = self._export([self._rec(False, [])])
        self.assertEqual(bench[0]["cost_is_partial"], "False")
        self.assertEqual(bench[0]["unpriced_models"], "")

    def test_main_csv_has_flag_columns_and_joined_models(self):
        main, _, _ = self._export([self._rec(True, ["a:x", "b:y"])])
        self.assertEqual(main[0]["cost_is_partial"], "True")
        self.assertEqual(main[0]["unpriced_models"], "a:x;b:y")

    def test_benchmark_json_flag_is_boolean(self):
        _, _, js = self._export([self._rec(True, ["a:x"])])
        self.assertIs(js[0]["cost_is_partial"], True)

    def test_old_records_without_flag_default_to_not_partial(self):
        rec = self._rec(False, [])
        rec.pop("cost_is_partial"); rec.pop("unpriced_models")
        _, bench, _ = self._export([rec])
        self.assertEqual(bench[0]["cost_is_partial"], "False")


if __name__ == "__main__":
    unittest.main()
