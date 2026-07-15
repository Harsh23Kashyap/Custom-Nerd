import json
import re


def clean_query(query_list, max_queries=None):
    """
    Turn query_generation output into a flat list of search strings.

    Accepts either:
    - A JSON string (or markdown-wrapped JSON) with ``expanded_queries`` in ``query_list[0]``
    - A nested list of plain query strings

    Optional ``max_queries`` limits how many strings are returned (order preserved).
    """
    if not query_list:
        return []

    queries = _parse_expanded_queries(query_list)
    if not queries:
        queries = _flatten_query_list(query_list)

    if max_queries is not None and max_queries > 0:
        return queries[:max_queries]
    return queries


def _strip_markdown_code_fence(text: str) -> str:
    s = (text or "").strip()
    if not s.startswith("```"):
        return s
    lines = s.split("\n")
    if not lines:
        return s
    lines = lines[1:]
    while lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_expanded_queries_loose(text: str) -> list:
    if not text:
        return []
    m = re.search(
        r'["\']expanded_queries["\']\s*:\s*\[(.*?)\]\s*(?:,|\})',
        text,
        re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return []
    inner = m.group(1)
    out = []
    for match in re.finditer(r'"((?:\\.|[^"\\])*)"', inner):
        raw = match.group(1)
        try:
            out.append(json.loads(f'"{raw}"'))
        except Exception:
            out.append(raw.replace("\\n", " ").strip())
    return [q for q in out if q and str(q).strip()]


def _parse_expanded_queries(query_list) -> list:
    raw = query_list[0]
    if not isinstance(raw, str):
        raw = str(raw)

    stripped = _strip_markdown_code_fence(raw)

    for candidate in (stripped, raw.strip()):
        if not candidate:
            continue
        try:
            data = json.loads(candidate)
            out = [q.strip() for q in data.get("expanded_queries", []) if q and str(q).strip()]
            if out:
                return out
        except Exception:
            pass

    try:
        import json5

        data = json5.loads(stripped)
        if isinstance(data, dict):
            out = [q.strip() for q in data.get("expanded_queries", []) if q and str(q).strip()]
            if out:
                return out
    except Exception:
        pass

    loose = _extract_expanded_queries_loose(stripped) or _extract_expanded_queries_loose(raw)
    return loose or []


def _flatten_query_list(query_list) -> list:
    def flatten(item):
        if isinstance(item, list):
            out = []
            for sub in item:
                out.extend(flatten(sub))
            return out
        text = str(item) if not isinstance(item, str) else item
        return [line.strip() for line in text.split("\n") if line.strip()]

    cleaned = []
    for element in query_list:
        cleaned.extend(flatten(element))

    seen = set()
    unique = []
    for item in cleaned:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
