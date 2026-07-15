"""
Regression tests for the 2026-07 audit fixes.

Each test corresponds to a fix documented in `.claude/knowledge/UNDERSTANDING.md`
section 12 (Known Bugs & Open Questions). The tests are independent — each
function can be run in isolation via `pytest tests/test_fixes.py::<name>`.

Run with:
    customnerd-backend/nerd_engine_venv/bin/python3 -m pytest tests/test_fixes.py -v
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "customnerd-backend"
WEBSITE_DIR = REPO_ROOT / "customnerd-website"

# Make the backend importable as a package sibling.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Test isolation helpers
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """A FastAPI TestClient. Heavy module — module-scoped to avoid re-imports."""
    # Lazy import so individual tests that don't need the app don't pay the cost.
    import main  # noqa: F401
    from main import app
    return TestClient(app)


@pytest.fixture
def tmp_nerd(tmp_path, monkeypatch):
    """Create a fake nerd pack on disk, monkeypatch the active-nerd lookup, and yield the path."""
    nerd_name = "TestNerd"
    nerd_dir = tmp_path / "customnerd-backend" / "saved_states" / nerd_name
    nerd_dir.mkdir(parents=True)

    # Files that /save_state writes for a nerd
    (nerd_dir / "openai_prompts.py").write_text("# openai prompts for TestNerd\n")
    (nerd_dir / "user_env.js").write_text("// TestNerd user_env\n")
    (nerd_dir / "user_list_search.py").write_text("# TestNerd user_list_search\n")
    (nerd_dir / "user_search_apis.py").write_text("# TestNerd user_search_apis\n")
    (nerd_dir / "clean_query.py").write_text("# TestNerd clean_query\n")
    (nerd_dir / "variables.env").write_text("LLM=OpenAI\nOPENAI_API_KEY=sk-test\n")
    (nerd_dir / "historical_answer.json").write_text("[]")

    # Pretend the saved-state dir is relative to backend_dir so /load_state finds it.
    backend_tmp = tmp_path / "customnerd-backend"
    backend_tmp.mkdir(exist_ok=True)
    backend_root_clean_query = backend_tmp / "clean_query.py"
    backend_root_clean_query.write_text("# OLD clean_query\n")

    # Patch BACKEND_DIR resolution by monkeypatching os.path.dirname in the load_state path.
    # Simpler: place TestNerd inside the real saved_states dir.
    real_nerd_dir = BACKEND_DIR / "saved_states" / nerd_name
    if real_nerd_dir.exists():
        pytest.skip(f"Test nerd {nerd_name} already exists in saved_states")
    real_nerd_dir.mkdir(parents=True)
    for f in ["openai_prompts.py", "user_env.js", "user_list_search.py",
              "user_search_apis.py", "clean_query.py", "variables.env",
              "historical_answer.json"]:
        (real_nerd_dir / f).write_text(f"# {f} for TestNerd\n")

    yield real_nerd_dir

    # Cleanup
    import shutil
    if real_nerd_dir.exists():
        shutil.rmtree(real_nerd_dir)


# ---------------------------------------------------------------------------
# Fix 1 — /load_state must restore clean_query.py
# ---------------------------------------------------------------------------

class TestLoadStateRestoresCleanQuery:
    """Bug from gap-loadstate.md: /load_state silently drops clean_query.py."""

    def test_files_to_copy_includes_clean_query(self):
        """Static check: load_state's files_to_copy must include clean_query.py."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        # Find the /load_state handler and its files_to_copy block.
        m = re.search(
            r'@app\.post\("/load_state"\)[\s\S]+?files_to_copy\s*=\s*\[(.*?)\]',
            main_src,
            re.DOTALL,
        )
        assert m, "Could not locate /load_state handler or files_to_copy in main.py"
        block = m.group(1)
        assert '"clean_query.py"' in block, (
            "BUG: /load_state's files_to_copy is missing 'clean_query.py'. "
            "Saved nerds cannot restore per-nerd query-cleaning logic."
        )

    def test_save_and_load_file_lists_match(self):
        """The save list and load list must reference the same file set."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        # Locate /save_state
        save_block = re.search(
            r'@app\.post\("/save_state"\)[\s\S]+?files_to_copy\s*=\s*\[(.*?)\]',
            main_src,
            re.DOTALL,
        ).group(1)
        # Locate /load_state
        load_block = re.search(
            r'@app\.post\("/load_state"\)[\s\S]+?files_to_copy\s*=\s*\[(.*?)\]',
            main_src,
            re.DOTALL,
        ).group(1)
        save_files = set(re.findall(r'"([^"]+)"', save_block))
        load_files = set(re.findall(r'"([^"]+)"', load_block))
        missing = save_files - load_files
        assert not missing, (
            f"BUG: /load_state files_to_copy is missing files that /save_state writes: {missing}"
        )

    def test_load_state_copies_clean_query(self, client, tmp_nerd):
        """End-to-end: loading a saved nerd must copy clean_query.py to backend_dir."""
        # Snapshot backend's clean_query.py before
        clean_query_dst = BACKEND_DIR / "clean_query.py"
        backup = clean_query_dst.read_text()
        try:
            r = client.post("/load_state", data={"state_name": "TestNerd"})
            assert r.status_code == 200, f"load_state failed: {r.text}"
            # The nerd's clean_query.py is "# clean_query.py for TestNerd"
            # If load_state restored it, the backend file is no longer the previous contents.
            assert clean_query_dst.read_text() != backup, (
                "load_state did not update backend clean_query.py"
            )
            assert "TestNerd" in clean_query_dst.read_text(), (
                "load_state restored clean_query.py but with wrong content"
            )
        finally:
            # Restore the original clean_query.py so we don't leave the env in a bad state.
            clean_query_dst.write_text(backup)


# ---------------------------------------------------------------------------
# Fix 2 — llm_telemetry.py is dead code; deletion is safe
# ---------------------------------------------------------------------------

class TestLLMTelemetryDeleted:
    def test_llm_telemetry_file_does_not_exist(self):
        """The dead file must be gone."""
        assert not (BACKEND_DIR / "llm_telemetry.py").exists(), (
            "llm_telemetry.py still exists — but it has zero importers in the repo. "
            "It duplicates benchmarking/telemetry.py and should be deleted."
        )

    def test_no_python_file_imports_llm_telemetry(self):
        """After deletion, no .py file should still try to import it."""
        offenders = []
        for py in BACKEND_DIR.rglob("*.py"):
            if py.name == "llm_telemetry.py":
                continue
            try:
                text = py.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue  # skip binary or non-UTF8 files
            if re.search(r"from\s+llm_telemetry|import\s+llm_telemetry", text):
                offenders.append(str(py.relative_to(REPO_ROOT)))
        assert not offenders, (
            f"Stale llm_telemetry imports still exist: {offenders}"
        )

    def test_no_py_references_to_llm_telemetry_outside_knowledge(self):
        """No source file references the deleted module anywhere."""
        offenders = []
        for path in [BACKEND_DIR, WEBSITE_DIR]:
            for f in path.rglob("*"):
                if not f.is_file() or f.suffix in (".png", ".jpg", ".ico", ".woff", ".ttf"):
                    continue
                if f.suffix in (".py", ".js", ".html", ".css", ".json", ".env"):
                    try:
                        text = f.read_text(encoding="utf-8")
                    except (UnicodeDecodeError, OSError):
                        continue
                    if "llm_telemetry" in text:
                        offenders.append(str(f.relative_to(REPO_ROOT)))
        assert not offenders, (
            f"Stale llm_telemetry references still exist: {offenders}"
        )


# ---------------------------------------------------------------------------
# Fix 3 — index.js no longer calls dead /generate or /db_sim_search endpoints
# ---------------------------------------------------------------------------

class TestDeadRoutesRemoved:
    def test_index_js_has_no_dead_route_callers(self):
        """The frontend must not call /generate/{q} or /db_sim_search/{q} anymore.

        Comments explaining the removal are allowed — only executable code matters.
        """
        index_js = (WEBSITE_DIR / "index.js").read_text()
        # Strip line comments and block comments so the search ignores explanatory notes.
        code_only = re.sub(r"//.*?$|/\*[\s\S]*?\*/", "", index_js, flags=re.MULTILINE)
        assert "/generate/" not in code_only, (
            "/generate/{question} route does not exist on the backend; "
            "the index.js caller should be removed (or replaced with a real endpoint)."
        )
        assert "/db_sim_search/" not in code_only, (
            "/db_sim_search/{question} route does not exist on the backend; "
            "the index.js caller should be removed (or replaced with a real endpoint)."
        )

    def test_remaining_generate_endpoints_still_work(self):
        """Sanity: the /generate_code_endpoint and /generate_prompt_endpoint routes DO exist."""
        # Check that the real endpoints are still wired.
        main_src = (BACKEND_DIR / "main.py").read_text()
        assert "/generate_code_endpoint" in main_src
        assert "/generate_prompt_endpoint" in main_src


# ---------------------------------------------------------------------------
# Fix 4 — SSE idle-timeout fallback
# ---------------------------------------------------------------------------

class TestSSEIdleTimeout:
    def test_sse_idle_timeout_constant_exists(self):
        """main.py must declare a configurable SSE idle timeout."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        assert "SSE_IDLE_TIMEOUT_SECONDS" in main_src, (
            "SSE_IDLE_TIMEOUT_SECONDS constant is missing — clients may hang "
            "forever if the orchestrator crashes mid-pipeline."
        )

    def test_sse_event_generator_wraps_queue_get_with_timeout(self):
        """The SSE event_generator must wrap queue.get() in asyncio.wait_for."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        # Find event_generator
        m = re.search(
            r"async def event_generator[\s\S]*?(?=\nasync def |\n@)",
            main_src,
        )
        assert m, "Could not find event_generator in main.py"
        body = m.group(0)
        assert "asyncio.wait_for" in body, (
            "event_generator does not use asyncio.wait_for — idle timeout is broken"
        )
        assert "TimeoutError" in body, (
            "event_generator does not handle asyncio.TimeoutError — clients will hang"
        )

    def test_sse_idle_timeout_emits_keepalive_not_close(self):
        """On timeout the generator must keep the stream alive (SSE comment) instead of closing.

        Long-running pipeline steps (relevance classification, final answer)
        can leave the queue silent for minutes. Closing the stream then breaks
        the user experience, so the generator emits an SSE comment and continues.
        """
        main_src = (BACKEND_DIR / "main.py").read_text()
        m = re.search(
            r"async def event_generator[\s\S]*?(?=\nasync def |\n@)",
            main_src,
        )
        body = m.group(0)
        # Grab the full TimeoutError branch — read forward until the next
        # top-level `if`/`elif` (next loop iteration boundary).
        timeout_branch = re.search(
            r"except\s+asyncio\.TimeoutError:[\s\S]*?\n[ \t]+if\b",
            body,
        )
        assert timeout_branch, "TimeoutError handler is missing"
        branch_text = timeout_branch.group(0)
        assert '"comment"' in branch_text or "'comment'" in branch_text, (
            "Timeout fallback must yield an SSE comment (keepalive) so the "
            "frontend EventSource does not see a hard close mid-pipeline."
        )
        assert 'continue' in branch_text, (
            "Timeout fallback must `continue` the loop — breaking closes the "
            "stream prematurely while the orchestrator is still working."
        )

    def test_sse_idle_timeout_does_not_yield_synthetic_final_output(self):
        """Timeout must NOT synthesize a final_output event.

        The old behavior of yielding `{final_output: '', error: 'sse_idle_timeout'}`
        caused the frontend to resolve `runGeneration` with empty data and crash.
        """
        main_src = (BACKEND_DIR / "main.py").read_text()
        m = re.search(
            r"async def event_generator[\s\S]*?(?=\nasync def |\n@)",
            main_src,
        )
        body = m.group(0)
        timeout_branch = re.search(
            r"except\s+asyncio\.TimeoutError:[\s\S]*?\n[ \t]+if\b",
            body,
        )
        assert timeout_branch, "TimeoutError handler is missing"
        branch = timeout_branch.group(0)
        assert '"sse_idle_timeout"' not in branch, (
            "Synthetic sse_idle_timeout event is no longer used — keepalive "
            "comments keep the stream alive without confusing the frontend."
        )
        assert '"final_output"' not in branch, (
            "Timeout must not synthesize a final_output event."
        )

    def test_sse_idle_timeout_clamped_to_one(self):
        """SSE_IDLE_TIMEOUT_SECONDS is clamped to >= 1."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        m = re.search(
            r"SSE_IDLE_TIMEOUT_SECONDS\s*=\s*max\(1,\s*(\w+)\)",
            main_src,
        )
        assert m, "SSE_IDLE_TIMEOUT_SECONDS must be clamped to >= 1"

    def test_no_telemetry_alias_in_main(self):
        """No telemetry_set_retrieval_mode alias."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        assert "telemetry_set_retrieval_mode" not in main_src

    def test_single_retrieval_lifecycle_scope(self):
        """Exactly one outer lifecycle_scope('Retrieval')."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        retrieval_scopes = re.findall(r'lifecycle_scope\(\s*"Retrieval"', main_src)
        assert len(retrieval_scopes) == 1, (
            f"Expected 1 'Retrieval' lifecycle_scope, found {len(retrieval_scopes)}"
        )

    def test_index_js_removed_route_stubs_throw(self):
        """Removed index.js functions are present as throwing stubs."""
        js = (REPO_ROOT / "customnerd-website" / "index.js").read_text()
        for stub_name in ("generate", "get_sim"):
            assert f"const {stub_name} = async" in js, f"{stub_name}() stub missing"
            match = re.search(rf"const {stub_name} = async[\s\S]*?\}};", js)
            assert match, f"{stub_name}() stub body not found"
            assert "throw new Error" in match.group(0), (
                f"{stub_name}() stub should throw"
            )

    def test_sse_idle_timeout_uses_pop_not_del(self):
        """Use dict.pop() in finally block — safer than del on missing keys."""
        main_src = (BACKEND_DIR / "main.py").read_text()
        m = re.search(
            r"async def event_generator[\s\S]*?(?=\nasync def |\n@)",
            main_src,
        )
        body = m.group(0)
        assert "pop(" in body, "event_generator should use queue.pop(..., None) in finally"


