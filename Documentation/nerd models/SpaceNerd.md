## SpaceNerd

![SpaceNerd Logo](https://github.com/Harsh23Kashyap/customnerd/blob/main/customnerd-backend/saved_states/SpaceNerd/customnerd_logo.png)

SpaceNerd is the astronomy/space research configuration of Custom‑Nerd. It collects from arXiv, NASA Images, and optionally NASA ADS, and enriches with astronomy knowledge sources (Wikipedia, SIMBAD, VizieR, MPC) for broader context.

### What SpaceNerd Does
- Validates whether a question is space‑topic or space‑technology related.
- Generates keyword‑only queries (no quotes/Boolean) that work well across arXiv, open image APIs, and catalog services.
- Aggregates results from multiple sources and normalizes output (title, summary, URL, source name).
- Optionally queries NASA ADS (if token provided) to surface peer‑reviewed literature with citations/bibcodes.
- Produces technically clear yet accessible summaries; includes identifiers (arXiv IDs, ADS links) when relevant.

### Architecture and Pipeline Specialization
1) Question Validation
   - Prompt: `DETERMINE_QUESTION_VALIDITY_PROMPT` returns “False - Astronomy/Tech” for in‑domain questions, otherwise “True” (i.e., out‑of‑domain).
2) Query Generation (Keyword Only)
   - Prompt: `GENERAL_QUERY_PROMPT` emits short keyword lines (one per line) suitable for arXiv/NASA/Wikipedia; avoids brackets/Boolean.
3) Article/Asset Collection
   - File: `user_search_apis.py`
   - Wikipedia: search + extract intro text; links to canonical pages.
   - NASA Images: keyword search, returns titles, descriptions, and image links.
   - arXiv: API feed parsed via regex; returns title, summary, id link.
   - NASA ADS (optional): requires `ADS_API_TOKEN`; returns title/authors/bibcode and ADS abstract URLs.
   - SIMBAD/VizieR/MPC: basic lookups for objects, tables, and orbits to enrich results.
   - Output is trimmed to `article_counter` with rate‑limit aware sleeps.
4) Relevance/Extraction/Synthesis
   - Prompts for classification and structured extraction adapted to space context (study vs review; technical metrics, risks, benefits).
   - Final response emphasizes clarity for non‑experts while preserving technical precision.

### Frontend Configuration (UI/UX)
File: `user_env.js`
- Theme: Space neutral, custom icon; disclaimer visible.
- Controls: Query Cleaning toggle visible (enabled), References visible.
- Search label: “Search using NASA, Wikipedia and other Articles.”

### Query Cleaning for Astronomy
File: `clean_query.py`
- Function `refine_prompts(query_list)` flattens nested inputs, trims whitespace, removes duplicates, and standardizes spacing.
- Useful when LLM generates multi‑line keyword lists or when user supplies heterogeneous inputs.

### Environment and Keys
File: `variables.env`
- Required: `OPENAI_API_KEY`.
- Optional: `ADS_API_TOKEN` for NASA ADS enrichment.
- Security: keep tokens local; do not commit secrets.

### Output Format and Quality Bar
- Summaries include technical context (mission/instrument names, observation modalities) but avoid jargon.
- Provide IDs/links: arXiv identifiers, ADS bibcodes/links, NASA images URLs.
- Call out uncertainty and active debates; prefer peer‑reviewed sources when ADS is enabled.

### Rate Limits and Performance Notes
- Public endpoints may throttle; the implementation prints diagnostic messages and sleeps briefly.
- arXiv prefers simple keyword searches; avoid complex Boolean and quotes.

### Example Queries and Behaviors
- “Current constraints on dark matter self‑interaction?” → arXiv/ADS literature with cross‑paper synthesis; highlights ranges and caveats.
- “JWST capabilities for exoplanet spectra” → NASA Images/Wikipedia context; arXiv reviews and instrument papers; links included.
- “Voyager 1 current status” → NASA sources and Wikipedia; relevant ADS entries if token provided.

### Saved State Snapshot Analogy
As with a `SavedVariable` snapshot, SpaceNerd’s saved state freezes prompts, UI toggles, and multi‑source collectors to ensure reproducible retrieval behavior across sessions.



