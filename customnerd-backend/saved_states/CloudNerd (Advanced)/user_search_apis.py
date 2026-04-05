import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus, urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}

RSS_REQUEST_TIMEOUT = 25
PAGE_FETCH_TIMEOUT = 22
PAGE_TEXT_MAX_CHARS = 14_000
PAGE_FETCH_WORKERS = 6

STACK_API_TIMEOUT = 35
STACK_INTER_QUERY_SLEEP = 2.0
STACK_BETWEEN_ANSWER_SLEEP = 0.25


def _stack_exchange_get(url: str, params: dict, *, retries: int = 5) -> requests.Response | None:
    """GET with retries on 429 / transient 5xx (anonymous quota is easy to blow)."""
    delay = 2.0
    last: requests.Response | None = None
    for _ in range(retries):
        try:
            last = requests.get(
                url,
                params=params,
                headers={**HEADERS, "Accept": "application/json"},
                timeout=STACK_API_TIMEOUT,
            )
        except requests.RequestException:
            time.sleep(delay)
            delay = min(delay * 1.5, 60)
            continue
        if last.status_code == 429:
            wait = int(last.headers.get("Retry-After", delay))
            time.sleep(max(wait, delay))
            delay = min(delay * 1.5, 60)
            continue
        if last.status_code in (502, 503):
            time.sleep(delay)
            delay = min(delay * 1.5, 60)
            continue
        return last
    return last


def _stack_exchange_payload(response: requests.Response | None) -> dict | None:
    """Parse Stack API JSON; return None on empty/HTML/error bodies (avoids json.decoder noise)."""
    if response is None:
        return None
    text = (response.text or "").strip()
    if not text:
        return None
    try:
        data = response.json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def _stack_apply_backoff(data: dict | None) -> None:
    if not data or "backoff" not in data:
        return
    try:
        time.sleep(float(data["backoff"]))
    except (TypeError, ValueError):
        time.sleep(2.0)


# ---------------------------------------------------------------------------
# RSS / cloud search (AWS, Azure, CloudFest)
# ---------------------------------------------------------------------------

QUERY_EXPANSIONS = {
    "kubernetes": ("kubernetes", "k8s", "kubelet", "kubectl", "helm", "cncf", "prometheus"),
    "k8s": ("kubernetes", "k8s"),
    "docker": ("docker", "container", "oci"),
    "containers": ("container", "containers", "kubernetes", "k8s", "docker"),
    "serverless": ("serverless", "lambda", "functions", "faas"),
    "lambda": ("lambda", "serverless"),
    "terraform": ("terraform", "iac", "infrastructure as code"),
    "security": ("security", "zero trust", "encryption", "compliance"),
}

STOPWORDS = frozenset(
    {"a", "an", "the", "and", "or", "of", "in", "to", "for", "on", "with", "is", "are"}
)

AWS_RESOURCE_PAGES = {
    "lambda": ("lambda/resources/",),
    "serverless": ("lambda/resources/",),
    "faas": ("lambda/resources/",),
    "ecs": ("ecs/resources/",),
    "fargate": ("ecs/resources/",),
    "containers": ("ecs/resources/",),
    "docker": ("ecs/resources/",),
    "kubernetes": ("ecs/resources/",),
    "k8s": ("ecs/resources/",),
    "eks": ("ecs/resources/",),
}


def _aws_blog_article_url(href: str) -> str | None:
    base = "https://aws.amazon.com"
    full = urljoin(base + "/", href)
    full = full.split("#")[0].split("?")[0].rstrip("/")
    if not full.startswith(f"{base}/blogs/"):
        return None
    rest = full[len(f"{base}/blogs/") :].strip("/")
    parts = [p for p in rest.split("/") if p]
    if len(parts) < 2:
        return None
    return f"{base}/blogs/{parts[0]}/{parts[1]}"


def _needles_for_token(token: str) -> tuple[str, ...] | None:
    t = token.lower().strip()
    if not t or t in STOPWORDS:
        return None
    return QUERY_EXPANSIONS.get(t, (t,))


def _content_matches(text_lower: str, query: str | None) -> bool:
    if not query or not query.strip():
        return True
    tokens = [x for x in re.split(r"\s+", query.strip().lower()) if x]
    groups = []
    for tok in tokens:
        needles = _needles_for_token(tok)
        if needles is None:
            continue
        groups.append(needles)
    if not groups:
        return True
    return all(any(n in text_lower for n in needles) for needles in groups)


