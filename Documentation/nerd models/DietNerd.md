## DietNerd

![DietNerd Logo](https://github.com/Harsh23Kashyap/customnerd/blob/main/customnerd-backend/saved_states/DietNerd/customnerd_logo.png)

DietNerd is the medical/nutrition research configuration of Custom‑Nerd. It focuses on PubMed as the primary source of peer‑reviewed literature and produces evidence‑based, citation‑rich answers that a lay reader can understand without compromising scientific rigor.

### What DietNerd Does
- Validates questions to exclude recipe creation and animal‑specific queries.
- Generates precise PubMed search strings using Boolean operators and synonyms.
- Collects PubMed articles (abstracts and metadata), with optional publisher integrations for full text when available.
- Classifies publication type (study vs review), extracts structured information from abstracts/reviews, and synthesizes a comprehensive answer.
- Emphasizes human evidence, includes risks/benefits/dosages (if reported), and outputs AMA‑style references.

### Architecture and Pipeline Specialization
DietNerd follows the common 9–10 stage pipeline, with medical‑specific prompts and PubMed‑centric collection:
1) Question Validation
   - Prompt: `DETERMINE_QUESTION_VALIDITY_PROMPT` filters out “False - Recipe” and “False - Animal”; otherwise “True`.
2) Query Generation
   - Prompt: `GENERAL_QUERY_PROMPT` outputs a single Boolean PubMed query string (no prose).
   - Optional: `QUERY_CONTENTION_PROMPT` can generate contention‑oriented queries per subtopic.
3) Article Collection (PubMed)
   - File: `user_search_apis.py`
   - Uses `Bio.Entrez.esearch` + `efetch` with relevance sort; deduplicates by PMID; returns up to 10 per query.
4) Relevance Classification
   - Prompt: `RELEVANCE_CLASSIFIER_PROMPT` returns yes/no; prioritizes human evidence and safety relevance; filters animal‑only abstracts.
5) Article Typing and Processing
   - Prompts: `ARTICLE_TYPE_PROMPT`, `STUDY_SUMMARY_PROMPT`, `REVIEW_SUMMARY_PROMPT`, `ABSTRACT_EXTRACTION_PROMPT` to extract structured fields (purpose, conclusions, risks, dosages, N, significance, CI, effect size, funding).
6) Final Synthesis
   - Prompt: `FINAL_RESPONSE_PROMPT` (medical variant) requires at least 8 and at most 20 articles (prefer more when strong evidence exists). Enforces human‑focused evidence and safety guidance. Outputs AMA‑style numbered references.

### Domain Prompts (Highlights)
- Validation strongly distinguishes recipe creation vs medical guidance vs animal questions.
- Study/Review extraction mandates numeric reporting when present (p‑values, CIs, effect sizes, N).
- Final synthesis includes explicit risk discussion and encourages consultation with a registered dietitian.

### Frontend Configuration (UI/UX)
File: `user_env.js`
- Theme: Medical blue (`BACKGROUND_COLOR: #EFF8FF`), `SITE_ICON: 🥗`, medical disclaimer text.
- Controls enabled: PDF upload (visible), PMID entry (visible), PubMed search (visible, defaultChecked = true), References section (visible).
- Endpoint: `API_URL: http://127.0.0.1:8000` (adjust per environment).

### Back‑of‑House Behavior (Backend Files)
- `user_search_apis.py`: Implements `collect_articles(query_list)`
  - Entrez email is set from `ENTREZ_EMAIL`.
  - `esearch` (relevance, retmax 10) → `efetch` → parse `PubmedArticle` → de‑duplicate by PMID.
  - Resilient calls via `exponential_backoff` from `helper_functions` (logging and retry on transient failures).
- `user_list_search.py`: `fetch_articles_by_pmids(pmid_list)` to directly fetch known PMIDs.
- `openai_prompts.py`: Contains all DietNerd‑specific prompt text (validation, query generation, classification, extraction, synthesis, disclaimers). The `FINAL_RESPONSE_PROMPT` enforces human evidence and deters harmful requests.

### Environment and Keys
File: `variables.env`
- Required: `OPENAI_API_KEY`, `NCBI_API_KEY`, `ENTREZ_EMAIL`.
- Optional (for full‑text, metadata, or coverage): `ELSEVIER_API_KEY`, `SPRINGER_API_KEY`, `WILEY_API_KEY`, `OXFORD_API_KEY`, `OXFORD_APP_HEADER`.
- Security: never commit real secrets; keep keys in local env only. Rotate keys periodically.

### Output Format and Quality Bar
- Output is a structured narrative followed by AMA‑style references `[1] ... [N]`.
- Bias toward human studies; animal‑only studies are filtered in relevance.
- Include numeric details when available (dosages, N, p‑values, CI, effect size, power).
- Always include safety considerations and urge professional consultation when appropriate.

### Rate Limits and Performance Notes
- PubMed (Entrez): 3 requests/sec with API key; DietNerd sleeps minimally and uses retries via `exponential_backoff`.
- If you see intermittent 429/HTTP errors, reduce concurrent queries or wait 60–120s.

### Example Queries and Behaviors
- “What are the benefits and risks of intermittent fasting?” → Validated (True), PubMed query generation, study/review extraction; emphasizes fasting risks (e.g., hypoglycemia) and subgroup differences, includes dosages/durations where reported.
- “Are probiotics effective for IBS?” → Collates RCTs and meta‑analyses; reports effect size ranges and confidence intervals when available.
- “Does vitamin D supplementation reduce fracture risk?” → Summarizes RCTs and reviews; includes dosage (IU/day), N, p‑values, and CI.

### Troubleshooting and Tips
- “No articles returned” → Check your PubMed query; try simplifying terms or re‑generate queries; confirm `ENTREZ_EMAIL`.
- “Animal‑only studies slip in” → Ensure relevance prompt is applied; increase filtering strictness in caller logic if needed.
- “Too few references” → Increase retmax in `user_search_apis.py`, or enable contention queries to broaden coverage.

### Saved State Snapshot Analogy (Why it’s Reliable)
Similar to PyTorch Autograd’s `SavedVariable` snapshot, the DietNerd saved state captures prompts, UI flags, search code, and env schema at a moment in time, enabling deterministic restores. This ensures reproducibility across sessions and machines: load the state, provide your keys, and behavior will match the snapshot.



