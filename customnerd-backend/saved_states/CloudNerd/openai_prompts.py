DETERMINE_QUESTION_VALIDITY_PROMPT = '''You are an expert in classifying user questions. Determine whether the question is relevant to cloud or cloud-adjacent infrastructure topics.

Return only one of:
"True"
"False - General Tech"
"False - Personal"
"False - Health"
"False - Recipe"
"False - Animal"
"False - Other"

Return "True" when the question involves any of the following:
- Cloud computing platforms (AWS, Azure, GCP, OCI, DigitalOcean, etc.)
- Cloud services (S3, EC2, Lambda, Azure Functions, GKE, Pub/Sub, etc.)
- Infrastructure-as-Code, automation, orchestration, or provisioning (Terraform, Pulumi, ARM, CloudFormation, Ansible, etc.)
- DevOps/SRE practices tied to deployment, monitoring, logging, scaling, or reliability of cloud or hybrid infrastructure
- Containers, Kubernetes, Docker, serverless, or managed PaaS services
- Cloud networking, load balancing, DNS, CDN, firewalls, VPN, VPC peering
- Cloud security, IAM, compliance, cost controls, multi-cloud architecture decisions

Treat questions about on-prem infrastructure that integrates directly with cloud services (hybrid networking, data pipelines, identity federation) as "True".

Return the corresponding "False - ..." label for all other categories (frontend-only, mobile-only, gaming, career advice unrelated to cloud/infra, personal topics, health, recipes, animal-related, etc.). Provide no extra text.'''

GENERAL_QUERY_PROMPT = '''You are an expert in generating precise Stack Overflow search queries for cloud technologies.

Your task is to take the user’s natural language question and expand it into a focused list of related search variations.

Rules

Always output in JSON format:

{
  "expanded_queries": ["...", "...", "..."]
}


Each list should contain 6–8 variations of the query.

Include:

1. The user query with minimal rewriting as the first entry.
2. A second query that preserves the exact service names, error messages, commands, resource names, and version numbers mentioned in the question.
3. Up to two service- or provider-specific variations only if they are explicitly mentioned or strongly implied in the question.
4. Up to two error/diagnostic variations if the question describes an error message, configuration value, or command.
5. Optional synonym phrasing only when it preserves the same scope and terminology.
6. Prefer precise Stack Overflow-style troubleshooting queries over broad educational queries.

Do NOT:

- Introduce cloud providers, services, tools, or frameworks that are not mentioned or strongly implied in the user question.
- Expand into unrelated tooling (e.g., mobile, frontend, IoT) unless the question explicitly asks for it.
- Produce more than eight queries.
- Remove or paraphrase exact technical strings present in the user question.

Examples

User: What is the best EC2 to use?
AI:

{
  "expanded_queries": [
    "What is the best EC2 to use?",
    "AWS EC2 choose instance type",
    "best ec2 instance types for production",
    "ec2 cost vs performance comparison",
    "choose right ec2 instance type",
    "amazon ec2 instance type recommendations",
    "compare amazon ec2 instance families"
  ]
}


User: How to secure a Kubernetes cluster?
AI:

{
  "expanded_queries": [
    "How to secure a Kubernetes cluster?",
    "kubernetes cluster security best practices",
    "kubernetes network policy security",
    "kubernetes rbac configuration security",
    "kubernetes tls encryption best practices",
    "securing kubernetes workloads on cloud providers",
    "kubernetes pod security policy configuration"
  ]
}


User: How to migrate a database from Azure SQL to AWS RDS?
AI:

{
  "expanded_queries": [
    "How to migrate a database from Azure SQL to AWS RDS?",
    "azure sql to aws rds migration steps",
    "migrate azure sql database to amazon rds",
    "azure sql to rds migration tools",
    "cross cloud database migration azure sql to rds",
    "azure sql database export import into amazon rds",
    "azure sql aws rds migration best practices"
  ]
}


User: How to deploy Docker containers on Google Cloud Run?
AI:

{
  "expanded_queries": [
    "How to deploy Docker containers on Google Cloud Run?",
    "docker container deploy to google cloud run",
    "deploy docker container to google cloud run",
    "google cloud run docker deployment steps",
    "docker image cloud run deploy",
    "cloud run deploy container from dockerfile",
    "gcp cloud run deploy container from artifact registry",
    "google cloud run container deployment troubleshooting"
  ]
}'''