def _entry_text(entry) -> str:
    parts: list[str] = []
    for key in ("title", "summary", "description"):
        v = entry.get(key)
        if isinstance(v, str) and v.strip():
            parts.append(v)
    for block in entry.get("content") or []:
        if isinstance(block, dict):
            val = block.get("value")
            if isinstance(val, str) and val.strip():
                parts.append(val)
    for tag in entry.get("tags") or []:
        if isinstance(tag, dict):
            term = tag.get("term")
            if isinstance(term, str) and term.strip():
                parts.append(term)
    return " ".join(parts)


def fetch_rss(
    feed_url,
    query=None,
    limit=10,
    max_scan=200,
    include_recent_when_empty=False,
):
    try:
        resp = requests.get(feed_url, headers=HEADERS, timeout=RSS_REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return {"results": [], "used_recent_fallback": False}

    feed = feedparser.parse(resp.content)
    entries = list(feed.entries)[:max_scan]

    matches: list[tuple[str, str]] = []
    for entry in entries:
        blob = _entry_text(entry).lower()
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if not link:
            continue
        if _content_matches(blob, query):
            matches.append((title, link))
            if len(matches) >= limit:
                break

    if matches or not (query and query.strip() and include_recent_when_empty):
        return {"results": matches, "used_recent_fallback": False}

    recent: list[tuple[str, str]] = []
    for entry in entries:
        title = (entry.get("title") or "").strip()
        link = (entry.get("link") or "").strip()
        if link:
            recent.append((title, link))
        if len(recent) >= limit:
            break
    return {"results": recent, "used_recent_fallback": bool(recent)}


def _aws_site_search_url(query: str) -> str:
    return f"https://aws.amazon.com/search/?searchQuery={quote_plus(query.strip())}"


def _aws_resource_paths_for_query(query: str | None) -> list[str]:
    if not query or not query.strip():
        return []
    tokens = [t for t in re.split(r"\s+", query.strip().lower()) if t]
    paths: list[str] = []
    seen_paths: set[str] = set()
    for tok in tokens:
        if tok in STOPWORDS:
            continue
        for needle in _needles_for_token(tok) or ():
            key = needle.lower()
            if key in AWS_RESOURCE_PAGES:
                for p in AWS_RESOURCE_PAGES[key]:
                    if p not in seen_paths:
                        seen_paths.add(p)
                        paths.append(p)
    return paths


def fetch_aws_resource_blog_links(resource_path: str, limit: int = 30) -> list[tuple[str, str]]:
    url = urljoin("https://aws.amazon.com/", resource_path.lstrip("/"))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=RSS_REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = _aws_blog_article_url(a["href"])
        if not href:
            continue
        if href in seen:
            continue
        seen.add(href)
        title = " ".join(a.get_text(separator=" ", strip=True).split())
        if not title or title.lower() == "blogs":
            title = href.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        out.append((title, href))
        if len(out) >= limit:
            break
    return out


def search_aws_rss(query, **kwargs):
    limit = kwargs.get("limit", 10)
    rss_payload = fetch_rss(
        "https://aws.amazon.com/blogs/aws/feed/", query, **kwargs
    )

    merged: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    def add(title: str, link: str) -> None:
        link = (link or "").strip()
        if not link or link in seen_urls:
            return
        seen_urls.add(link)
        merged.append((title.strip(), link))

    q = (query or "").strip()
    if q:
        add(f'AWS site search (blogs, docs, pages): "{q}"', _aws_site_search_url(q))

    for path in _aws_resource_paths_for_query(q):
        prefix = path.rstrip("/").replace("/", " ").title()
        for title, link in fetch_aws_resource_blog_links(path, limit=25):
            add(f"[{prefix}] {title}", link)

    for title, link in rss_payload["results"]:
        add(title, link)
        if len(merged) >= limit:
            break

    merged = merged[:limit]
    return {
        "results": merged,
        "used_recent_fallback": rss_payload["used_recent_fallback"],
    }


def _azure_blog_search_url(query: str) -> str:
    return f"https://azure.microsoft.com/en-us/blog/search/?s={quote_plus(query.strip())}"


def _azure_blog_article_from_href(href: str) -> str | None:
    full = urljoin("https://azure.microsoft.com/", href)
    full = full.split("#")[0].split("?")[0].rstrip("/") + "/"
    if not full.startswith("https://azure.microsoft.com/en-us/blog/"):
        return None
    parts = [p for p in urlparse(full).path.strip("/").split("/") if p]
    if len(parts) != 3:
        return None
    if parts[0] != "en-us" or parts[1] != "blog":
        return None
    slug = parts[2]
    if slug in ("search", "feed", "wp-content", "page") or slug.startswith("wp-"):
        return None
    return f"https://azure.microsoft.com/en-us/blog/{slug}/"


def fetch_azure_blog_search_links(query: str, limit: int = 15) -> list[tuple[str, str]]:
    query = (query or "").strip()
    if not query:
        return []
    url = _azure_blog_search_url(query)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=RSS_REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        canon = _azure_blog_article_from_href(a["href"])
        if not canon or canon in seen:
            continue
        title = " ".join(a.get_text(separator=" ", strip=True).split())
        if len(title) < 12:
            title = canon.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        seen.add(canon)
        out.append((title, canon))
        if len(out) >= limit:
            break
    return out


def search_azure_rss(query, **kwargs):
    limit = kwargs.get("limit", 10)
    rss_payload = fetch_rss(
        "https://azure.microsoft.com/en-us/blog/feed/", query, **kwargs
    )

    merged: list[tuple[str, str]] = []
    seen_urls: set[str] = set()

    def add(title: str, link: str) -> None:
        link = (link or "").strip()
        if not link or link in seen_urls:
            return
        seen_urls.add(link)
        merged.append((title.strip(), link))

    q = (query or "").strip()
    if q:
        add(f'Azure blog search (browser): "{q}"', _azure_blog_search_url(q))
        html_cap = max(0, min(8, limit - 1))
        for title, link in fetch_azure_blog_search_links(q, limit=html_cap):
            add(f"[Azure search] {title}", link)

    for title, link in rss_payload["results"]:
        add(title, link)
        if len(merged) >= limit:
            break

    merged = merged[:limit]
    return {
        "results": merged,
        "used_recent_fallback": rss_payload["used_recent_fallback"],
    }


def search_cloudfest_rss(query, **kwargs):
    return fetch_rss("https://www.cloudfest.com/feed/", query, **kwargs)


def search_all_rss(query, **kwargs):
    spec = [
        ("aws", search_aws_rss),
        ("azure", search_azure_rss),
        ("cloudfest", search_cloudfest_rss),
    ]
    out: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(fn, query, **kwargs): name for name, fn in spec}
        for fut in as_completed(futs):
            out[futs[fut]] = fut.result()
    return {name: out[name] for name, _ in spec}