# ---------------------------------------------------------------------------
# Fix 5 & 6 — Documentation drift fixes
# ---------------------------------------------------------------------------

class TestDocsUpdated:
    def test_venv_drift_fixed_in_backend_readme(self):
        """Backend_README.md must reference nerd_engine_venv, not bare 'venv'."""
        text = (REPO_ROOT / "Documentation" / "Design" / "Backend_README.md").read_text()
        # The line `source venv/bin/activate` is the bad one. After fix it should be nerd_engine_venv.
        assert "source venv/bin/activate" not in text, (
            "Backend_README.md still says `source venv/bin/activate` — should be `nerd_engine_venv/bin/activate`"
        )
        assert "nerd_engine_venv/bin/activate" in text

    def test_venv_drift_fixed_in_installation_case_studies(self):
        text = (REPO_ROOT / "Documentation" / "INSTALLATION_CASE_STUDIES.md").read_text()
        assert "source venv/bin/activate" not in text
        assert "nerd_engine_venv/bin/activate" in text

    def test_venv_drift_fixed_in_detailed_documentation(self):
        text = (REPO_ROOT / "Documentation" / "DETAILED_PROJECT_DOCUMENTATION.md").read_text()
        # The project-structure tree line used to say `venv/`. Should now say `nerd_engine_venv/`.
        assert "├── venv/" not in text, (
            "DETAILED_PROJECT_DOCUMENTATION.md project tree still lists `venv/` — should be `nerd_engine_venv/`"
        )
        assert "nerd_engine_venv/" in text

    def test_pipeline_stage_count_drift_fixed(self):
        """All three docs must now mention the canonical 7 stages, not 9 or 10."""
        for fname, expected_old in [
            ("ARCHITECTURE_SUMMARY.md", "9-stage"),
            ("CASE_STUDIES_SUMMARY.md", "9-stage"),
            ("DETAILED_PROJECT_DOCUMENTATION.md", "10-stage"),
        ]:
            text = (REPO_ROOT / "Documentation" / fname).read_text()
            assert expected_old not in text, (
                f"{fname} still says `{expected_old} processing pipeline` — "
                f"should be the canonical 7 stages from LIFECYCLE_ORDER."
            )
            # Each must mention 7 somewhere
            assert re.search(r"\b7[\s-]+stage", text), (
                f"{fname} should mention a 7-stage pipeline"
            )