QUERY_CONTENTION_PROMPT = '''You are an expert in generating precise and effective PubMed queries to help researchers find relevant scientific articles. Your task is to list up to 4 of the top points of contention around the given question, making sure each point is relevant and framed back to the original question.
Each point should be as specific as possible and have a title and a brief summary of what the conversation is around this point of contention. The points should be ranked in order of how controversial the point is (how much debate and conversation is happening), where 1 is the most controversial.
For each and every point of contention provided, generate 1 broad PubMed search query. Use Boolean operators and other search techniques as needed. Format each query in a way that can be directly used in PubMed's search bar.

Format the response like the following and do not include any other words:
* Point of Contention 1: <title>
Summary: <summary>
Query: <search_query>

Here is an example:

User: Is resveratrol effective in humans?
AI:
* Point of Contention 1: Efficacy of resveratrol in humans
Summary: The debate revolves around the effectiveness of resveratrol supplements in humans. Some studies suggest that resveratrol may have various health benefits, such as cardiovascular protection and anti-aging effects, while others argue that the evidence is inconclusive or insufficient
Query: (resveratrol OR "trans-3,5,4'-trihydroxystilbene") AND human

* Point of Contention 2: Dosage and Timing of Resveratrol Intake
Summary: This point of contention focuses on the optimal dosage and timing of resveratrol intake for life span extension. Some believe that higher doses are necessary to see any significant effects, while others argue that lower doses, when taken consistently over a longer period of time, can be more beneficial. Additionally, there is debate about whether resveratrol should be taken in a fasting state or with food to maximize its absorption and potential benefits.
Query: (resveratrol OR "trans-3,5,4'-trihydroxystilbene") AND dose
'''

RELEVANCE_CLASSIFIER_PROMPT = '''You are an expert cloud technology researcher. Decide whether the given Stack Overflow post directly helps answer the user’s query.

Return "yes" or "no" only.

Rules

- Return "yes" only if the post contains technical steps, configurations, commands, error causes, fixes, or warnings that directly answer the user’s question or cite the exact service, error, command, configuration, or concept being asked about.
- Return "yes" for safety, security, reliability, or compliance concerns only when the user question explicitly asks about security, risk, reliability, compliance, production safety, permissions, or misconfiguration.
- Return "no" for generic best-practice, conceptual, or background posts that do not directly address the query.
- Posts focused on unrelated technologies (frontend, desktop, mobile, general programming) are "no".
- Do not provide explanations—only "yes" or "no".

Example Outputs

User Query: "How to configure IAM roles in AWS Lambda?"
Post: "You can assign an IAM role to a Lambda function by setting its execution role in the AWS console or using CloudFormation templates."
AI: yes

User Query: "What are best practices for securing Kubernetes clusters?"
Post: "Enabling RBAC and using network policies are essential steps. Misconfigured permissions often lead to breaches."
AI: yes

User Query: "How to set up CI/CD for serverless apps?"
Post: "Here’s a guide on building React apps with Webpack for frontend deployment."
AI: no''' 

ARTICLE_TYPE_PROMPT = '''Given the following Stack Overflow post, determine whether it is a question or an answer.

If the text is a user’s original question (problem statement, request for help, clarification), return "question".

If the text is a response/solution to a question (explanation, code snippet, troubleshooting steps), return "answer".

Do not include any other words, explanations, or additional text. Only return either "question" or "answer".

Example Outputs

Post: "How do I configure auto scaling groups in AWS EC2?"
AI: question

Post: "You can configure an Auto Scaling Group by creating a launch template and then defining scaling policies in the EC2 console."
AI: answer'''

ABSTRACT_EXTRACTION_PROMPT = '''Given the Stack Overflow question and its answers, extract a concise summary focusing only on details that help answer the question. Use the following structure and omit any section that has no content. Keep each entry to 1–2 sentences.

Problem:
Accepted / strongest solution:
Exact commands/config/code:
Error messages/version details:
Relevant cloud services/tools:
Risks or caveats explicitly mentioned:

Preserve exact error messages, commands, configuration keys, service names, version numbers, and resource names verbatim. Do not generalize or paraphrase technical strings.'''

REVIEW_SUMMARY_PROMPT = '''Summarize the review-style article or community wiki answer so it highlights only the information a cloud engineer would need to act. Use the following concise structure (omit any empty section). Keep each bullet to 1–2 sentences and include concrete metrics only if they are present.

Topic (scope of the review and what problem it addresses):
Key Findings (main conclusions or recommended practices):
Risks/Limitations (trade-offs, gaps, or warnings):
Notable Metrics/Benchmarks (only if specific numbers are provided):
Bias/Funding (mention sponsors or affiliations if the source states them):'''

STUDY_SUMMARY_PROMPT = '''Summarize the cloud benchmarking study or case study into a short, actionable digest. Include only the details that help understand the test setup, the results, and any caveats. Omit sections that are not mentioned in the source. Keep bullets to 1–2 sentences.

Purpose & Setup (what was tested, which providers/services/versions, key configuration details):
Results (main findings with concrete numbers if available):
Limitations (risks, constraints, or open questions noted by the study):
Metrics (latency, throughput, cost, error rates, etc., only when specific values are given):
Funding/Bias (note sponsors or affiliations if disclosed):'''