# ---------------------------------------------------------------------------
# Stack Overflow + page fetch for cloud URLs
# ---------------------------------------------------------------------------

_AWS_SEARCH_SKIP = re.compile(
    r"^https?://aws\.amazon\.com/search/?\?", re.IGNORECASE
)
_AZURE_BLOG_SEARCH_SKIP = re.compile(
    r"^https?://azure\.microsoft\.com/en-us/blog/search/?\?", re.IGNORECASE
)


def clean_html(html_text):
    """Strip HTML tags but keep code blocks readable."""
    soup = BeautifulSoup(html_text, "html.parser")
    for code in soup.find_all("code"):
        code.replace_with(f"\n```\n{code.get_text()}\n```\n")
    return soup.get_text("\n").strip()


def _should_fetch_page_body(url: str) -> bool:
    if not url or not url.startswith("http"):
        return False
    if _AWS_SEARCH_SKIP.search(url) or _AZURE_BLOG_SEARCH_SKIP.search(url):
        return False
    return True


def fetch_page_plain_text(url: str) -> str:
    """GET one level: main article-ish body as plain text (truncated)."""
    if not _should_fetch_page_body(url):
        return ""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=PAGE_FETCH_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(resp.content, "html.parser")
    for tag in soup.find_all(["script", "style", "noscript", "template"]):
        tag.decompose()

    root = (
        soup.find("article")
        or soup.find("main")
        or soup.find(attrs={"role": "main"})
        or soup.body
        or soup
    )
    text = root.get_text("\n", strip=True)
    lines = [ln for ln in text.split("\n") if ln.strip()]
    blob = "\n".join(lines)
    if len(blob) > PAGE_TEXT_MAX_CHARS:
        blob = blob[:PAGE_TEXT_MAX_CHARS] + "\n…"
    return blob


