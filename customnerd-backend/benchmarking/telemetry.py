import os
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Optional

import tiktoken


_ENC = tiktoken.get_encoding("cl100k_base")
_LOCK = threading.Lock()
_REQUEST_ID_CTX: ContextVar[Optional[str]] = ContextVar("benchmark_request_id", default=None)
_LIFECYCLE_STAGE_CTX: ContextVar[Optional[str]] = ContextVar("benchmark_lifecycle_stage", default=None)
_REQUESTS: Dict[str, Dict[str, Any]] = {}


# Estimated USD pricing per 1K tokens (input/output).
_PRICING_PER_1K = {
    "openai": {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
    },
    "anthropic": {
        "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
        "claude-haiku-4-5": {"input": 0.0008, "output": 0.004},
    },
    "gemini": {
        "gemini-2.5-flash": {"input": 0.00035, "output": 0.00105},
    },
    "ollama": {
        "__default__": {"input": 0.0, "output": 0.0},
    },
}

LIFECYCLE_ORDER = [
    "Question Start",
    "Query Generation",
    "Query Cleaning",
    "Retrieval",
    "Reranking",
    "Final Answer",
    "Question End",
]


def _is_truthy(raw: str) -> bool:
    return str(raw or "").strip().lower() in {"1", "true", "yes", "on"}


def is_benchmark_mode() -> bool:
    # Optional global switch; request-level benchmark_mode is still authoritative.
    return _is_truthy(os.getenv("CLOUDNERD_BENCHMARK_MODE", "0"))


def _estimate_tokens(text: str) -> int:
    if not text:
        return 0
    try:
        return len(_ENC.encode(text))
    except Exception:
        return max(1, int(len(text.split()) * 1.3))