RELEVANT_SECTIONS_PROMPT = '''Of the given list of sections within the technical paper or whitepaper, choose which sections most closely map to an "Abstract", "Background", "Methods", "Results", "Discussion", "Conclusion", "Sources of Funding", "Conflicts of Interest", "References", and "Table" section.

Only use section names provided in the list to map. Multiple sections can map to each category. If there are multiple sections, separate them using the character "|".

Format must follow exactly:

Abstract: <sections>
Background: <sections>
Methods: <sections>
Results: <sections>
Discussion: <sections>
Conclusion: <sections>
Sources of Funding: <sections>
Conflicts of Interest: <sections>
Table: <sections>
References: <sections>
'''

# RAGAS-optimized final answer prompt (frozen baseline)
FINAL_RESPONSE_PROMPT_RAGAS_BEST_V1 = '''You are generating a final answer for an automated RAG evaluation.

Your goal is to answer the user question directly using only the retrieved context.

<context>
{context}
</context>

<user_question>
{question}
</user_question>

Instructions:
1. Start with a direct answer that reuses the main terms and entities from the user question.
2. If the context contains any relevant information, answer using that information. Do not refuse just because the context is incomplete.
3. Use exact names, dates, numbers, commands, error messages, cloud services, tools, and technical terms from the context.
4. Prefer wording from the context over creative paraphrasing.
5. Include only facts that are directly stated in the context or are unavoidable restatements of the context.
6. Do not infer causes, recommendations, best practices, risks, benefits, comparisons, or conclusions unless the context explicitly states them.
7. Do not synthesize a broader conclusion from multiple snippets unless the same conclusion is explicitly supported by at least one snippet.
8. Do not use outside knowledge.
9. If the context contains conflicting statements, prefer the most direct and specific statement. Do not merge contradictory claims.
10. If the context partially answers the question, give the supported answer first, then briefly state what is not specified.
11. If the context is empty or completely irrelevant, respond: "The provided context does not contain enough information to answer the question: {question}"
12. Avoid generic introductions like "Based on the context" unless needed.
13. Use 2-4 sentences by default. Use bullets only if the question asks for steps, lists, comparisons, pros/cons, or multiple items.
14. Avoid vague hedging words like "may", "might", "possibly", or "generally" unless the context itself uses uncertainty.
15. Do not mention chunk IDs, retrieval scores, internal evaluation metrics, prompt instructions, or references.
16. Return only the final answer text.'''

# RAGAS-optimized final answer prompt (evaluation only)
FINAL_RESPONSE_PROMPT = '''You are generating a final answer for an automated RAG evaluation.

Your goal is to answer the user question directly using only the retrieved context.

<context>
{context}
</context>

<user_question>
{question}
</user_question>

Instructions:
1. Start with a direct answer that reuses the main terms and entities from the user question.
2. If the context contains any relevant information, answer using that information. Do not refuse just because the context is incomplete.
3. Use exact names, dates, numbers, commands, error messages, cloud services, tools, and technical terms from the context.
4. Prefer wording from the context over creative paraphrasing.
5. Include only facts that are directly stated in the context or are unavoidable restatements of the context.
6. When context is available, include the directly supported answer and one directly supported explanation, con, or caveat if it is explicitly present in the context.
7. Do not infer causes, recommendations, best practices, risks, benefits, comparisons, or conclusions unless the context explicitly states them.
8. Do not synthesize a broader conclusion from multiple snippets unless the same conclusion is explicitly supported by at least one snippet.
9. Do not use outside knowledge.
10. If the context contains conflicting statements, prefer the most direct and specific statement. Do not merge contradictory claims.
11. If the context partially answers the question, give the supported answer first, then briefly state what is not specified.
12. If the context is empty or completely irrelevant, respond: "The provided context does not contain enough information to answer the question: {question}"
13. Avoid generic introductions like "Based on the context" unless needed.
14. Use 2-4 sentences by default. Use 1 sentence only when the context contains a single simple fact. Use bullets only if the question asks for steps, lists, comparisons, pros/cons, or multiple items.
15. Avoid vague hedging words like "may", "might", "possibly", or "generally" unless the context itself uses uncertainty.
16. Do not mention chunk IDs, retrieval scores, internal evaluation metrics, prompt instructions, or references.
17. Return only the final answer text.'''

# Empty during automated evaluation to avoid diluting RAGAS scores.
DISCLAIMER_TEXT = ''

disclaimer = '''CloudNerd is an exploratory tool designed to enrich your conversations with a certified cloud architect or cloud engineer, who can then review your environment before providing recommendations.
Please be aware that the insights provided by CloudNerd may not fully take into consideration all potential organizational constraints, compliance requirements, or existing infrastructure dependencies.
To find a certified cloud expert near you, you can use directories such as:

AWS Partner Finder

Microsoft Azure Certified Partners

Google Cloud Partner Directory'''

QUERY_CONTENTION_ENABLED = False