def _cloud_news_records_for_query(
    query: str,
    links_per_source: int = 10,
    fetch_pages: bool = True,
) -> list[dict]:
    """AWS + Azure + CloudFest via search_all_rss; optional per-URL body fetch."""
    print(f"[user_search_apis] Cloud RSS — query={query!r} (links_per_source={links_per_source})")
    payload = search_all_rss(
        query,
        limit=links_per_source,
        include_recent_when_empty=True,
    )

    rows: list[tuple[str, str, str, bool]] = []
    seen: set[str] = set()
    for source, block in payload.items():
        used_fb = bool(block.get("used_recent_fallback"))
        raw_links = block.get("results") or []
        print(
            f"  source={source}: rss_links={len(raw_links)}, "
            f"used_recent_fallback={used_fb}"
        )
        for title, link in raw_links:
            link = (link or "").strip()
            if not link or link in seen:
                continue
            seen.add(link)
            rows.append((source, title, link, used_fb))

    if not rows:
        print("  (no cloud links after dedupe)")
        return []

    print(
        f"  → {len(rows)} unique URLs to fetch "
        f"(workers={PAGE_FETCH_WORKERS}, timeout={PAGE_FETCH_TIMEOUT}s)"
    )

    def worker(item: tuple[str, str, str, bool]) -> dict:
        source, title, link, used_fb = item
        body = fetch_page_plain_text(link) if fetch_pages else ""
        if not fetch_pages:
            action = "no-fetch"
        elif not _should_fetch_page_body(link):
            action = "skip-GET (search/listing hub)"
        else:
            action = "GET"
        if not body:
            body = f"(No in-page excerpt fetched; open URL for full content.)\n{title}\n{link}"
        preview = (title[:72] + "…") if len(title) > 72 else title
        print(
            f"    [{action}] {source}: {preview}\n"
            f"      url={link}\n"
            f"      answer_body_chars={len(body)} rss_fallback={used_fb}"
        )
        return {
            "question_title": f"[{source}] {title}",
            "question_url": link,
            "answer_body": body,
            "answer_url": link,
            "answer_id": None,
            "is_accepted": False,
            "score": 0,
            "cloud_news_source": source,
            "rss_recent_fallback": used_fb,
        }

    if not fetch_pages:
        print("  fetch_pages=False — using titles/URLs only")
        return [worker(r) for r in rows]

    order = {"aws": 0, "azure": 1, "cloudfest": 2}
    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=PAGE_FETCH_WORKERS) as pool:
        futs = {pool.submit(worker, r): r for r in rows}
        for fut in as_completed(futs):
            try:
                out.append(fut.result())
            except Exception as e:
                r = futs[fut]
                print(f"[Cloud news] Error processing {r[2]}: {e}")
    out.sort(key=lambda d: (order.get(d.get("cloud_news_source", ""), 99), d.get("question_title", "")))
    print(f"  → cloud records built: {len(out)}")
    return out