# ---------------------------------------------------------------------------
# Sanity — verify the canonical 7-stage lifecycle is unchanged
# ---------------------------------------------------------------------------

class TestLifecycleCanonical:
    def test_lifecycle_order_has_seven_stages(self):
        """The canonical LIFECYCLE_ORDER in benchmarking/telemetry.py must list 7 stages."""
        telemetry = (BACKEND_DIR / "benchmarking" / "telemetry.py").read_text()
        m = re.search(r"LIFECYCLE_ORDER\s*=\s*\[(.*?)\]", telemetry, re.DOTALL)
        assert m, "LIFECYCLE_ORDER not found in benchmarking/telemetry.py"
        stages = re.findall(r'"([^"]+)"', m.group(1))
        assert len(stages) == 7, f"Expected 7 stages, got {len(stages)}: {stages}"
        assert stages == [
            "Question Start",
            "Query Generation",
            "Query Cleaning",
            "Retrieval",
            "Reranking",
            "Final Answer",
            "Question End",
        ], f"LIFECYCLE_ORDER drifted: {stages}"


# ---------------------------------------------------------------------------
# Module-load smoke test
# ---------------------------------------------------------------------------

def test_main_module_loads():
    """Sanity check: main.py still imports cleanly after all edits."""
    # Re-import in case earlier tests cached a stale version
    if "main" in sys.modules:
        importlib.reload(sys.modules["main"])
    import main  # noqa: F401
    assert hasattr(main, "app")
    # Verify our new constant is exposed
    assert hasattr(main, "SSE_IDLE_TIMEOUT_SECONDS")


def test_importlib_added_to_main():
    """importlib must be imported in main.py (needed for the clean_query reload)."""
    main_src = (BACKEND_DIR / "main.py").read_text()
    assert re.search(r"^import importlib", main_src, re.MULTILINE), (
        "main.py is missing `import importlib` — /load_state's clean_query reload will fail"
    )