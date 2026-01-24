## SciNer

![SciNer Logo](https://github.com/Harsh23Kashyap/customnerd/blob/main/customnerd-backend/saved_states/SciNer/customnerd_logo.png)

SciNer is the QASPER‑based scientific paper QA configuration of Custom‑Nerd. It consumes papers, questions, and evidence annotations in the QASPER style and synthesizes strictly evidence‑grounded answers with structured formatting and AMA citations.

### QASPER Basis (Core Principles)
- Use only provided papers and evidence passages; do not hallucinate external facts.
- Favor more papers (min 8, up to 20) when strong evidence exists; synthesize across them.
- Explain technical concepts in plain language while preserving quantitative details.
- If a question is unanswerable from the provided evidence, state this explicitly.

### Architecture and Pipeline Specialization
1) Question Validation (QASPER Scope)
   - Prompt: `DETERMINE_QUESTION_VALIDITY_PROMPT` (SciNer) returns True only for questions answerable from provided PDFs/annotations; returns “False - Not Supported/Out of Scope” otherwise.
2) Query Formation (Internal Scoping)
   - Prompt: `GENERAL_QUERY_PROMPT` (SciNer) shapes internal sub‑questions aligned to QASPER’s annotated structure rather than external API queries.
3) Evidence Gathering
   - Primary path: provided PDFs and annotations (QASPER). The template includes PubMed‑style files for compatibility, but SciNer is optimized for local evidence ingestion.
4) Relevance/Typing/Extraction
   - Prompts: relevance yes/no; `ARTICLE_TYPE_PROMPT` (“new research” vs “review” for ML literature); structured extraction prompts tuned for ML/NLP papers (model, dataset, metrics, results, significance, effect sizes, funding/conflicts).
5) Final Synthesis
   - Prompt: `FINAL_RESPONSE_PROMPT` (SciNer) requires multi‑paper synthesis, balanced strengths/limitations, demographic/context notes where applicable, and AMA‑style references.

### Frontend Configuration (UI/UX)
File: `user_env.js`
- Theme: Academic; `SITE_ICON: 🧠`; disclaimer clarifies educational research scope.
- Controls: PDF upload visible; PubMed/news toggles off; references visible.
- Placeholder encourages ML‑oriented questions.

### Back‑of‑House Behavior (Backend Files)
- `openai_prompts.py`: QASPER‑aligned prompts; strict formatting and paper count requirements; unanswerable handling; clear risk/safety messaging for harmful queries.
- `user_search_apis.py` and `user_list_search.py`: Retained for framework uniformity; main path is PDF/evidence ingestion.
- `clean_query.py`: Utility function `refine_prompts(query_list)` to normalize text inputs and support multi‑line sub‑questions.

### Environment and Keys
- Required: `OPENAI_API_KEY`.
- Optional: none strictly required beyond local evidence.

### Output Format and Quality Bar
- Summary of evidence followed by AMA‑style references [1]…[N].
- Include metrics wherever possible: accuracy/F1/AUROC/BLEU, statistical tests, CIs, effect sizes, power, dataset sizes, and training data composition when relevant.
- When evidence conflicts, describe divergence and potential causes (dataset shift, methodology differences, hyperparameter choices).

### Example Questions and Behaviors
- “Does transfer learning improve performance in low‑resource NLP tasks?” → Synthesizes across fine‑tuning and adapter studies; quantifies average gains; flags domains with limited improvements.
- “What evaluation metrics dominate recent QA architectures?” → Tallies metric prevalence; highlights standard benchmarks and shifts over time.
- “Is model X superior to model Y on dataset Z?” → Compares head‑to‑head results with statistical significance if reported; calls out training/data differences.

### Troubleshooting and Tips
- “Unanswerable” → Ensure the provided papers actually contain the needed evidence; otherwise SciNer correctly returns insufficiency.
- “Too few papers used” → Provide more papers or reduce the strictness of inclusion; SciNer aims for 8–20.
- “Missing metrics” → Some papers lack detailed statistics; SciNer reports what is present and notes omissions.

### Saved State Snapshot Analogy
Like a `SavedVariable` snapshot, SciNer’s state captures QASPER‑specific prompts, UI flags, and ingestion behavior to ensure repeatable, evaluation‑grade runs across machines.