def _normalize_usage(usage: Any) -> Dict[str, int]:
    def _to_int(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            try:
                return int(float(value))
            except (TypeError, ValueError):
                return 0

    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    if isinstance(usage, dict):
        input_tokens = _to_int(
            usage.get("prompt_tokens")
            or usage.get("input_tokens")
            or usage.get("prompt_token_count")
            or 0
        )
        output_tokens = _to_int(
            usage.get("completion_tokens")
            or usage.get("output_tokens")
            or usage.get("candidates_token_count")
            or 0
        )
        total_tokens = _to_int(
            usage.get("total_tokens")
            or usage.get("total_token_count")
            or (input_tokens + output_tokens)
        )
        return {
            "input_tokens": max(0, input_tokens),
            "output_tokens": max(0, output_tokens),
            "total_tokens": max(0, total_tokens),
        }

    input_tokens = _to_int(
        getattr(usage, "prompt_tokens", 0)
        or getattr(usage, "input_tokens", 0)
        or getattr(usage, "prompt_token_count", 0)
        or 0
    )
    output_tokens = _to_int(
        getattr(usage, "completion_tokens", 0)
        or getattr(usage, "output_tokens", 0)
        or getattr(usage, "candidates_token_count", 0)
        or 0
    )
    total_tokens = _to_int(
        getattr(usage, "total_tokens", 0)
        or getattr(usage, "total_token_count", 0)
        or (input_tokens + output_tokens)
    )
    return {
        "input_tokens": max(0, input_tokens),
        "output_tokens": max(0, output_tokens),
        "total_tokens": max(0, total_tokens),
    }


def _resolve_rates(provider: str, model: str) -> Dict[str, float]:
    p = (provider or "").strip().lower()
    m = (model or "").strip()
    models = _PRICING_PER_1K.get(p, {})
    if m in models:
        return models[m]
    for key, rates in models.items():
        if key != "__default__" and m.startswith(key):
            return rates
    return models.get("__default__", {"input": 0.0, "output": 0.0})


def _new_request_state(request_id: str, question_id: Optional[str], retrieval_mode: Optional[str]) -> Dict[str, Any]:
    lifecycle = {
        stage: {
            "runtime_seconds": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "llm_calls_count": 0,
        }
        for stage in LIFECYCLE_ORDER
    }
    return {
        "request_id": request_id,
        "question_id": str(question_id) if question_id is not None else None,
        "retrieval_mode": retrieval_mode,
        "started_at": time.time(),
        "runtime_seconds": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
        "llm_calls": [],
        "lifecycle": lifecycle,
    }


def _resolve_request_id(request_id: Optional[str]) -> Optional[str]:
    if request_id:
        return request_id
    return _REQUEST_ID_CTX.get()


def begin_request(
    request_id: str,
    *,
    question_id: Optional[str] = None,
    retrieval_mode: Optional[str] = None,
) -> None:
    with _LOCK:
        _REQUESTS[request_id] = _new_request_state(request_id, question_id, retrieval_mode)
    _REQUEST_ID_CTX.set(request_id)


def set_request_context(request_id: str) -> None:
    _REQUEST_ID_CTX.set(request_id)


def clear_request_context(request_id: Optional[str] = None) -> None:
    _REQUEST_ID_CTX.set(None)
    _LIFECYCLE_STAGE_CTX.set(None)


def set_lifecycle_stage(stage: Optional[str]) -> None:
    _LIFECYCLE_STAGE_CTX.set(stage)


def clear_lifecycle_stage() -> None:
    _LIFECYCLE_STAGE_CTX.set(None)


def add_stage_runtime(stage: str, runtime_seconds: float, *, request_id: Optional[str] = None) -> None:
    rid = _resolve_request_id(request_id)
    if not rid:
        return
    with _LOCK:
        state = _REQUESTS.get(rid)
        if state is None:
            return
        lifecycle = state.get("lifecycle", {})
        stage_entry = lifecycle.get(stage)
        if stage_entry is None:
            stage_entry = {
                "runtime_seconds": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "llm_calls_count": 0,
            }
            lifecycle[stage] = stage_entry
        stage_entry["runtime_seconds"] = round(
            float(stage_entry.get("runtime_seconds", 0.0)) + max(0.0, runtime_seconds),
            6,
        )


@contextmanager
def lifecycle_scope(stage: str, *, request_id: Optional[str] = None):
    rid = _resolve_request_id(request_id)
    if not rid:
        yield
        return
    prev_stage = _LIFECYCLE_STAGE_CTX.get()
    _LIFECYCLE_STAGE_CTX.set(stage)
    t0 = time.time()
    try:
        yield
    finally:
        elapsed = max(0.0, time.time() - t0)
        add_stage_runtime(stage, elapsed, request_id=rid)
        _LIFECYCLE_STAGE_CTX.set(prev_stage)


def set_retrieval_mode(retrieval_mode: str, *, request_id: Optional[str] = None) -> None:
    rid = _resolve_request_id(request_id)
    if not rid:
        return
    with _LOCK:
        state = _REQUESTS.get(rid)
        if state is not None:
            state["retrieval_mode"] = retrieval_mode


def record_llm_call(
    *,
    provider: str,
    model: str,
    usage: Any = None,
    stage: Optional[str] = None,
    prompt_text: Optional[str] = None,
    completion_text: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    try:
        rid = _resolve_request_id(request_id)
        if not rid:
            return
        with _LOCK:
            state = _REQUESTS.get(rid)
            if state is None:
                return

            tokens = _normalize_usage(usage)
            if tokens["input_tokens"] == 0 and prompt_text:
                tokens["input_tokens"] = _estimate_tokens(prompt_text)
            if tokens["output_tokens"] == 0 and completion_text:
                tokens["output_tokens"] = _estimate_tokens(completion_text)
            if tokens["total_tokens"] == 0:
                tokens["total_tokens"] = tokens["input_tokens"] + tokens["output_tokens"]

            rates = _resolve_rates(provider, model)
            call_cost = (
                (tokens["input_tokens"] / 1000.0) * rates["input"]
                + (tokens["output_tokens"] / 1000.0) * rates["output"]
            )
            lifecycle_stage = _LIFECYCLE_STAGE_CTX.get() or "Unscoped"

            state["input_tokens"] += tokens["input_tokens"]
            state["output_tokens"] += tokens["output_tokens"]
            state["total_tokens"] += tokens["total_tokens"]
            state["estimated_cost_usd"] += call_cost
            state["llm_calls"].append(
                {
                    "timestamp": time.time(),
                    "provider": provider,
                    "model": model,
                    "stage": stage or "unspecified",
                    "lifecycle_stage": lifecycle_stage,
                    "input_tokens": tokens["input_tokens"],
                    "output_tokens": tokens["output_tokens"],
                    "total_tokens": tokens["total_tokens"],
                    "estimated_cost_usd": round(call_cost, 8),
                }
            )
            lifecycle = state.get("lifecycle", {})
            if lifecycle_stage not in lifecycle:
                lifecycle[lifecycle_stage] = {
                    "runtime_seconds": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost_usd": 0.0,
                    "llm_calls_count": 0,
                }
            lifecycle_stage_entry = lifecycle[lifecycle_stage]
            lifecycle_stage_entry["input_tokens"] += tokens["input_tokens"]
            lifecycle_stage_entry["output_tokens"] += tokens["output_tokens"]
            lifecycle_stage_entry["total_tokens"] += tokens["total_tokens"]
            lifecycle_stage_entry["estimated_cost_usd"] += call_cost
            lifecycle_stage_entry["llm_calls_count"] += 1
    except Exception:
        # Never interrupt model execution due to telemetry.
        return


def finalize_request(request_id: str) -> Dict[str, Any]:
    with _LOCK:
        state = _REQUESTS.get(request_id)
        if state is None:
            return {
                "question_id": None,
                "retrieval_mode": None,
                "runtime_seconds": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "llm_calls": [],
                "lifecycle": {},
            }
        state["runtime_seconds"] = round(max(0.0, time.time() - state["started_at"]), 3)
        lifecycle = state.get("lifecycle", {})
        for stage_name, stage_data in lifecycle.items():
            stage_data["runtime_seconds"] = round(float(stage_data.get("runtime_seconds", 0.0)), 6)
            stage_data["estimated_cost_usd"] = round(float(stage_data.get("estimated_cost_usd", 0.0)), 8)
        finalized = {
            "question_id": state.get("question_id"),
            "retrieval_mode": state.get("retrieval_mode"),
            "runtime_seconds": state.get("runtime_seconds", 0.0),
            "input_tokens": int(state.get("input_tokens", 0)),
            "output_tokens": int(state.get("output_tokens", 0)),
            "total_tokens": int(state.get("total_tokens", 0)),
            "estimated_cost_usd": round(float(state.get("estimated_cost_usd", 0.0)), 8),
            "llm_calls": list(state.get("llm_calls", [])),
            "lifecycle": lifecycle,
        }
        _REQUESTS.pop(request_id, None)
    clear_request_context(request_id)
    return finalized
