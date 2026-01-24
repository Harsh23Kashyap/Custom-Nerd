## NewsNerd

![NewsNerd Logo](https://github.com/Harsh23Kashyap/customnerd/blob/main/customnerd-backend/saved_states/NewsNerd/customnerd_logo.png)

NewsNerd is the current‑events configuration of Custom‑Nerd. It aggregates multiple reputable news APIs to provide concise, research‑backed digests with links to sources, prioritizing recency and deduplication.

### What NewsNerd Does
- Validates whether a user’s question is news‑appropriate (filters trivial, purely opinion, or non‑research needs).
- Generates short, Boolean‑lite queries appropriate for news APIs (synonyms via OR, core concepts via AND; avoids quotes where APIs penalize exact phrases).
- Aggregates results from GNews, NewsAPI, and The Guardian Open Platform; deduplicates by title; limits output to the requested count.
- Produces a balanced, linked summary with emphasis on factual reporting and cross‑source corroboration when possible.

### Architecture and Pipeline Specialization
1) Question Validation
   - Prompt: `DETERMINE_QUESTION_VALIDITY_PROMPT` (news variant) returns True only for research‑backed news topics.
2) Query Generation
   - Prompt: `GENERAL_QUERY_PROMPT` outputs minimal‑keyword, API‑friendly search expressions.
3) Article Collection (Multi‑Source)
   - File: `user_search_apis.py`
   - GNews: REST search with `q`, `lang=en`, `sortby=publishedAt`, `max` and token.
   - NewsAPI: `get_everything` with `language=en`, `sort_by=publishedAt`, `page_size`.
   - Guardian: content API with `show-fields`, `page-size`, `order-by=newest`.
   - Dedup Strategy: track seen titles across sources to avoid repeats.
   - Rate‑Limit Handling: brief sleeps; HTTP error handling (401 invalid key, 429 throttling) with diagnostic prints.
4) Relevance Filtering and Synthesis
   - Light LLM relevance filtering optional; final synthesis outlines key developments, differences across sources, and provides links.

### Frontend Configuration (UI/UX)
File: `user_env.js`
- Theme: Neutral gray background.
- Controls: PDF upload (hidden), PMID/ID search (hidden), News search (visible, defaultChecked = true).
- References: visible or simplified depending on presentation; source links shown inline.

### Back‑of‑House Behavior (Backend Files)
- `user_search_apis.py`: `collect_articles(query_list, article_counter=30)` integrates the three providers with consistent output shape: title, description, url, publishedAt, source.
- `user_list_search.py`: Minimal ID‑based lookup (news rarely uses stable IDs akin to PMIDs; function retained for framework compatibility).
- `openai_prompts.py`: News validation and query prompts tuned for minimal keywords and boolean operators compatible with target APIs.

### Environment and Keys
File: `variables.env` (in NewsNerd saved state)
- Required: `OPENAI_API_KEY`, `NEWS_API_KEY` (for NewsAPI), `GNEWS_API_KEY`, `GUARDIAN_API_KEY`.
- Security: never commit real keys; rotate keys; respect provider ToS.

### Output Format and Quality Bar
- Short, factual summaries with links; highlight corroboration across multiple outlets when relevant.
- Prioritize timeliness and reduce redundancy (dedup titles, filter wire duplicates).
- Avoid pure opinion summaries unless the question explicitly asks for media coverage analysis (then describe spectrum of positions with sources).

### Rate Limits and Performance Notes
- Add short sleeps between provider calls; handle 401/429 explicitly.
- Some plans restrict historical depth and page size; account for pagination if needed.

### Example Queries and Behaviors
- “How have oil prices reacted to recent Middle East tensions?” → collects recency‑sorted coverage; summarizes price movement context and cites sources.
- “Key takeaways from the latest G7 summit?” → aggregates communiqués coverage; lists primary policy themes with links.
- “How is AI regulation evolving in the EU this year?” → synthesizes legislative milestones and major proposals with outlet references.

### Troubleshooting and Tips
- “Empty results” → adjust keywords; try synonyms; remove stopwords; confirm API plan limits.
- “HTTP 401/429” → verify keys; reduce frequency; add waits; check daily quotas.
- “Duplicate articles” → ensure dedup by title remains active; consider dedup by URL hostname + normalized title.

### Saved State Snapshot Analogy
Like a `SavedVariable` snapshot, NewsNerd’s saved state pins prompts, UI toggles, and provider settings so the aggregation behavior can be restored deterministically across environments.



