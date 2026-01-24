## CloudNerd

![CloudNerd Logo](https://github.com/Harsh23Kashyap/customnerd/blob/main/customnerd-backend/saved_states/CloudNerd/customnerd_logo.png)

CloudNerd is the cloud technology research configuration of Custom‑Nerd. It aggregates Stack Overflow discussions and technical solutions to provide comprehensive, evidence‑based answers for cloud computing questions across AWS, Azure, GCP, Kubernetes, and DevOps technologies.

### What CloudNerd Does
- Validates whether questions are cloud‑technology related (filters out general tech, personal, health, recipe, and animal questions).
- Generates 8‑12 expanded query variations in JSON format for comprehensive Stack Overflow searches.
- Aggregates Stack Overflow questions and answers, prioritizing accepted answers and high‑scored responses.
- Extracts technical details including code snippets, configurations, error messages, and performance metrics.
- Produces structured summaries with security considerations, cost implications, and best practices.

### Architecture and Pipeline Specialization
1) Question Validation
   - Prompt: `DETERMINE_QUESTION_VALIDITY_PROMPT` returns "True" for cloud topics (AWS, Azure, GCP, Kubernetes, DevOps, IaC, serverless, etc.), "False - General Tech/Personal/Health/Recipe/Animal/Other" for out‑of‑scope questions.
2) Query Generation (JSON Expansion)
   - Prompt: `GENERAL_QUERY_PROMPT` outputs JSON with 8‑12 query variations including exact rephrases, synonyms, provider‑specific terms, and service‑specific versions.
3) Article Collection (Stack Overflow API)
   - File: `user_search_apis.py`
   - Uses Stack Exchange API to search questions by relevance, then fetches top answers by votes.
   - Deduplicates by question_id, limits to 50 total answers.
   - HTML cleaning preserves code blocks while removing markup.
4) Relevance Classification
   - Prompt: `RELEVANCE_CLASSIFIER_PROMPT` returns yes/no for cloud‑relevant technical information or security concerns.
5) Article Typing and Processing
   - Prompts: `ARTICLE_TYPE_PROMPT` (question vs answer), `ABSTRACT_EXTRACTION_PROMPT` (technical details, solutions, risks, benefits, tools, configurations, performance metrics, security considerations).
6) Final Synthesis
   - Prompt: `FINAL_RESPONSE_PROMPT` requires 8‑20 posts, prioritizes accepted/high‑voted answers, emphasizes security warnings, and includes Stack Overflow citations.

### Domain Prompts (Highlights)
- Validation covers comprehensive cloud technology scope including platforms, services, IaC, containers, networking, security, and architecture.
- Query expansion generates provider‑specific variations (AWS EC2 instance types, Azure services, GCP products).
- Extraction focuses on technical implementation details, code snippets, configurations, error handling, and performance benchmarks.
- Final synthesis emphasizes security best practices and warns against dangerous misconfigurations.

### Frontend Configuration (UI/UX)
File: `user_env.js`
- Theme: Cloud‑neutral (`BACKGROUND_COLOR: #fafafa`), `SITE_ICON: ☁️`, comprehensive educational disclaimer.
- Controls: PDF upload (hidden), PMID search (hidden), Stack Exchange search (visible, defaultChecked = true), References visible, Query cleaning enabled.
- Search label: "Search using Stack Exchange Articles" with tooltip about Stack Overflow discussions.

### Back‑of‑House Behavior (Backend Files)
- `user_search_apis.py`: `collect_articles(query_list, answer_counter=50)`
  - Stack Exchange API integration with optional API key for higher rate limits.
  - Two‑stage process: search questions by relevance, then fetch top answers by votes.
  - HTML cleaning with BeautifulSoup preserves code blocks in markdown format.
  - Rate limiting with 1‑second delays between requests.
- `user_list_search.py`: Minimal PMID‑based lookup (retained for framework compatibility).
- `clean_query.py`: `clean_query(query_list)` parses JSON from query expansion and extracts expanded_queries array.
- `openai_prompts.py`: Cloud‑specific validation, JSON query expansion, technical extraction, and security‑focused synthesis prompts.

### Environment and Keys
File: `variables.env`
- Required: `OPENAI_API_KEY`.
- Optional: `STACK_API_KEY` for higher Stack Exchange API rate limits (10,000 requests/day vs 300 without key).
- Security: keep API keys local; do not commit secrets.

### Output Format and Quality Bar
- Structured technical summaries with problem context, proposed solutions, best practices, and security considerations.
- Includes code snippets, configuration details, performance metrics, and error handling guidance.
- Emphasizes security warnings and cost implications.
- References include Stack Overflow question/answer URLs with titles.

### Rate Limits and Performance Notes
- Stack Exchange API: 300 requests/day without key, 10,000 with key.
- Implementation includes 1‑second delays and error handling for 429 responses.
- HTML parsing adds processing overhead but preserves code readability.

### Example Queries and Behaviors
- "What is the best EC2 instance type for web applications?" → Expands to 12 variations including performance comparisons, cost analysis, and scaling considerations.
- "How to secure a Kubernetes cluster?" → Aggregates RBAC, network policies, encryption, and monitoring solutions with security warnings.
- "How to migrate from Azure SQL to AWS RDS?" → Collects migration strategies, tools, and best practices with cost/performance trade‑offs.

### Troubleshooting and Tips
- "No results returned" → Check query expansion; try broader cloud terms; verify Stack Exchange API access.
- "Rate limit exceeded" → Add Stack API key; increase delays; reduce query count.
- "Missing technical details" → Ensure answers include code snippets and configurations; filter for accepted answers.

### Saved State Snapshot Analogy
Like a `SavedVariable` snapshot, CloudNerd's saved state captures cloud‑specific prompts, Stack Overflow integration, and UI configuration for deterministic restoration across environments.

### Security and Compliance Focus
- Emphasizes security best practices and warns against dangerous configurations.
- Includes compliance considerations (IAM, encryption, RBAC, audit logs).
- Highlights cost implications and scaling limitations.
- Recommends consulting certified cloud professionals for production decisions.