def collect_articles(
    query_list,
    answer_counter=50,
    cloud_links_per_source=10,
):
    """
    Stack Exchange (Stack Overflow) answers, then AWS / Azure / CloudFest hits from
    ``search_all_rss``. Each news URL is fetched once; visible text is stored in
    ``answer_body`` so downstream steps match the Stack Overflow record shape.

    Returns up to ``answer_counter`` Stack items plus up to ``min(30, max(6, answer_counter//2))``
    unique cloud URLs (with bodies), in that order.
    """
    print(
        "[user_search_apis] collect_articles start — "
        f"queries={len([q for q in query_list if str(q).strip()])}, "
        f"answer_counter={answer_counter}, cloud_links_per_source={cloud_links_per_source}"
    )

    stack_api_key = os.getenv("STACK_API_KEY")
    search_url = "https://api.stackexchange.com/2.3/search/advanced"
    answers_url = "https://api.stackexchange.com/2.3/questions/{ids}/answers"

    collected: list[dict] = []
    seen_questions: set[int] = set()

    for query in query_list:
        query = str(query).strip()
        if not query:
            continue

        try:
            print(f"[user_search_apis] Stack Exchange API — query={query!r}")
            params = {
                "order": "desc",
                "sort": "relevance",
                "q": query,
                "site": "stackoverflow",
                "pagesize": 10,
            }
            if stack_api_key:
                params["key"] = stack_api_key

            response = _stack_exchange_get(search_url, params)
            data = _stack_exchange_payload(response)
            if data is None and response is not None and response.status_code == 200:
                time.sleep(5)
                response = _stack_exchange_get(search_url, params)
                data = _stack_exchange_payload(response)
            if data is None:
                st = response.status_code if response is not None else "?"
                print(
                    f"[Search] Error for query {query!r}: empty or non-JSON response "
                    f"(status={st}; often 429 without JSON body)"
                )
                time.sleep(STACK_INTER_QUERY_SLEEP)
                continue
            if data.get("error_id") is not None:
                print(
                    f"[Search] Stack API error for query {query!r}: "
                    f"{data.get('error_message', data)}"
                )
                time.sleep(STACK_INTER_QUERY_SLEEP)
                continue
            _stack_apply_backoff(data)
            questions = data.get("items", [])
            print(f"  → questions returned: {len(questions)}")

            answers_this_query = 0
            for q in questions:
                qid = q.get("question_id")
                if qid in seen_questions:
                    continue
                seen_questions.add(qid)

                ans_params = {
                    "order": "desc",
                    "sort": "votes",
                    "site": "stackoverflow",
                    "filter": "withbody",
                    "pagesize": 5,
                }
                if stack_api_key:
                    ans_params["key"] = stack_api_key

                ans_response = _stack_exchange_get(
                    answers_url.format(ids=qid), ans_params
                )
                if ans_response is None:
                    print(f"[Answers] No response for QID {qid}; skipping")
                    continue
                if ans_response.status_code in (400, 404):
                    print(
                        f"[Answers] Skipping QID {qid}: HTTP {ans_response.status_code} "
                        "(invalid, deleted, or migrated question)"
                    )
                    continue
                if ans_response.status_code != 200:
                    print(
                        f"[Answers] Error fetching answers for QID {qid}: "
                        f"HTTP {ans_response.status_code}"
                    )
                    time.sleep(STACK_BETWEEN_ANSWER_SLEEP)
                    continue

                ans_data = _stack_exchange_payload(ans_response)
                if ans_data is None:
                    print(
                        f"[Answers] Non-JSON or empty body for QID {qid} "
                        f"(status={ans_response.status_code})"
                    )
                    time.sleep(STACK_BETWEEN_ANSWER_SLEEP)
                    continue
                if ans_data.get("error_id") is not None:
                    print(
                        f"[Answers] Stack API error for QID {qid}: "
                        f"{ans_data.get('error_message', ans_data)}"
                    )
                    time.sleep(STACK_BETWEEN_ANSWER_SLEEP)
                    continue
                _stack_apply_backoff(ans_data)
                answers = ans_data.get("items", [])

                for ans in answers:
                    collected.append(
                        {
                            "question_title": q.get("title"),
                            "question_url": q.get("link"),
                            "answer_id": ans.get("answer_id"),
                            "is_accepted": ans.get("is_accepted", False),
                            "score": ans.get("score", 0),
                            "answer_body": clean_html(ans.get("body", "")),
                            "answer_url": f"https://stackoverflow.com/a/{ans.get('answer_id')}",
                        }
                    )
                    answers_this_query += 1
                    ab = collected[-1]["answer_body"]
                    print(
                        f"    [stackoverflow] QID={qid} answer_id={ans.get('answer_id')} "
                        f"score={ans.get('score')} accepted={ans.get('is_accepted')} "
                        f"answer_body_chars={len(ab)}"
                    )

                time.sleep(STACK_BETWEEN_ANSWER_SLEEP)

            print(f"  → answers appended this query: {answers_this_query}")
            time.sleep(STACK_INTER_QUERY_SLEEP)

        except Exception as e:
            print(f"[Search] Error for query '{query}': {str(e)}")

    stack_slice = collected[:answer_counter]
    print(
        f"[user_search_apis] Stack Overflow slice: {len(stack_slice)} "
        f"(raw collected {len(collected)}, cap answer_counter={answer_counter})"
    )

    cloud: list[dict] = []
    seen_cloud_urls: set[str] = set()
    for query in query_list:
        query = str(query).strip()
        if not query:
            continue
        for rec in _cloud_news_records_for_query(
            query, links_per_source=cloud_links_per_source, fetch_pages=True
        ):
            u = rec.get("question_url") or ""
            if u in seen_cloud_urls:
                continue
            seen_cloud_urls.add(u)
            cloud.append(rec)

    cloud_cap = min(30, max(6, answer_counter // 2))
    cloud_before_cap = len(cloud)
    cloud = cloud[:cloud_cap]
    print(
        f"[user_search_apis] Cloud news merged (deduped): {cloud_before_cap} → "
        f"after cap ({cloud_cap}): {len(cloud)}"
    )

    total = len(stack_slice) + len(cloud)
    print(
        f"[user_search_apis] collect_articles done — stack={len(stack_slice)}, "
        f"cloud={len(cloud)}, total={total}"
    )

    return stack_slice + cloud
