from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Optional

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import os
env = 'variables.env'
load_dotenv(env)

from generic_prompts import *

# Question to Query
import pandas as pd
import random
import time
import math
import numpy as np

import logging

# Database
import ast
import mysql.connector
from mysql.connector import Error
from scipy import spatial # for calculating vector similarities for search
import json
import itertools
import fitz
import re
import subprocess 
import html
import io
import urllib.error
import urllib.request

# Information Retrieval
from Bio import Entrez
from Bio.Entrez import efetch, esearch
from metapub import PubMedFetcher
import re
import requests
from bs4 import BeautifulSoup
from openai_prompts import *

# Token Clean-Up
import tiktoken
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Summarizer
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
import string
from tenacity import retry # Exponential Backoff
# wait_random_exponential stop_after_attempt

# Output Synthesis
import textwrap
MAX_RETRIES = 3            # network / rate-limit retries
BACKOFF_SECS = 2           # exponential back-off base

# Import LLM execution modules
from openai_executions import (
    determine_question_validity_openai, query_generation_openai, get_article_type_openai,
    generate_content_from_pdf_openai, section_match_openai, generate_final_response_openai,
    generate_code_from_content_openai, generate_prompt_from_content_openai, _retryable_openai_call
)
from gemini_executions import (
    determine_question_validity_gemini, query_generation_gemini, get_article_type_gemini,
    generate_content_from_pdf_gemini, section_match_gemini, generate_final_response_gemini,
    generate_code_from_content_gemini, generate_prompt_from_content_gemini, _retryable_gemini_call
)
from claude_executions import (
    determine_question_validity_claude, query_generation_claude, get_article_type_claude,
    generate_content_from_pdf_claude, section_match_claude, generate_final_response_claude,
    generate_code_from_content_claude, generate_prompt_from_content_claude, _retryable_claude_call
)
from ollama_executions import (
    determine_question_validity_ollama, query_generation_ollama, get_article_type_ollama,
    generate_content_from_pdf_ollama, section_match_ollama, generate_final_response_ollama,
    generate_code_from_content_ollama, generate_prompt_from_content_ollama, _retryable_ollama_call
)
from benchmarking.telemetry import lifecycle_scope, set_request_context

def get_llm_client():
    from dotenv import load_dotenv
    load_dotenv('variables.env', override=True)
    
    llm_preference = os.getenv('LLM', 'OpenAI').strip('"').strip()
    
    if llm_preference.lower() == 'gemini':
        return 'gemini'
    if llm_preference.lower() == 'claude':
        return 'claude'
    if llm_preference.lower() == 'ollama':
        return 'ollama'
    return 'openai'

"""# Step1. Evaluate Question Validity
We do not answer questions related to meal-planning or recipe creation.
* This filter will return `FALSE` if it is not a valid question, in other words, it is a meal-planning/recipe creation question.
* This filter will return `TRUE` if it is a valid question that we will answer.
"""

def determine_question_validity(query):
    """
    Determines if the user's question is one that we can answer.

    Parameters:
    - query (str): The user's question.

    Returns:
    - question_validity (str): "True", "False - Recipe", or "False - Animal".
    """
    llm_client = get_llm_client()
    
    if llm_client == 'openai':
        return determine_question_validity_openai(query, DETERMINE_QUESTION_VALIDITY_PROMPT)
    if llm_client == 'claude':
        return determine_question_validity_claude(query, DETERMINE_QUESTION_VALIDITY_PROMPT)
    if llm_client == 'ollama':
        return determine_question_validity_ollama(query, DETERMINE_QUESTION_VALIDITY_PROMPT)
    return determine_question_validity_gemini(query, DETERMINE_QUESTION_VALIDITY_PROMPT)


"""# If Valid Question

## Step2. Query Generation
"""


def query_generation(
    query,
    general_query_prompt_override=None,
    query_contention_enabled_override=None,
):
    """
    Generates a total of 5 PubMed queries that are aggregated together into a list:
    - 1 query built directly from the user's question that is meant to retrieve articles that provide general context
    - 4 queries to represent the top points of contention around the topic and retrieve articles that may provide more clarity

    Parameters:
    - query (str): The user's question.
    - general_query_prompt_override (str, optional): Override system prompt for general query (cascade P4).
    - query_contention_enabled_override (bool, optional): Force contention on/off (cascade uses False).

    Returns:
    - general_query (str): The broad query that will retrieve articles related to a specific topic.
    - query_contention (str): A list of 4 queries to represent the top points of contention around the topic.
    - query_list (list): A list of all 5 queries generated.
    """
    llm_client = get_llm_client()

    from openai_prompts import QUERY_CONTENTION_ENABLED

    g_prompt = general_query_prompt_override or GENERAL_QUERY_PROMPT
    contention_enabled = (
        QUERY_CONTENTION_ENABLED
        if query_contention_enabled_override is None
        else query_contention_enabled_override
    )

    if llm_client == 'openai':
        general_query, query_contention = query_generation_openai(query, g_prompt, QUERY_CONTENTION_PROMPT, contention_enabled)
    elif llm_client == 'claude':
        general_query, query_contention = query_generation_claude(query, g_prompt, QUERY_CONTENTION_PROMPT, contention_enabled)
    elif llm_client == 'ollama':
        general_query, query_contention = query_generation_ollama(query, g_prompt, QUERY_CONTENTION_PROMPT, contention_enabled)
    else:
        general_query, query_contention = query_generation_gemini(query, g_prompt, QUERY_CONTENTION_PROMPT, contention_enabled)

    if contention_enabled:
        #### AGGREGATE ALL 5 QUERIES
        pattern = r"Query: (.*)"
        matches = re.findall(pattern, query_contention)
        query_list = matches + [general_query]
    else:
        # Skip contention queries when disabled
        query_contention = "Query contention disabled"
        query_list = [general_query]

    return general_query, query_contention, query_list


"""## Step3. Information Retrieval"""

def exponential_backoff(func, *args, **kwargs):
        retries = 5
        wait = 1 

        for i in range(retries):
            try:
                result = func(*args, **kwargs)
                if result:
                    return result
            except Exception as e:
                print(f"Attempt {i+1} failed: {str(e)}")
                time.sleep(wait)
                wait *= 2 ** i + (random.uniform(0, 1) * 0.1) 
        return None

# _retryable_openai_call moved to openai_executions.py

# --------------------------------------------------------------------------- #
# 1. helper
# --------------------------------------------------------------------------- #
def _flatten_authors(raw) -> str:
    """
    Accepts str · list[str] · list[dict] · dict  → returns a comma-separated
    author string or "".
    """
    if not raw:
        return ""

    # single string
    if isinstance(raw, str):
        return raw.strip()

    # single dict  ➜ wrap in list and recurse
    if isinstance(raw, dict):
        return _flatten_authors([raw])

    # list case
    if isinstance(raw, list):
        names = []
        for item in raw:
            if isinstance(item, str):
                names.append(item.strip())
            elif isinstance(item, dict):
                # grab the first plausible name-ish key
                for key in ("name", "full_name", "fullname", "author", "given", "family"):
                    if item.get(key):
                        names.append(str(item[key]).strip())
                        break
            else:
                # fallback – stringify whatever it is
                names.append(str(item).strip())
        return ", ".join([n for n in names if n])   # strip empties

    # anything else – stringify
    return str(raw).strip()


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    """
    Attempts to parse a JSON string that may be wrapped in ``` fences,
    contain trailing commas, or be otherwise slightly malformed.
    Returns {} on failure.
    """
    if not raw:
        return {}

    # remove markdown fences and language hints
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw, flags=re.IGNORECASE).strip()

    # remove common trailing commas (very permissive)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logging.warning("[safe_json_loads] JSON decode failed; returning empty dict.")
        return {}


def _coerce_to_str(val: Any, default: str = "") -> str:
    """Return `val` as str if truthy, else default."""
    return str(val).strip() if val else default


def _ensure_fields(d: Dict[str, Any], reference: Dict[str, Any]) -> Dict[str, Any]:
    """Guarantees all keys from `reference` exist in d, filling missing with blank / None."""
    return {k: d.get(k, v) for k, v in reference.items()}


# ---------- 2. canonical defaults -------------------------------------------- #


DEFAULT_ARTICLE: Dict[str, Any] = {
    "title": "",
    "publication_type": "",
    "url": "",
    "abstract": "",
    "citations": "",
    "author_name": "",
    "summary": "",
    "is_relevant": True,
    "id": "",
    "doi": "",
    "date": "",
    "journal": "",
}

# --------------------------------------------------------------------------- #
# 3.  Low-level helpers                                                       #
# --------------------------------------------------------------------------- #
# _retryable_openai_call moved to openai_executions.py


def _safe_json_loads(raw: str) -> Dict[str, Any]:
    """Parse possibly-malformed JSON; return {} on failure."""
    if not raw:
        return {}
    cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw, flags=re.I).strip()
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)  # rm trailing commas
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logging.warning("[safe_json_loads] JSON decode failed.")
        return {}


def _coerce_to_str(val: Any, default: str = "") -> str:
    """Return a stripped string or default."""
    return str(val).strip() if val else default


def _ensure_fields(d: Dict[str, Any],
                   reference: Dict[str, Any]) -> Dict[str, Any]:
    """Guarantee all keys from reference exist in d."""
    return {k: d.get(k, v) for k, v in reference.items()}


def _flatten_authors(raw: Any) -> str:
    if not raw:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, dict):
        return _flatten_authors([raw])
    if isinstance(raw, list):
        names = []
        for item in raw:
            if isinstance(item, str):
                names.append(item.strip())
            elif isinstance(item, dict):
                for key in ("name", "full_name", "fullname",
                            "author", "given", "family"):
                    if item.get(key):
                        names.append(str(item[key]).strip())
                        break
            else:
                names.append(str(item).strip())
        return ", ".join(filter(None, names))
    return str(raw).strip()

# --------------------------------------------------------------------------- #
# 4.  Main orchestrator                                                       #
# --------------------------------------------------------------------------- #
def organize_database_articles(article: Any, user_query: str) -> Dict[str, Any]:
    """
    Extract & normalise metadata from an arbitrary article payload while never
    crashing.  Returns the full DEFAULT_ARTICLE schema with all non-bool fields
    stringified.
    """
    # 4.1  stringify the incoming payload ------------------------------------ #
    try:
        article_str = json.dumps(article, indent=2) if isinstance(article, dict) else str(article)
    except Exception:
        article_str = str(article) if article else ""
    if not article_str:
        logging.error("[organize] Empty article payload.")
        return DEFAULT_ARTICLE.copy()

    # 4.2  initial metadata extraction via LLM ------------------------------- #
    extraction_prompt = (
        "You are a strict JSON extractor for scientific records.\n"
        'Return ONLY a JSON object with keys: title, authors, abstract, journal, '
        'id, doi, url, date. Leave unknown fields null.'
    )
    llm_client = get_llm_client()
    if llm_client == 'openai':
        extraction_raw = _retryable_openai_call(
            messages=[
                {"role": "system", "content": extraction_prompt},
                {"role": "user",   "content": article_str},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
    elif llm_client == 'claude':
        extraction_raw = _retryable_claude_call(
            system=extraction_prompt,
            user=f"Article: {article_str}",
            temperature=0.1,
        )
    elif llm_client == 'ollama':
        extraction_raw = _retryable_ollama_call(
            messages=[
                {"role": "system", "content": extraction_prompt},
                {"role": "user",   "content": article_str},
            ],
            temperature=0.1,
        )
    else:
        extraction_raw = _retryable_gemini_call(
            prompt=f"{extraction_prompt}\n\nArticle: {article_str}",
            temperature=0.1
        )
    meta = _safe_json_loads(extraction_raw)

    # 4.3  populate base record --------------------------------------------- #
    article_data = DEFAULT_ARTICLE.copy()
    article_data.update({
        "title":       _coerce_to_str(meta.get("title")),
        "author_name": _flatten_authors(meta.get("authors")),
        "abstract":    _coerce_to_str(meta.get("abstract")),
        "journal":     _coerce_to_str(meta.get("journal")),
        "id":          _coerce_to_str(meta.get("id")),
        "doi":         _coerce_to_str(meta.get("doi")),
        "url":         _coerce_to_str(meta.get("url")),
        "date":        _coerce_to_str(meta.get("date")),
    })

    # 4.4  classify publication type ---------------------------------------- #
    pub_type_prompt = (
        "Classify the text as either 'review' or 'study'. "
        "Respond with exactly one lowercase word: review / study."
    )
    if llm_client == 'openai':
        pub_type_raw = _retryable_openai_call(
            messages=[
                {"role": "system", "content": pub_type_prompt},
                {"role": "user",   "content": article_str},
            ],
            temperature=0.0,
        ).strip().lower()
    elif llm_client == 'claude':
        pub_type_raw = _retryable_claude_call(
            system=pub_type_prompt,
            user=f"Article: {article_str}",
            temperature=0.0,
        ).strip().lower()
    elif llm_client == 'ollama':
        pub_type_raw = _retryable_ollama_call(
            messages=[
                {"role": "system", "content": pub_type_prompt},
                {"role": "user",   "content": article_str},
            ],
            temperature=0.0,
        ).strip().lower()
    else:
        pub_type_raw = _retryable_gemini_call(
            prompt=f"{pub_type_prompt}\n\nArticle: {article_str}",
            temperature=0.0
        ).strip().lower()
    if pub_type_raw in {"review", "study"}:
        article_data["publication_type"] = pub_type_raw

    # 4.5  ensure abstract exists ------------------------------------------- #
    if len(article_data["abstract"]) < 40:
        abstract_prompt = (
            "Extract the abstract from the text. If absent, generate a concise "
            "abstract (≤150 words) covering objectives, methods, results, conclusion."
        )
        if llm_client == 'openai':
            article_data["abstract"] = _retryable_openai_call(
                messages=[
                    {"role": "system", "content": abstract_prompt},
                    {"role": "user",   "content": article_str},
                ],
                temperature=0.4,
            )[:4000]
        elif llm_client == 'claude':
            article_data["abstract"] = _retryable_claude_call(
                system=abstract_prompt,
                user=f"Article: {article_str}",
                temperature=0.4,
            )[:4000]
        elif llm_client == 'ollama':
            article_data["abstract"] = _retryable_ollama_call(
                messages=[
                    {"role": "system", "content": abstract_prompt},
                    {"role": "user",   "content": article_str},
                ],
                temperature=0.4,
            )[:4000]
        else:
            article_data["abstract"] = _retryable_gemini_call(
                prompt=f"{abstract_prompt}\n\nArticle: {article_str}",
                temperature=0.4
            )[:4000]

    # 4.6  user-tailored summary -------------------------------------------- #
    summary_prompt = (
        "Provide a 3-5 sentence summary tailored to the user query below. "
        "Emphasise study design & findings if this is a study, or themes if review.\n\n"
        f"User query: {user_query}"
    )
    if llm_client == 'openai':
        article_data["summary"] = _retryable_openai_call(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user",   "content": article_data['abstract']},
            ],
            temperature=0.5,
        )
    elif llm_client == 'claude':
        article_data["summary"] = _retryable_claude_call(
            system=summary_prompt,
            user=f"Abstract: {article_data['abstract']}",
            temperature=0.5,
        )
    elif llm_client == 'ollama':
        article_data["summary"] = _retryable_ollama_call(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user",   "content": article_data['abstract']},
            ],
            temperature=0.5,
        )
    else:
        article_data["summary"] = _retryable_gemini_call(
            prompt=f"{summary_prompt}\n\nAbstract: {article_data['abstract']}",
            temperature=0.5
        )

    # 4.7  fallback title / author extraction -------------------------------- #
    if not article_data["title"]:
        title_prompt = "Generate a concise, descriptive title for the article."
        if llm_client == 'openai':
            article_data["title"] = _retryable_openai_call(
                messages=[
                    {"role": "system", "content": title_prompt},
                    {"role": "user",   "content": article_str[:2000]},
                ],
                temperature=0.6,
            )[:300]
        elif llm_client == 'claude':
            article_data["title"] = _retryable_claude_call(
                system=title_prompt,
                user=f"Article: {article_str[:2000]}",
                temperature=0.6,
            )[:300]
        elif llm_client == 'ollama':
            article_data["title"] = _retryable_ollama_call(
                messages=[
                    {"role": "system", "content": title_prompt},
                    {"role": "user",   "content": article_str[:2000]},
                ],
                temperature=0.6,
            )[:300]
        else:
            article_data["title"] = _retryable_gemini_call(
                prompt=f"{title_prompt}\n\nArticle: {article_str[:2000]}",
                temperature=0.6
            )[:300]

    if not article_data["author_name"]:
        author_prompt = (
            "Extract author names from the text. If none discovered, return ''."
        )
        if llm_client == 'openai':
            article_data["author_name"] = _retryable_openai_call(
                messages=[
                    {"role": "system", "content": author_prompt},
                    {"role": "user",   "content": article_str},
                ],
                temperature=0.2,
            )[:500]
        elif llm_client == 'claude':
            article_data["author_name"] = _retryable_claude_call(
                system=author_prompt,
                user=f"Article: {article_str}",
                temperature=0.2,
            )[:500]
        elif llm_client == 'ollama':
            article_data["author_name"] = _retryable_ollama_call(
                messages=[
                    {"role": "system", "content": author_prompt},
                    {"role": "user",   "content": article_str},
                ],
                temperature=0.2,
            )[:500]
        else:
            article_data["author_name"] = _retryable_gemini_call(
                prompt=f"{author_prompt}\n\nArticle: {article_str}",
                temperature=0.2
            )[:500]

    # 4.8  final sanitation – **string-ify everything** ---------------------- #
    article_data = _ensure_fields(article_data, DEFAULT_ARTICLE)
    for k, v in article_data.items():
        if k != "is_relevant":                 # keep the bool as-is
            article_data[k] = _coerce_to_str(v)

    return article_data

#@title concurrent_organize_database_articles
def concurrent_organize_database_articles(articles, user_query, request_id: Optional[str] = None):
    """
    Concurrently processes and classifies articles using multiple threads for improved performance.
    Uses ThreadPoolExecutor to parallelize the classification of articles into relevant and irrelevant categories.

    Parameters:
    - articles (list): List of article dictionaries to be classified
    - user_query (str): The user's search query used for relevance classification

    Returns:
    - all_articles (list): List of organized article dictionaries
    """
    all_articles = []

    def _organize_worker(article):
        if request_id:
            set_request_context(request_id)
        return organize_database_articles(article, user_query)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_organize_worker, article) for article in articles]
        for future in as_completed(futures):
            try:
                article = future.result()
                all_articles.append(article)
            except Exception as e:
                print(f"Error processing article: {str(e)}")

    return all_articles

# Step 3.5: Process Reference Articles
def process_articles_by_url(articles):
    ref_articles = []
    for article in articles:
        if article['url'] is None:
            ref_articles.append(article)
        else:
            new_summary = url_to_summary(article['url'])
            new_summary = generate_summary(new_summary)
            ref_article = {
                'title': article.get('title', ''),
                'publication_type': article.get('publication_type', ''),
                'url': article.get('url', ''),
                'abstract': article.get('abstract', ''),
                'citations': article.get('citations', ''),
                'author_name': article.get('author_name', ''),
                'summary': new_summary,
                'is_relevant': article.get('is_relevant', ''),
                'id': article.get('id', ''),
                'doi': article.get('doi', ''),
                'date': article.get('date', ''),
                'journal': article.get('journal', ''),
            }
            ref_articles.append(ref_article)
    return ref_articles

def url_to_summary(url: str):
    result = subprocess.run(
        f'curl -sL "{url}" | lynx -stdin -dump',
        shell=True, capture_output=True, text=True, errors="replace"
    )
    text = result.stdout or ""
    if not text:
        return ""
    return clean_text(text)

# Helper function to clean text
def clean_text(raw) -> str:
    """
    Cleans raw HTML/text with escape sequences into readable plain text.
    Handles:
      - HTML tags (convert <br>, <p>, <li>, headings, etc.)
      - Escape sequences (\n, \t, \\uXXXX, etc.)
      - Removes URLs, reference markers, image tags
      - Cuts off common trailing sections (References, External Links, etc.)
      - Normalizes whitespace
    """
    # Handle non-string inputs by converting to string
    if not isinstance(raw, str):
        if isinstance(raw, (list, dict)):
            # For lists and dicts, convert to JSON string
            try:
                raw = json.dumps(raw, ensure_ascii=False)
            except (TypeError, ValueError):
                raw = str(raw)
        else:
            raw = str(raw)
    
    # Handle empty or None input
    if not raw:
        return ""
    
    # --- 1. Decode escape sequences ---
    try:
        raw = raw.encode("utf-8").decode("unicode_escape", errors="ignore")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If encoding/decoding fails, use the original string
        pass

    # --- 2. Convert HTML entities (like &amp;) ---
    text = html.unescape(raw)

    # --- 3. Replace key HTML tags with formatting ---
    replacements = {
        r"<br\s*/?>": "\n",
        r"</p>": "\n\n",
        r"<p[^>]*>": "",
        r"<li[^>]*>": "- ",
        r"</li>": "\n",
        r"<h[1-6][^>]*>": "\n# ",   # headings
        r"</h[1-6]>": "\n",
        r"<div[^>]*>": "\n",
        r"</div>": "\n",
        r"<tr[^>]*>": "\n",
        r"</tr>": "\n",
        r"<td[^>]*>": " ",
        r"</td>": " ",
        r"<th[^>]*>": " ",
        r"</th>": " ",
        r"<ul[^>]*>|</ul>|<ol[^>]*>|</ol>": "\n",
        r"<blockquote[^>]*>": "\n> ",
        r"</blockquote>": "\n",
        r"<pre[^>]*>|</pre>": "\n",
        r"<code[^>]*>|</code>": "",
    }
    for pat, repl in replacements.items():
        text = re.sub(pat, repl, text, flags=re.I)

    # --- 4. Remove all remaining HTML tags ---
    text = re.sub(r"<[^>]+>", "", text)

    # --- 5. Cut at common end sections ---
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if re.match(r"^\s*(references?|external links?|see also|gallery|media|further reading|notes)\s*:?\s*$", line, re.I):
            lines = lines[:idx]
            break
    text = "\n".join(lines)

    # --- 6. Remove URLs, ref markers, images, edit links, etc. ---
    text = re.sub(r"https?://\S+|\bwww\.\S+", "", text, flags=re.I)
    text = re.sub(r"\[\s*\d+\s*\]", "", text)  # [1], [2]
    text = re.sub(r"\^\[[^\]]+\]|\^{1,}", "", text)  # ^[note]
    text = re.sub(r"\[(?:edit|[a-z]{2})\]", "", text, flags=re.I)
    text = re.sub(r"\[(?:citation needed|when\?|update)\]", "", text, flags=re.I)
    text = re.sub(r"\[[^\]]+\.(?:jpg|jpeg|png|svg|gif)\]", "", text, flags=re.I)

    # --- 7. Remove lines with iframe/button/nav junk ---
    filtered = []
    for line in text.splitlines():
        s = line.strip()
        if (re.search(r"\b(iframe|button)\b", s, re.I) or
            re.match(r"^\s*\[\s*\d+\s*\]\s+\S+", s) or
            s.lower() in {"[edit]", "edit", "top view", "side view"} or
            s.upper().startswith("CAPTION:") or
            re.match(r"^(main article|see also):", s, re.I) or
            re.match(r"^[*\-]\s+\S+", s)):
            continue
        filtered.append(line)
    text = "\n".join(filtered)

    # --- 8. Normalize whitespace ---
    text = text.replace("\uFFFD", "").replace("�", "")
    text = re.sub(r"[\t ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def generate_summary(text: str):
    summary_prompt = (
        "You are to write a comprehensive and highly descriptive review of the following text, "
        "which was fetched from a web page using curl and may contain some HTML tags or unnecessary words. "
        "Please ignore any HTML tags, formatting artifacts, or irrelevant words that may appear in the text. "
        "Focus on providing a thorough and insightful review: "
        "if the text is a study, discuss the study design, methodology, results, and implications in detail; "
        "if it is a review, elaborate on the main themes, arguments, and perspectives. "
        "Include relevant background, context, and your interpretation, ensuring the review is rich in detail and clarity.\n\n"
        # f"Text: {text}"
    )
    llm_client = get_llm_client()
    if llm_client == 'openai':
        summary = _retryable_openai_call(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user",   "content": text},
            ],
            temperature=0.5,
        )
    elif llm_client == 'claude':
        summary = _retryable_claude_call(
            system=summary_prompt,
            user=f"Text: {text}",
            temperature=0.5,
        )
    elif llm_client == 'ollama':
        summary = _retryable_ollama_call(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user",   "content": text},
            ],
            temperature=0.5,
        )
    else:
        summary = _retryable_gemini_call(
            prompt=f"{summary_prompt}\n\nText: {text}",
            temperature=0.5
        )

    return summary

def relevance_classifier(article: Dict[str, Any], user_query: str) -> tuple[str, bool, Dict[str, Any]]:
    """
    Classifies a processed article as relevant or irrelevant based on its abstract.
    
    An article is considered relevant if:
    - It contains information that is helpful in answering the question.
    - It contains a safety aspect that would be important to include in the answer.
    - It is NOT an animal-based study.

    Parameters:
    - article (dict): A dictionary containing the fetched PubMed article data.
    - user_query (str): The user's original query.

    Returns:
    - pmid (str): PubMed ID of the article.
    - article_is_relevant (bool): Whether the article is relevant or not (True/False).
    - article (dict): The input article dictionary.
    """
    # 1. Safely get the ID, falling back to a default
    article_id = _coerce_to_str(article.get("id") or article.get("ID"), "Unknown ID")

    # 2. Safely get the abstract, with fallbacks to summary and title
    content_for_relevance = _coerce_to_str(article.get("abstract"))
    if not content_for_relevance or len(content_for_relevance) < 20:
        content_for_relevance = _coerce_to_str(article.get("summary"))
    if not content_for_relevance or len(content_for_relevance) < 20:
        content_for_relevance = _coerce_to_str(article.get("title"))
    if not content_for_relevance:
        content_for_relevance = "No content available."

    # 3. Classify relevance using the retryable OpenAI wrapper
    relevance_prompt = (
        "Based on the provided text, is this article relevant to the user's question? "
        "Consider that animal studies are NOT relevant. "
        "Answer with a single word: yes or no."
    )
    
    llm_client = get_llm_client()
    if llm_client == 'openai':
        relevance_raw = _retryable_openai_call(
            messages=[
                {"role": "system", "content": RELEVANCE_CLASSIFIER_PROMPT},
                {"role": "user",   "content": f"Question: {user_query}\n\nArticle Content: {content_for_relevance}"},
            ],
            temperature=0.1
        )
    elif llm_client == 'claude':
        relevance_raw = _retryable_claude_call(
            system=RELEVANCE_CLASSIFIER_PROMPT,
            user=f"Question: {user_query}\n\nArticle Content: {content_for_relevance}",
            temperature=0.1,
        )
    elif llm_client == 'ollama':
        relevance_raw = _retryable_ollama_call(
            messages=[
                {"role": "system", "content": RELEVANCE_CLASSIFIER_PROMPT},
                {"role": "user",   "content": f"Question: {user_query}\n\nArticle Content: {content_for_relevance}"},
            ],
            temperature=0.1,
        )
    else:
        relevance_raw = _retryable_gemini_call(
            prompt=f"{RELEVANCE_CLASSIFIER_PROMPT}\n\nQuestion: {user_query}\n\nArticle Content: {content_for_relevance}",
            temperature=0.1
        )

    # 4. Parse the response
    first_word = relevance_raw.split()[0].strip(string.punctuation).lower() if relevance_raw else ""
    article_is_relevant = first_word not in {"no", "n"}

    return article_id, article_is_relevant, article

#@title concurrent_relevance_classification
def concurrent_relevance_classification(articles, user_query, request_id: Optional[str] = None):
  """
  Concurrent classification of articles as relevant or irrelevant using the relevance_classifier function.

  Parameters:
  - articles (list): A list of article dictionaries to classify.

  Returns:
  - relevant_articles (list): A list of dictionaries of relevant articles.
  - irrelevant_articles (list): A list of dictionaries of irrelevant articles.
  """
  relevant_articles = []
  irrelevant_articles = []
  print("Arctile classification")
  def _relevance_worker(article_tmp):
        if request_id:
            set_request_context(request_id)
        return relevance_classifier(article_tmp, user_query)

  with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_relevance_worker, article_tmp) for article_tmp in articles]
        for future in as_completed(futures):
            try:
                result = future.result()
                # Bucket articles as relevant vs irrelevant
                if result[1]:
                    relevant_articles.append(result[2])
                else:
                    irrelevant_articles.append(result[2])
            except Exception as e:
                print("Error processing article:", e)

  return relevant_articles, irrelevant_articles

"""## Step4. Research Processing
* Summarization
* Relevance Ranking
* Reliability Assessment

### RAG - Reliability Analysis Match

#### MySQL Connection
"""



"""#### Article Matching
* If there is an article match, store it into a list.
* If there is no match, process article and store it into relevant_articles list. Write it to MySQL database.
"""

#@title clean_extracted_text
def clean_extracted_text(text):
    """
    Cleans the extracted text to improve readability by removing unicode, markdown, and ASCII characters.

    Parameters:
    - text (str): The extracted text from the PDF.

    Returns:
    - cleaned_text (str): Cleaned up version of the extracted text.
    """
    # Replace newline characters with spaces
    cleaned_text = text.replace('\n', ' ')

    # Remove any strange unicode characters (like \u202f, \u2002, \xa0)
    cleaned_text = re.sub(r'[\u202f\u2002\xa0]', ' ', cleaned_text)

    # Fix hyphenated words at the end of lines
    cleaned_text = re.sub(r'-\s+', '', cleaned_text)

    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Strip leading/trailing whitespace
    cleaned_text = cleaned_text.strip()

    return cleaned_text

#@title get_article_type
def get_article_type(abstract):
    """
    Determines whether an article is a study or a review.

    - If it is a study (e.g., observational study, randomized controlled trial), return "study".
    - If it is a review (e.g., literature review, systematic review, meta-analysis), return "review".

    Parameters:
    - abstract (str): The abstract of the article.

    Returns:
    - article_type (str): Either "study" or "review".
    """
    llm_client = get_llm_client()
    
    if llm_client == 'openai':
        return get_article_type_openai(abstract, ARTICLE_TYPE_PROMPT)
    if llm_client == 'claude':
        return get_article_type_claude(abstract, ARTICLE_TYPE_PROMPT)
    if llm_client == 'ollama':
        return get_article_type_ollama(abstract, ARTICLE_TYPE_PROMPT)
    return get_article_type_gemini(abstract, ARTICLE_TYPE_PROMPT)



def generate_content_from_pdf(pdf_text, content_type="abstract", publication_type="study"):
    """
    Extracts structured summaries from a research paper PDF.

    - If `content_type` is "abstract", extracts structured abstract details.
    - If `content_type` is "summary":
        - Uses a different summarization prompt based on whether the article is a study or a review.

    Parameters:
    - pdf_text (str): The full text extracted from a research paper PDF.
    - content_type (str): Either "abstract" or "summary".
    - publication_type (str): Either "study" or "review".

    Returns:
    - summary (str): A structured summary of the research paper.
    """
    llm_client = get_llm_client()
    
    if llm_client == 'openai':
        return generate_content_from_pdf_openai(pdf_text, content_type, publication_type,
                                              ABSTRACT_EXTRACTION_PROMPT, REVIEW_SUMMARY_PROMPT, STUDY_SUMMARY_PROMPT)
    if llm_client == 'claude':
        return generate_content_from_pdf_claude(pdf_text, content_type, publication_type,
                                              ABSTRACT_EXTRACTION_PROMPT, REVIEW_SUMMARY_PROMPT, STUDY_SUMMARY_PROMPT)
    if llm_client == 'ollama':
        return generate_content_from_pdf_ollama(pdf_text, content_type, publication_type,
                                              ABSTRACT_EXTRACTION_PROMPT, REVIEW_SUMMARY_PROMPT, STUDY_SUMMARY_PROMPT)
    return generate_content_from_pdf_gemini(pdf_text, content_type, publication_type,
                                              ABSTRACT_EXTRACTION_PROMPT, REVIEW_SUMMARY_PROMPT, STUDY_SUMMARY_PROMPT)


def process_pdf_article(file_info, pdf_counter):
    """
    Process a single PDF article and extract relevant data.

    Args:
        file_info (dict): File metadata and content.
        pdf_counter (int): Counter for naming articles.

    Returns:
        dict: Formatted article extracted from the PDF.
    """
    file_data = file_info['content']
    file_name = file_info['filename']
    content_type = file_info['content_type']

    if content_type not in ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        print(f"Skipping file {file_name}: unsupported content type {content_type}")
        return None

    pdf_text = ""
    metadata = {}

    if content_type == 'application/pdf':
        pdf_document = fitz.open(stream=file_data, filetype="pdf")
        for page in pdf_document:
            page_text = page.get_text()
            page_text = page_text.replace('\n', ' ')
            pdf_text += page_text + " "
        metadata = pdf_document.metadata
    elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        # TODO: Implement DOCX processing
        metadata = {}

    title = metadata.get('title', f'Upload PDF {pdf_counter}')
    if not title or title.strip() == '':
        title = f'Upload PDF {pdf_counter}'

    publication_type = get_article_type(pdf_text)
    abstract = generate_content_from_pdf(pdf_text, content_type="abstract")
    summary = generate_content_from_pdf(pdf_text, content_type="summary", publication_type=publication_type)
    # citation = generate_pdf_ama_citation(metadata, pdf_counter)  # TODO: Implement this function
    citation = f"PDF {pdf_counter}"  # Placeholder

    return {
        'title': title,
        'publication_type': publication_type,
        'url': 'nil',
        'abstract': abstract,
        'is_relevant': True,
        'citation': citation,
        'ID': None,
        'full_text': True,
        'summary': summary
    }


def section_match(list_of_strings, required_titles):
    """
    Capture only the most relevant sections from an article's full text to be cognizant of token size and context windows.
    Does a case-sensitive check to see which of the section titles provided of a given article best match the required section titles.
    This function is only used if the article's full text is available directly in PubMed.

    Parameters:
    - list_of_strings (list): A list of all of an article's section titles to search through.
    - required_titles (list): A list of titles that are deemed to be the most relevant and helpful to include.

    Returns:
    - sections_to_pull (list): A list of matched section titles.
    """
    # Convert all strings in the list to lowercase and keep original strings in a dictionary for lookup
    lower_to_original = {title.lower(): title for title in list_of_strings}

    # Check if all required titles are present (case-insensitively) in the list
    all_titles_present = all(title.lower() in lower_to_original for title in required_titles)

    if all_titles_present:
        # If all required titles are present, collect the matched titles from the list
        sections_to_pull = [lower_to_original[title.lower()] for title in required_titles if title.lower() in lower_to_original]
        return sections_to_pull
    else:
        ### Identify the most important columns
        list_of_strings_str = ', '.join(list_of_strings)

        llm_client = get_llm_client()
        
        if llm_client == 'openai':
            relevant_sections = section_match_openai(list_of_strings, RELEVANT_SECTIONS_PROMPT)
        elif llm_client == 'claude':
            relevant_sections = section_match_claude(list_of_strings, RELEVANT_SECTIONS_PROMPT)
        elif llm_client == 'ollama':
            relevant_sections = section_match_ollama(list_of_strings, RELEVANT_SECTIONS_PROMPT)
        else:
            relevant_sections = section_match_gemini(list_of_strings, RELEVANT_SECTIONS_PROMPT)

        # Split the text into lines
        lines = relevant_sections.split('\n')

        # Create a list to hold distinct values
        sections_to_pull = []

        # Iterate over each line
        for line in lines:
            # Check if line contains ':'
            if ':' in line:
                # Split the line at ':' and strip whitespace from the result
                value = line.split(':', 1)[1].strip()
                # Process and add the values
                # Split the value by '|' and strip whitespace
                split_values = [val.strip() for val in value.split('|')]
                # Add each trimmed value to the set of distinct values
                for val in split_values:
                    if val not in sections_to_pull:
                        sections_to_pull.append(val)

        return sections_to_pull


# #@title process_article
# def process_article(article):
#   """
#   Create the article JSON that includes the following information:
#   - title
#   - publication_type
#   - url
#   - abstract
#   - is_relevant
#   - citation
#   - PMID
#   - PMCID
#   - full_text
#   - reliability analysis

#   Full-text article will be pulled in if it is available via PubMed, Elsevier, Springer, JAMA, and Wiley. Otherwise, the abstract is used.
#   The reliability analysis pulls various attributes from the paper that can be used to deduce the strength of the article's claim.
#   This is the helper function for ThreadPoolExecutor.

#   Parameters:
#   - article (dict): A dictionary containing the article data.

#   Returns:
#   - article_json (dict): A dictionary containing the article information.
#   """

#   try:
#     ### Retrieve the abstract ###
#     abstract = article["MedlineCitation"]["Article"]["Abstract"]["AbstractText"]


#     ### Clean-Up Abstract ###
#     reconstructed_abstract = ""
#     for element in abstract:
#         label = element.attributes.get("Label", "")
#         if reconstructed_abstract:
#           reconstructed_abstract += "\n\n"
#         if label:
#           reconstructed_abstract += f"{label}:\n"
#         reconstructed_abstract += str(element)

#     ### Citation ###
#     citation = generate_ama_citation(article)


#     ### Article JSON ###
#     title = article["MedlineCitation"]["Article"]["ArticleTitle"]
#     url = (f"https://pubmed.ncbi.nlm.nih.gov/"
#               f"{article['MedlineCitation']['PMID']}/")

#     types_html = article['MedlineCitation']['Article']['PublicationTypeList']
#     publication_types = []
#     for pub_type in types_html:
#       publication_types.append(str(pub_type))

#     pmc_id = next((element for element in article['PubmedData']['ArticleIdList'] if element.attributes.get('IdType') == 'pmc'), None)

#     article_json =  {
#                       "title": title,
#                       "publication_type": publication_types,
#                       "url": url,
#                       "abstract": reconstructed_abstract,
#                       "is_relevant": True,
#                       "citation": citation,
#                       "PMID": str(article['MedlineCitation']['PMID']),
#                       "PMCID": str(pmc_id)
#                     }

#     preferred_link = get_preferred_link(article_json['url'])

#     ### Bring in Full Text, if PMC text Available ###
#         ### Bring in Full Text, if PMC text Available ###
#     if (article_json['PMCID'] != None) & (article_json['PMCID'] != "None"):
#       article_content = get_full_text_pubmed(article_json)
#       article_json["full_text"] = True
#     elif preferred_link and "elsevier" in preferred_link:
#       pii = extract_pii(preferred_link)
#       article_data_json = get_full_text_elsevier(pii)
#       if 'full-text-retrieval-response' in article_data_json and 'coredata' in article_data_json['full-text-retrieval-response']:
#         if (article_data_json['full-text-retrieval-response']['coredata']['openaccess'] == 1) | (article_data_json['full-text-retrieval-response']['coredata']['openaccess'] == '1'):
#           article_content = clean_extracted_text(str(article_data_json['full-text-retrieval-response']['originalText']))
#           article_json["full_text"] = True
#         else:
#           article_content = article_json['abstract']
#           article_json["full_text"] = False
#       else:
#         article_content = article_json['abstract'] 
#         article_json["full_text"] = False
#     elif preferred_link and "springer" in preferred_link:
#       try:
#         article_content = clean_extracted_text(str(get_full_text_springer(preferred_link)))
#         article_json["full_text"] = True
#       except:
#         article_content = article_json['abstract']
#     elif preferred_link and "jamanetwork" in preferred_link:
#       try:
#         article_content = clean_extracted_text(str(get_full_text_jama(preferred_link)))
#         article_json["full_text"] = True
#       except:
#         article_content = article_json['abstract']
#     elif preferred_link and "wiley" in preferred_link:
#       try:
#         article_content = clean_extracted_text(str(get_full_text_wiley(preferred_link)))
#         article_json["full_text"] = True
#       except:
#         article_content = article_json['abstract']
#     else:
#       article_content = article_json['abstract']
#       article_json["full_text"] = False

#     if len(article_content) > 1048576:
#       article_content = article_content[:1044000]

#     ### Summarize only the relevant articles and assess strength of work ###
#     study_types = set(['Adaptive Clinical Trial',
#                     'Case Reports',
#                     'Clinical Study',
#                     'Clinical Trial',
#                     'Clinical Trial Protocol',
#                     'Clinical Trial, Phase I',
#                     'Clinical Trial, Phase II',
#                     'Clinical Trial, Phase III',
#                     'Clinical Trial, Phase IV',
#                     'Clinical Trial, Veterinary',
#                     'Comparative Study',
#                     'Controlled Clinical Trial',
#                     'Equivalence Trial',
#                     'Evaluation Study',
#                     # 'Journal Article',
#                     'Multicenter Study',
#                     'Observational Study',
#                     'Observational Study, Veterinary',
#                     'Pragmatic Clinical Trial',
#                     'Preprint',
#                     'Published Erratum',
#                     'Randomized Controlled Trial',
#                     'Randomized Controlled Trial, Veterinary',
#                     'Technical Report',
#                     'Twin Study',
#                     'Validation Study'])

#     article_type = set(article_json['publication_type'])

#     if article_type.isdisjoint(study_types):
#       # review type paper
#       system_prompt_summarize = REVIEW_SUMMARY_PROMPT
#     else:
#       # study type paper
#       system_prompt_summarize = STUDY_SUMMARY_PROMPT

#     reliability_analysis_response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages = [
#             {
#                 "role": "system",
#                 "content": system_prompt_summarize
#             },
#             {
#                 "role": "user",
#                 "content": f"Paper: {article_content}"
#             }
#         ],
#         temperature=0.6,
#         top_p=1
#     )

#     # Extract the generated summary
#     answer_summary = reliability_analysis_response.choices[0].message.content
#     article_json["summary"] = answer_summary

#     return article_json
#   except KeyError:
#     print("No abstract provided")
    
# """### Reliability Analysis"""

# #@title process_article_with_retry
# def process_article_with_retry(article):
#   """
#   Include a retry decorator and buffer for the article processing function.

#   Parameters:
#   - article (dict): A dictionary containing the article data.

#   Returns:
#   - article_json (dict): A dictionary containing the article information.
#   """
#   try:
#       return process_article(article)
#   except Exception as e:
#       print("Error processing article:", e, "- waiting 10 secs")
#       time.sleep(10)
#       print("Trying again")
#       return process_article(article)


# def concurrent_article_processing(articles_to_process):
#   """
#   Concurrent article processing using ThreadPoolExecutor.

#   Parameters:
#   - articles_to_process (list): A list of articles to process.

#   Returns:
#   - relevant_article_summaries (list): A list of relevant article summaries.
#   """
#   relevant_article_summaries = []

#   with ThreadPoolExecutor(max_workers=8) as executor:
#       futures = [executor.submit(process_article_with_retry, article) for article in articles_to_process]
#       for future in as_completed(futures):
#           try:
#               result = future.result()
#               relevant_article_summaries.append(result)
#               print(result)
#               print('-----------------------------------------------------------')
#           except Exception as e:
#               print("Error processing article:", e)
#   return relevant_article_summaries


def calculate_token_count(text: str, model: str = "gpt-4-turbo") -> int:
    """Calculate the number of tokens in a text string."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))

def calculate_relevance_score(text: str, query: str, vectorizer) -> float:
    """Calculate relevance score using TF-IDF and cosine similarity."""
    vectors = vectorizer.transform([text, query])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return float(similarity[0][0])

#Interim function to trim the list of relevant articles to fit within the token limit based on relevance to the user query.
def trim_relevant_articles_by_token_limit(all_relevant_articles, user_query, max_tokens: int = 100000):
    """
    Trim the list of relevant articles to fit within the token limit based on relevance to the user query.
    """
    # Convert articles to string for token counting
    article_strings = [json.dumps(article) for article in all_relevant_articles]
    
    # Initial token count with just the user query
    current_tokens = calculate_token_count(user_query)

    # Check total token count if we include everything
    total_tokens = calculate_token_count(" ".join(article_strings) + user_query)
    if total_tokens <= max_tokens:
        return all_relevant_articles

    # Fit TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    vectorizer.fit(article_strings + [user_query])
    
    # Score articles by relevance to user query
    article_scores = [
        (article, calculate_relevance_score(json.dumps(article), user_query, vectorizer))
        for article in all_relevant_articles
    ]

    # Sort articles by score (most relevant first)
    article_scores.sort(key=lambda x: x[1], reverse=True)

    # Select articles while staying within token limit
    selected_articles = []
    for article, score in article_scores:
        article_token_count = calculate_token_count(json.dumps(article))
        if current_tokens + article_token_count <= max_tokens:
            selected_articles.append(article)
            current_tokens += article_token_count
        else:
            break

    return selected_articles

"""## Step5. Final Output"""

def generate_final_response(all_relevant_articles, query, retrieval_confidence=None):
    """
    Generate the final response to the user's question based on the strongest level of evidence in the provided article summaries.

    Parameters:
    - all_relevant_articles (list): List of all relevant article summaries.
    - query (str): User's question.
    - retrieval_confidence (str, optional): high | medium | low from tiered retrieval.

    Returns:
    - final_output (str): Final response to the user question.
    """
    llm_client = get_llm_client()
    prompt = FINAL_RESPONSE_PROMPT
    if retrieval_confidence == "low":
        prompt = (
            prompt
            + "\n\nRetrieval confidence is LOW: keep the answer shorter, cite only the "
            "strongest available evidence, and end with one sentence noting that "
            "supporting literature may be limited."
        )
    elif retrieval_confidence == "medium":
        prompt = (
            prompt
            + "\n\nRetrieval confidence is MEDIUM: some articles came from broader "
            "search planes — prioritize the strongest human-focused evidence and be "
            "concise where support is thin."
        )

    if llm_client == 'openai':
        return generate_final_response_openai(all_relevant_articles, query, prompt, DISCLAIMER_TEXT)
    if llm_client == 'claude':
        return generate_final_response_claude(all_relevant_articles, query, prompt, DISCLAIMER_TEXT)
    if llm_client == 'ollama':
        return generate_final_response_ollama(all_relevant_articles, query, prompt, DISCLAIMER_TEXT)
    return generate_final_response_gemini(all_relevant_articles, query, prompt, DISCLAIMER_TEXT)


"""### Write Final Output to Database"""

def clean_citation(citation: str):
  """
  Removes the citation number from the citation.

  Parameters:
    - citation (str): The citation to be cleaned.

  Returns:
    - cleaned_citation (str): The cleaned citation.
  """
  # Remove the citation number (e.g., [1]) from the citation
  cleaned_citation = re.sub(r'^\[\d+\]\s*', '', str(citation)).strip()
  return cleaned_citation

def parse_str(input_string: str) -> str:
  """
  Clean string by removing double periods and unnecessary semicolons and parentheses.

  Parameters:
    - input_string (str): The input string to be cleaned.

  Returns:
    - cleaned_string (str): The cleaned string.
  """
  # Replace double periods with a single period
  cleaned_string = input_string.replace("..", ".")

  # Remove unnecessary semicolons and empty parentheses
  cleaned_string = re.sub(r';\s*', ' ', cleaned_string)
  cleaned_string = re.sub(r'\(\s*\)', '', cleaned_string)

  # Remove extra spaces that may result from the above replacements
  cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
  return cleaned_string


def normalize_title(title):
    """
    Normalize titles for comparison by handling all types of quotes and formatting issues
    
    Args:
        title (str): The title to normalize
        
    Returns:
        str: Normalized title
    """
    if not title:
        return ""
    
    # Remove HTML entities
    title = html.unescape(title)
    
    # Remove various types of quotes from beginning and end
    # Handle: "", '', "", '', ‚‛, „‟, etc.
    quote_chars = ['"', "'", '"', '"', ''', ''', '‚', '‛', '„', '‟', '«', '»', '‹', '›']
    
    # Strip whitespace first
    title = title.strip()
    
    # Remove quotes from beginning and end repeatedly until no more quotes
    changed = True
    while changed:
        changed = False
        original_title = title
        
        # Remove quotes from start and end
        for quote in quote_chars:
            if title.startswith(quote):
                title = title[len(quote):]
                changed = True
            if title.endswith(quote):
                title = title[:-len(quote)]
                changed = True
        
        # Remove escaped quotes
        title = title.replace('\\"', '').replace("\\'", '')
        
        # Strip whitespace after each iteration
        title = title.strip()
        
        # Check if anything changed
        if title == original_title:
            changed = False
    
    # Remove trailing punctuation that might cause mismatches
    title = title.rstrip('.,!?;:')
    
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    return title

def print_referenced_articles(final_output, json_data):
    """
    Extracts references from final_output and returns corresponding JSON objects in order.
    Robust to heading style differences and supports DOI-first matching. Falls back to top articles when no matches.

    Args:
        final_output (str): The formatted output containing references
        json_data (list): List of article JSON objects

    Returns:
        list: List of matched articles with specified fields
    """

    # 1) Find references block (support 'References', 'References:', '### References') and stop at disclaimer
    try:
        header_match = re.search(r"(?im)^(#+\s*)?references\s*:?[\t ]*$", final_output)
        if header_match:
            tail = final_output[header_match.end():]
        else:
            tail = final_output.split("References:", 1)[1] if "References:" in final_output else final_output
        end_match = re.search(r"(?is)\n\s*\*\*Disclaimer:\*\*", tail)
        references_section = tail[: end_match.start()] if end_match else tail
    except Exception:
        references_section = final_output

    # 2) Collect numbered reference lines
    reference_lines = []
    for line in references_section.split('\n'):
        s = line.strip()
        if re.match(r"^\[\d+\]", s):
            reference_lines.append(s)

    if not reference_lines:
        for line in final_output.split('\n'):
            s = line.strip()
            if re.match(r"^\[\d+\]", s):
                reference_lines.append(s)

    matched_articles = []

    # Pre-normalize article fields
    pool = [{
        "article": a,
        "title_norm": normalize_title(a.get("title", "")),
        "doi_norm": (a.get("doi", "") or "").lower().strip(),
    } for a in json_data]

    def extract_title_and_doi(ref: str):
        doi_match = re.search(r"\b10\.\d{4,9}/\S+\b", ref, flags=re.I)
        doi_found = (doi_match.group(0).rstrip('.,);').lower() if doi_match else "")
        q = re.search(r'"([^"]+)"', ref)
        if q:
            return q.group(1).strip(), doi_found
        tmp = re.sub(r"^\[\d+\]\s*", "", ref).strip()
        parts = [p.strip() for p in re.split(r"\.(?:\s+|$)", tmp) if p.strip()]
        title_guess = parts[1] if len(parts) >= 2 else (parts[0] if parts else "")
        title_guess = re.sub(r"\bdoi\s*:\s*\S+", "", title_guess, flags=re.I).strip()
        return title_guess, doi_found

    for ref_line in reference_lines:
        print(f"Processing reference: {ref_line}")
        ref_title, ref_doi = extract_title_and_doi(ref_line)
        norm_ref_title = normalize_title(ref_title)

        found = None
        best = 0.0

        # Prefer DOI match
        if ref_doi:
            for item in pool:
                if item["doi_norm"] and item["doi_norm"] == ref_doi:
                    found = item["article"]
                    best = 100.0
                    print("DOI MATCH FOUND!")
                    break

        # Title-based matching
        if not found and norm_ref_title:
            for item in pool:
                t = item["title_norm"]
                if not t:
                    continue
                if norm_ref_title.lower() == t.lower():
                    found = item["article"]
                    best = 100.0
                    print("EXACT TITLE MATCH")
                    break
                if (norm_ref_title.lower() in t.lower() or t.lower() in norm_ref_title.lower()):
                    score = min(len(norm_ref_title), len(t)) / max(len(norm_ref_title), len(t)) * 90.0
                    if score > best:
                        best = score
                        found = item["article"]
                rw = set(norm_ref_title.lower().split())
                aw = set(t.lower().split())
                stop = {'a','an','the','and','or','but','in','on','at','to','for','of','with','by','is','are','was','were','be','been','being'}
                rw -= stop; aw -= stop
                if rw and aw:
                    inter = len(rw & aw)
                    union = len(rw | aw)
                    j = (inter / union) if union else 0.0
                    if inter >= 2 or j >= 0.3:
                        score = j * 80.0
                        if score > best:
                            best = score
                            found = item["article"]

        if found and best > 20.0:
            matched_articles.append({
                "title": found.get('title', ''),
                "url": found.get('url', ''),
                "abstract": found.get('abstract', ''),
                "author_name": found.get('author_name', ''),
                "summary": found.get('summary', ''),
                "id": found.get('id', ''),
                "doi": found.get('doi', ''),
                "date": found.get('date', ''),
                "journal": found.get('journal', ''),
            })
        else:
            print(f"❌ NO RELIABLE MATCH for: {ref_line}")

    # Fallback to first few articles if none matched, to avoid empty citations_obj
    if not matched_articles and json_data:
        for art in json_data[:min(8, len(json_data))]:
            matched_articles.append({
                "title": art.get('title', ''),
                "url": art.get('url', ''),
                "abstract": art.get('abstract', ''),
                "author_name": art.get('author_name', ''),
                "summary": art.get('summary', ''),
                "id": art.get('id', ''),
                "doi": art.get('doi', ''),
                "date": art.get('date', ''),
                "journal": art.get('journal', ''),
            })

    return matched_articles

# Function to recursively replace the invalid values with "Not Available"
def replace_invalid_values(obj):
    if isinstance(obj, dict):  # If the object is a dictionary
        return {key: replace_invalid_values(value) for key, value in obj.items()}
    elif isinstance(obj, list):  # If the object is a list
        return [replace_invalid_values(item) for item in obj]
    elif isinstance(obj, str):  # If it's a string
        if obj.lower() == "none" or obj == "null" or obj == "NaN" or obj == "nan":
            return "Not Detected"
    elif isinstance(obj, float) and (math.isnan(obj)):  # If it's NaN
        return "Not Detected"
    elif obj is None:  # If it's None
        return "Not Detected"
    return obj  # Otherwise, return the value unchanged



def generate_code_from_content(article_content: str, type: str):
    """
    Generates a summary of an article using the configured LLM model.
    
    Parameters:
    - article_content (str): The content of the article to summarize
    
    Returns:
    - str: The generated summary of the article
    """
    llm_client = get_llm_client()
    clean_prompt = system_prompt_function_generator_clean_query
    
    try:
        if llm_client == 'openai':
            return generate_code_from_content_openai(
                article_content, type,
                system_prompt_function_generator_list_search,
                system_prompt_function_generator_id_search,
                clean_prompt,
            )
        if llm_client == 'claude':
            return generate_code_from_content_claude(
                article_content, type,
                system_prompt_function_generator_list_search,
                system_prompt_function_generator_id_search,
                clean_prompt,
            )
        if llm_client == 'ollama':
            return generate_code_from_content_ollama(
                article_content, type,
                system_prompt_function_generator_list_search,
                system_prompt_function_generator_id_search,
                clean_prompt,
            )
        return generate_code_from_content_gemini(
            article_content, type,
            system_prompt_function_generator_list_search,
            system_prompt_function_generator_id_search,
            clean_prompt,
        )
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None


def generate_prompt_from_content(article_content: str, prompt_type: str, include_rationale: bool = False):
    llm_client = get_llm_client()

    system_prompts = {
        "ABSTRACT_EXTRACTION_PROMPT_SAMPLE": ABSTRACT_EXTRACTION_PROMPT,     # <-- include your example + public rationale here
        "STUDY_SUMMARY_PROMPT_SAMPLE": STUDY_SUMMARY_PROMPT,
        "REVIEW_SUMMARY_PROMPT_SAMPLE": REVIEW_SUMMARY_PROMPT,
        "RELEVANCE_CLASSIFIER_PROMPT_SAMPLE": RELEVANCE_CLASSIFIER_PROMPT,
        "ARTICLE_TYPE_PROMPT_SAMPLE": ARTICLE_TYPE_PROMPT,
        "FINAL_RESPONSE_PROMPT_SAMPLE": FINAL_RESPONSE_PROMPT,
        "RELEVANT_SECTIONS_PROMPT_SAMPLE": RELEVANT_SECTIONS_PROMPT,
        "DETERMINE_QUESTION_VALIDITY_PROMPT_SAMPLE": DETERMINE_QUESTION_VALIDITY_PROMPT,
        "GENERAL_QUERY_PROMPT_SAMPLE": GENERAL_QUERY_PROMPT,
        "QUERY_CONTENTION_PROMPT_SAMPLE": QUERY_CONTENTION_PROMPT,
    }

    if llm_client == "openai":
        return generate_prompt_from_content_openai(
            article_content=article_content,
            prompt_type=prompt_type,
            system_prompts=system_prompts,
            include_rationale=include_rationale
        )
    if llm_client == "claude":
        return generate_prompt_from_content_claude(article_content, prompt_type, system_prompts, include_rationale)
    if llm_client == "ollama":
        return generate_prompt_from_content_ollama(article_content, prompt_type, system_prompts, include_rationale)
    return generate_prompt_from_content_gemini(article_content, prompt_type, system_prompts, include_rationale)


# --------------------------------------------------------------------------- #
# Rate-limit resilience: curl fallback (requests + urllib / Entrez)
# --------------------------------------------------------------------------- #
# Keeps logic out of user_search_apis.py / user_list_search.py. When an HTTP API
# returns 429/409/503 or a JSON throttle payload (e.g. Stack Exchange), we retry
# the same URL with curl. urllib.request.urlopen is patched for PubMed Entrez.

_RATE_RESILIENCE_INSTALLED = False
_ORIGINAL_REQUESTS_GET = None
_ORIGINAL_URLOPEN = None

RATE_LIMIT_HTTP_CODES = frozenset({429, 409, 503})


def is_rate_limit_http_status(status_code: Optional[int]) -> bool:
    if status_code is None:
        return False
    try:
        return int(status_code) in RATE_LIMIT_HTTP_CODES
    except (TypeError, ValueError):
        return False


def _json_body_indicates_rate_limit(resp: requests.Response) -> bool:
    """
    Some APIs return HTTP 200 with JSON describing throttling (Stack Exchange).
    """
    if resp.status_code in RATE_LIMIT_HTTP_CODES:
        return True
    if resp.status_code >= 400:
        return is_rate_limit_http_status(resp.status_code)
    ctype = (resp.headers.get("Content-Type") or "").lower()
    if "json" not in ctype:
        return False
    try:
        j = resp.json()
    except Exception:
        return False
    if not isinstance(j, dict):
        return False
    if "error_id" not in j and "error_message" not in j and "error_name" not in j:
        return False
    msg = f"{j.get('error_message', '')} {j.get('error_name', '')}".lower()
    if any(x in msg for x in ("throttle", "too many requests", "rate limit", "quota")):
        return True
    eid = j.get("error_id")
    if eid is not None and int(eid) in (429, 502):
        return True
    return False


class CurlBackedResponse:
    """Minimal requests.Response-like object for bodies fetched via curl."""

    def __init__(self, text: str, url: str, status_code: int = 200):
        self.text = text
        self.content = text.encode("utf-8", errors="replace")
        self.status_code = status_code
        self.headers = {}
        self.url = url
        self.encoding = "utf-8"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            err = requests.HTTPError(f"HTTP {self.status_code} for {self.url}")
            err.response = self  # type: ignore[attr-defined]
            raise err

    def json(self, **kwargs):
        return json.loads(self.text)


def curl_fetch_url_text(url: str, timeout: int = 120) -> str:
    """GET a URL with curl (no shell). Returns decoded text; empty string on failure."""
    cmd = [
        "curl",
        "-sS",
        "-L",
        "-m",
        str(timeout),
        "--compressed",
        "-H",
        "User-Agent: CustomNerd/1.0 (+https://localhost; rate-limit fallback)",
        url,
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout + 20,
        )
    except subprocess.TimeoutExpired:
        logging.warning("[curl_fallback] timeout for %s", url[:160])
        return ""
    if proc.returncode != 0:
        logging.warning(
            "[curl_fallback] curl exit %s for %s stderr=%s",
            proc.returncode,
            url[:120],
            (proc.stderr or "")[:240],
        )
        return ""
    return proc.stdout or ""


def _prepare_get_url(url: str, params: Optional[Dict[str, Any]]) -> str:
    if not params:
        return url
    prep = requests.PreparedRequest()
    prep.prepare_url(url, params)
    return prep.url


def requests_get_with_curl_fallback(url, params=None, **kwargs):
    """
    GET via requests; on rate-limit status or JSON throttle, retry the same URL with curl.
    """
    if _ORIGINAL_REQUESTS_GET is None:
        raise RuntimeError("install_rate_limit_curl_resilience() must be called first")
    resp = _ORIGINAL_REQUESTS_GET(url, params=params, **kwargs)
    need_curl = _json_body_indicates_rate_limit(resp)
    if not need_curl:
        return resp

    full_url = getattr(resp, "url", None) or _prepare_get_url(url, params)
    tmo = kwargs.get("timeout")
    curl_timeout = 120
    if isinstance(tmo, (int, float)):
        curl_timeout = min(300, int(tmo) + 20)

    logging.warning(
        "[rate_limit] retrying via curl (status=%s) %s",
        resp.status_code,
        full_url[:120],
    )
    text = curl_fetch_url_text(full_url, timeout=curl_timeout)
    if text:
        return CurlBackedResponse(text, full_url, 200)
    return resp


def _patched_requests_get(url, params=None, **kwargs):
    return requests_get_with_curl_fallback(url, params=params, **kwargs)


def _urlopen_target_to_url(target) -> str:
    if isinstance(target, str):
        return target
    if hasattr(target, "full_url"):
        return target.full_url
    return target.get_full_url()


def _patched_urlopen(*args, **kwargs):
    try:
        return _ORIGINAL_URLOPEN(*args, **kwargs)
    except urllib.error.HTTPError as e:
        if e.code not in RATE_LIMIT_HTTP_CODES:
            raise
        url = _urlopen_target_to_url(args[0])
        logging.warning("[rate_limit] urllib HTTP %s; curl fallback %s", e.code, url[:120])
        data = curl_fetch_url_text(url, timeout=120).encode("utf-8", errors="replace")
        return io.BytesIO(data)


def install_rate_limit_curl_resilience(force: bool = False) -> None:
    """
    Patch requests.get and urllib.request.urlopen so rate-limited HTTP responses
    retry the same URL via curl. Idempotent.
    """
    global _RATE_RESILIENCE_INSTALLED, _ORIGINAL_REQUESTS_GET, _ORIGINAL_URLOPEN
    if _RATE_RESILIENCE_INSTALLED and not force:
        return
    if _ORIGINAL_REQUESTS_GET is None:
        _ORIGINAL_REQUESTS_GET = requests.get
    if _ORIGINAL_URLOPEN is None:
        _ORIGINAL_URLOPEN = urllib.request.urlopen
    requests.get = _patched_requests_get
    urllib.request.urlopen = _patched_urlopen
    # Biopython Entrez does `from urllib.request import urlopen`; rebind to patched callable.
    try:
        import Bio.Entrez as _bio_entrez

        _bio_entrez.urlopen = urllib.request.urlopen
    except Exception:
        pass
    _RATE_RESILIENCE_INSTALLED = True
    logging.info("Rate-limit curl resilience active (requests.get, urllib.request.urlopen)")


def run_with_rate_limit_curl_fallback(fn, *args, **kwargs):
    """
    Call any user-defined function (e.g. collect_articles or fetch_articles_by_ids)
    after ensuring curl resilience is installed. Use when user modules must stay unchanged.
    """
    install_rate_limit_curl_resilience()
    return fn(*args, **kwargs)


def collect_articles_with_curl_fallback(collect_fn, query_list, *args, **kwargs):
    return run_with_rate_limit_curl_fallback(collect_fn, query_list, *args, **kwargs)


_RETRIEVAL_STOPWORDS = frozenset(
    "a an the is are was were be been being have has had do does did will would "
    "can could should may might must shall to of in for on with at by from as into "
    "through during before after above below between out off over under again "
    "how what when where why which who whom this that these those i me my we our "
    "you your they their it its".split()
)

_CASCADE_BROAD_QUERY_PROMPT = (
    "You are an expert at generating broad, alternative search queries for "
    "scientific literature retrieval. Given a user question, produce one concise "
    "PubMed-style query using synonyms, related terms, and OR expansions. "
    "Return only the query string and no other text."
)

RETRIEVAL_DEFAULTS: Dict[str, Any] = {
    "mode": "legacy",
    "planes": ["P1", "P2", "P3", "P4", "P5"],
    "short_circuit": False,
    "min_articles": 2,
    "min_term_coverage": 0.4,
    "min_top_score": 0.15,
    "max_queries_p1": 8,
    "max_queries_p4": 12,
    "rerank_top_k": 30,
    "p1_quota": 0.6,
    "facet_suffix": "",
    "lexicon": "",
}

RETRIEVAL_NERD_PROFILES: Dict[str, Dict[str, Any]] = {
    "DietNerd": {
        "mode": "cascade",
        "facet_suffix": "[Humans]",
    },
    "CloudNerd": {
        "mode": "cascade",
        "lexicon": (
            "aws,amazon,azure,gcp,google cloud,heroku,terraform,kubernetes,docker,"
            "lambda,ec2,s3,blob,devops,cloud run,firebase,stack,helm,nginx"
        ),
    },
    "NewsNerd": {"mode": "legacy"},
    "SpaceNerd": {"mode": "legacy"},
    "SciNERd": {"mode": "legacy"},
}

_active_nerd_name: Optional[str] = None
_retrieval_profile_override: Dict[str, Any] = {}
_active_nerd_state_path: Optional[str] = None


def configure_retrieval_state_path(path: Optional[str]) -> None:
    global _active_nerd_state_path
    _active_nerd_state_path = path


def _persist_active_nerd_state(state_name: Optional[str]) -> None:
    if not _active_nerd_state_path:
        return
    try:
        from pathlib import Path

        path = Path(_active_nerd_state_path)
        if state_name:
            path.write_text(state_name.strip(), encoding="utf-8")
        elif path.is_file():
            path.unlink(missing_ok=True)
    except Exception as exc:
        print(f"[retrieval] could not persist active nerd state: {exc}")


def restore_active_nerd_profile_from_disk() -> None:
    """Restore last loaded saved state after restart."""
    if not _active_nerd_state_path:
        return
    try:
        from pathlib import Path

        path = Path(_active_nerd_state_path)
        if not path.is_file():
            return
        state_name = path.read_text(encoding="utf-8").strip()
        if state_name:
            set_active_nerd_profile(state_name)
    except Exception as exc:
        print(f"[retrieval] could not restore active nerd state: {exc}")


def _safe_profile_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().strip('"').lower()
    if text in ("1", "true", "yes", "on"):
        return True
    if text in ("0", "false", "no", "off", ""):
        return False
    return default


def _safe_profile_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_profile_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _legacy_env_retrieval_overrides() -> Dict[str, Any]:
    """Honor RETRIEVAL_* env vars when no known Nerd profile is active."""
    overrides: Dict[str, Any] = {}

    def _env(name: str) -> str:
        return (os.getenv(name) or "").strip().strip('"')

    mode = _env("RETRIEVAL_MODE").lower()
    if mode in ("cascade", "legacy"):
        overrides["mode"] = mode

    planes_raw = _env("RETRIEVAL_PLANES")
    if planes_raw:
        planes = [p.strip().upper() for p in planes_raw.split(",") if p.strip()]
        if planes:
            overrides["planes"] = planes

    if _env("RETRIEVAL_SHORT_CIRCUIT"):
        overrides["short_circuit"] = _safe_profile_bool(_env("RETRIEVAL_SHORT_CIRCUIT"), False)

    for env_key, profile_key, caster, default in (
        ("RETRIEVAL_MIN_ARTICLES", "min_articles", _safe_profile_int, 2),
        ("RETRIEVAL_MAX_QUERIES_P1", "max_queries_p1", _safe_profile_int, 8),
        ("RETRIEVAL_MAX_QUERIES_P4", "max_queries_p4", _safe_profile_int, 12),
        ("RETRIEVAL_RERANK_TOP_K", "rerank_top_k", _safe_profile_int, 30),
        ("RETRIEVAL_MIN_TERM_COVERAGE", "min_term_coverage", _safe_profile_float, 0.4),
        ("RETRIEVAL_MIN_TOP_SCORE", "min_top_score", _safe_profile_float, 0.15),
        ("RETRIEVAL_P1_QUOTA", "p1_quota", _safe_profile_float, 0.6),
    ):
        raw = _env(env_key)
        if raw:
            overrides[profile_key] = caster(raw, default)

    facet = _env("RETRIEVAL_FACET_SUFFIX")
    if facet:
        overrides["facet_suffix"] = facet

    lexicon = _env("RETRIEVAL_LEXICON")
    if lexicon:
        overrides["lexicon"] = lexicon

    return overrides


def _normalize_retrieval_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce profile fields so bad/missing values never crash retrieval."""
    out = dict(RETRIEVAL_DEFAULTS)
    out.update(profile)

    mode = str(out.get("mode", "legacy")).strip().lower()
    out["mode"] = mode if mode in ("legacy", "cascade") else "legacy"

    planes = out.get("planes") or RETRIEVAL_DEFAULTS["planes"]
    if isinstance(planes, str):
        planes = [p.strip().upper() for p in planes.split(",") if p.strip()]
    elif isinstance(planes, (list, tuple, set)):
        planes = [str(p).strip().upper() for p in planes if str(p).strip()]
    else:
        planes = list(RETRIEVAL_DEFAULTS["planes"])
    out["planes"] = planes or list(RETRIEVAL_DEFAULTS["planes"])

    out["short_circuit"] = _safe_profile_bool(out.get("short_circuit"), False)
    out["min_articles"] = max(0, _safe_profile_int(out.get("min_articles"), 2))
    out["max_queries_p1"] = max(1, _safe_profile_int(out.get("max_queries_p1"), 8))
    out["max_queries_p4"] = max(1, _safe_profile_int(out.get("max_queries_p4"), 12))
    out["rerank_top_k"] = max(1, _safe_profile_int(out.get("rerank_top_k"), 30))
    out["min_term_coverage"] = _safe_profile_float(out.get("min_term_coverage"), 0.4)
    out["min_top_score"] = _safe_profile_float(out.get("min_top_score"), 0.15)
    out["p1_quota"] = min(1.0, max(0.0, _safe_profile_float(out.get("p1_quota"), 0.6)))
    out["facet_suffix"] = str(out.get("facet_suffix") or "")
    out["lexicon"] = str(out.get("lexicon") or "")
    return out


def set_retrieval_profile_override(overrides: Optional[Dict[str, Any]] = None) -> None:
    global _retrieval_profile_override
    _retrieval_profile_override = dict(overrides or {})


def clear_retrieval_profile_override() -> None:
    set_retrieval_profile_override(None)


def _normalize_nerd_profile_key(state_name: str) -> Optional[str]:
    if not state_name:
        return None
    name = state_name.strip()
    if name in RETRIEVAL_NERD_PROFILES:
        return name
    lower = name.lower()
    for key in RETRIEVAL_NERD_PROFILES:
        if lower.startswith(key.lower()):
            return key
    return None


def set_active_nerd_profile(state_name: Optional[str]) -> None:
    global _active_nerd_name
    try:
        _active_nerd_name = state_name.strip() if state_name else None
        key = _normalize_nerd_profile_key(_active_nerd_name or "")
        mode = get_retrieval_profile().get("mode", "legacy")
        print(f"[retrieval] active nerd={_active_nerd_name!r} profile={key!r} mode={mode}")
        _persist_active_nerd_state(_active_nerd_name)
    except Exception as exc:
        print(f"[retrieval] set_active_nerd_profile failed ({exc!r}); using legacy defaults")


def get_retrieval_profile() -> Dict[str, Any]:
    profile = dict(RETRIEVAL_DEFAULTS)
    key = _normalize_nerd_profile_key(_active_nerd_name or "")
    if key:
        profile.update(RETRIEVAL_NERD_PROFILES[key])
    else:
        profile.update(_legacy_env_retrieval_overrides())
    if _retrieval_profile_override:
        profile.update(_retrieval_profile_override)
    return _normalize_retrieval_profile(profile)


def _frontend_user_env_path() -> str:
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(backend_dir, "..", "customnerd-website", "user_env.js"))


def load_frontend_user_flow() -> Dict[str, Any]:
    try:
        with open(_frontend_user_env_path(), "r", encoding="utf-8") as f:
            content = f.read()
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        if start_idx == -1 or end_idx <= 0:
            return {}
        import json5

        config = json5.loads(content[start_idx:end_idx])
        user_flow = config.get("USER_FLOW", {})
        return user_flow if isinstance(user_flow, dict) else {}
    except Exception:
        return {}


def is_user_cascade_retrieval_enabled() -> bool:
    cascade = load_frontend_user_flow().get("cascade_retrieval")
    if not isinstance(cascade, dict):
        return False
    return bool(cascade.get("visible", False))


def is_cascade_mode() -> bool:
    try:
        return is_user_cascade_retrieval_enabled()
    except Exception:
        return False


def _enabled_retrieval_planes() -> set[str]:
    planes = get_retrieval_profile().get("planes") or RETRIEVAL_DEFAULTS["planes"]
    return {str(p).strip().upper() for p in planes if str(p).strip()}


def resolve_title(title_text: Optional[str], body_text: str) -> str:
    if title_text and str(title_text).strip():
        return str(title_text).strip()
    body = (body_text or "").strip()
    if not body:
        return ""
    head = body.split("?")[0].strip()
    if head and len(head) <= 200:
        return head + ("?" if "?" in body[: len(head) + 1] else "")
    return body[:200].strip()


def get_article_dedupe_key(article: Any) -> str:
    if not isinstance(article, dict):
        return str(id(article))
    mc = article.get("MedlineCitation")
    if isinstance(mc, dict) and mc.get("PMID"):
        return f"pmid:{mc.get('PMID')}"
    for key in ("id", "answer_id", "PMID", "url", "link"):
        val = article.get(key)
        if val:
            return f"{key}:{val}"
    title = article.get("title") or article.get("Title")
    if title:
        return f"title:{str(title).strip().lower()[:200]}"
    return f"obj:{id(article)}"


def merge_and_dedupe_articles(existing: list, extra: list) -> list:
    seen = {get_article_dedupe_key(a) for a in existing}
    merged = list(existing)
    for art in extra:
        key = get_article_dedupe_key(art)
        if key in seen:
            continue
        seen.add(key)
        merged.append(art)
    return merged


def extract_key_terms(query: str, title: Optional[str] = None) -> list:
    text = f"{title or ''} {query}"
    terms: list = []
    seen: set = set()

    def add(tok: str) -> None:
        t = tok.strip().lower()
        if len(t) < 3 or t in seen or t in _RETRIEVAL_STOPWORDS:
            return
        seen.add(t)
        terms.append(t)

    for m in re.finditer(r"[a-zA-Z][a-zA-Z0-9_./:-]{2,}", text):
        add(m.group(0))

    lexicon = get_retrieval_profile().get("lexicon") or ""
    if lexicon:
        lower = text.lower()
        for term in lexicon.split(","):
            term = term.strip().lower()
            if term and term in lower:
                add(term)

    return terms[:24]


def _article_corpus_text(articles: list) -> str:
    parts: list = []
    for art in articles or []:
        if not isinstance(art, dict):
            parts.append(str(art))
            continue
        mc = art.get("MedlineCitation")
        if isinstance(mc, dict):
            article_node = mc.get("Article") or {}
            parts.append(str(article_node.get("ArticleTitle") or ""))
            abstract = article_node.get("Abstract") or {}
            if isinstance(abstract, dict):
                for block in abstract.get("AbstractText") or []:
                    parts.append(str(block))
            else:
                parts.append(str(abstract))
        parts.extend(
            [
                str(art.get("title") or ""),
                str(art.get("abstract") or ""),
                str(art.get("summary") or ""),
                str(art.get("answer_body") or ""),
            ]
        )
    return " ".join(parts).lower()


def _article_text_for_rank(article: Any) -> str:
    if not isinstance(article, dict):
        return str(article)[:4000]
    mc = article.get("MedlineCitation")
    if isinstance(mc, dict):
        article_node = mc.get("Article") or {}
        title = str(article_node.get("ArticleTitle") or "")
        abstract = article_node.get("Abstract") or {}
        abs_text = ""
        if isinstance(abstract, dict):
            for block in abstract.get("AbstractText") or []:
                abs_text += " " + str(block)
        else:
            abs_text = str(abstract)
        return f"{title} {abs_text}".strip()
    return " ".join(
        str(article.get(k) or "")
        for k in ("title", "abstract", "summary", "answer_body", "body")
    ).strip()


def _top_tfidf_score(articles: list, query_text: str) -> float:
    if not articles or not query_text:
        return 0.0
    texts = [_article_text_for_rank(a) for a in articles]
    texts = [t for t in texts if t.strip()]
    if not texts:
        return 0.0
    try:
        vec = TfidfVectorizer(stop_words="english", max_features=5000)
        mat = vec.fit_transform(texts + [query_text])
        sims = cosine_similarity(mat[-1], mat[:-1]).flatten()
        return float(max(sims)) if len(sims) else 0.0
    except Exception:
        return 0.0


def passes_retrieval_quality_gate(
    articles: list,
    query_text: str,
    *,
    terms: Optional[list] = None,
) -> tuple:
    cfg = get_retrieval_profile()
    min_articles = cfg.get("min_articles", 2)
    min_coverage = cfg.get("min_term_coverage", 0.4)
    min_top = cfg.get("min_top_score", 0.15)

    count = len(articles or [])
    terms = terms if terms is not None else extract_key_terms(query_text)
    corpus = _article_corpus_text(articles)
    coverage = 1.0
    if terms:
        coverage = sum(1 for t in terms if t.lower() in corpus) / len(terms)

    top_score = _top_tfidf_score(articles, query_text)
    passed = count >= min_articles and coverage >= min_coverage

    if passed and coverage >= 0.6 and top_score >= min_top:
        confidence = "high"
    elif passed:
        confidence = "medium"
    else:
        confidence = "low"

    meta = {
        "article_count": count,
        "term_coverage": round(coverage, 3),
        "top_tfidf_score": round(top_score, 3),
        "passed": passed,
    }
    return passed, confidence, meta


def _cascade_normalize_queries(raw_list: list, max_queries: int) -> list:
    import clean_query

    try:
        return clean_query.clean_query(raw_list, max_queries=max_queries)
    except Exception:
        queries = [str(q).strip() for q in raw_list if q and str(q).strip()]
        if max_queries > 0:
            return queries[:max_queries]
        return queries


def _cascade_generate_queries(
    text: str,
    *,
    general_prompt: Optional[str] = None,
    max_queries: int = 8,
) -> list:
    try:
        _, _, raw_list = query_generation(
            text,
            general_query_prompt_override=general_prompt,
            query_contention_enabled_override=False,
        )
    except Exception as exc:
        print(f"[tiered] query_generation failed ({exc}); using deterministic backup")
        return deterministic_backup_queries(text, max_queries=max_queries)
    if raw_list and isinstance(raw_list[0], str) and not raw_list[0].strip().startswith("{"):
        import clean_query

        return clean_query.clean_query(raw_list, max_queries=max_queries)
    return _cascade_normalize_queries(raw_list, max_queries)


def deterministic_backup_queries(text: str, max_queries: int = 8) -> list:
    lower = (text or "").lower()
    tokens = [
        t for t in re.findall(r"[a-z0-9]+", lower)
        if len(t) > 2 and t not in _RETRIEVAL_STOPWORDS
    ]
    lexicon_hits: list = []
    lexicon = get_retrieval_profile().get("lexicon") or ""
    if lexicon:
        for term in lexicon.split(","):
            term = term.strip().lower()
            if term and term in lower:
                lexicon_hits.append(term)

    queries: list = []
    seen: set = set()

    def add(q: str) -> None:
        q = " ".join(q.split()).strip()
        if q and q not in seen and len(queries) < max_queries:
            seen.add(q)
            queries.append(q)

    if tokens:
        add(" ".join(tokens[:6]))
        add(" ".join(tokens[:4]))
        if len(tokens) >= 3:
            add(" ".join(tokens[1:5]))
    for term in lexicon_hits[:3]:
        add(f"{term} {' '.join(tokens[:4])}".strip())
    title_short = resolve_title(None, text)
    if title_short:
        add(title_short.rstrip("?"))
    return queries[:max_queries]


def _apply_facet_suffix(queries: list) -> list:
    suffix = (get_retrieval_profile().get("facet_suffix") or "").strip()
    if not suffix:
        return queries
    out: list = []
    for q in queries:
        q = q.strip()
        if not q:
            continue
        if suffix.lower() in q.lower():
            out.append(q)
        else:
            out.append(f"{q} {suffix}".strip())
    return out


def _tag_plane_articles(articles: list, plane_id: str, tier: str) -> list:
    for art in articles:
        if isinstance(art, dict):
            art["retrieval_plane"] = plane_id
            art["retrieval_tier"] = tier
    return articles


def _invoke_collect(collect_fn, queries: list) -> list:
    if not queries:
        return []
    try:
        result = collect_fn(queries)
    except TypeError:
        result = collect_fn(queries, max_date=None)
    return list(result or [])


def build_gap_fill_queries(
    query: str,
    title: Optional[str],
    missing: list,
    *,
    max_queries: int = 6,
) -> list:
    resolved = resolve_title(title, query)
    queries: list = []
    seen: set = set()

    def add(q: str) -> None:
        q = " ".join(q.split()).strip()
        if q and q not in seen and len(queries) < max_queries:
            seen.add(q)
            queries.append(q)

    for term in missing[:max_queries]:
        add(f"{term} {resolved[:80]}".strip())
        add(term)
    if not queries:
        queries = deterministic_backup_queries(query, max_queries=max_queries)
    return queries


def rerank_tiered_articles(
    articles: list,
    query_text: str,
    *,
    top_k: Optional[int] = None,
) -> list:
    with lifecycle_scope("Reranking"):
        if not articles:
            return []
        cfg = get_retrieval_profile()
        top_k = top_k or cfg.get("rerank_top_k", 30)
        quota_ratio = cfg.get("p1_quota", 0.6)

        p1 = [a for a in articles if isinstance(a, dict) and a.get("retrieval_plane") == "P1"]
        other = [a for a in articles if a not in p1]
        p1_slots = max(1, int(top_k * quota_ratio)) if p1 else 0
        other_slots = top_k - p1_slots

        def rank_pool(pool: list) -> list:
            if not pool:
                return []
            texts = [_article_text_for_rank(a) for a in pool]
            if not any(t.strip() for t in texts):
                return pool
            try:
                vec = TfidfVectorizer(stop_words="english", max_features=5000)
                mat = vec.fit_transform(texts + [query_text])
                sims = cosine_similarity(mat[-1], mat[:-1]).flatten()
                ranked = sorted(zip(pool, sims), key=lambda x: x[1], reverse=True)
                return [a for a, _ in ranked]
            except Exception:
                return pool

        ranked_p1 = rank_pool(p1)[:p1_slots]
        ranked_other = rank_pool(other)[:other_slots]
        combined = ranked_p1 + ranked_other
        seen_keys = set()
        deduped: list = []
        for art in combined:
            key = get_article_dedupe_key(art)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped.append(art)
        if len(deduped) < len(articles):
            for art in rank_pool(articles):
                key = get_article_dedupe_key(art)
                if key not in seen_keys:
                    seen_keys.add(key)
                    deduped.append(art)
                if len(deduped) >= top_k:
                    break
        return deduped[:top_k]


def _confidence_from_best_plane(best_plane: Optional[str], gate_confidence: str) -> str:
    if best_plane == "P1":
        return "high" if gate_confidence in ("high", "medium") else "medium"
    if best_plane in ("P2", "P3"):
        return "medium"
    if best_plane:
        return "low"
    return gate_confidence


def tiered_collect_articles(
    collect_fn,
    input_text: str,
    p1_query_list: list,
    *,
    title_text: Optional[str] = None,
) -> tuple:
    try:
        return _tiered_collect_articles_impl(
            collect_fn, input_text, p1_query_list, title_text=title_text
        )
    except Exception as exc:
        import traceback

        print(f"[tiered] tiered_collect_articles failed ({exc!r}); caller should use legacy collect")
        traceback.print_exc()
        return [], {
            "retrieval_mode": "cascade",
            "planes_run": [],
            "planes_log": [f"error: {exc}"],
            "queries_per_plane": {},
            "retrieval_confidence": "low",
            "quality_gate": {},
            "error": str(exc),
        }


def _tiered_collect_articles_impl(
    collect_fn,
    input_text: str,
    p1_query_list: list,
    *,
    title_text: Optional[str] = None,
) -> tuple:
    planes_enabled = _enabled_retrieval_planes()
    cfg = get_retrieval_profile()
    short_circuit = cfg.get("short_circuit", False)
    max_p4 = cfg.get("max_queries_p4", 12)

    meta: Dict[str, Any] = {
        "retrieval_mode": "cascade",
        "planes_run": [],
        "planes_log": [],
        "queries_per_plane": {},
        "retrieval_confidence": "low",
        "quality_gate": {},
    }
    all_articles: list = []
    best_plane: Optional[str] = None

    def log(msg: str) -> None:
        print(f"[tiered] {msg}")
        meta["planes_log"].append(msg)

    def run_plane(plane_id: str, tier: str, queries: list) -> list:
        if plane_id not in planes_enabled or not queries:
            return []
        tagged_queries = queries
        if plane_id == "P3":
            tagged_queries = _apply_facet_suffix(queries)
        batch = _invoke_collect(collect_fn, tagged_queries)
        batch = _tag_plane_articles(batch, plane_id, tier)
        meta["planes_run"].append(plane_id)
        meta["queries_per_plane"][plane_id] = len(tagged_queries)
        log(f"{plane_id} tier={tier} queries={len(tagged_queries)} articles={len(batch)}")
        return batch

    import clean_query as cq_mod

    p1_queries = cq_mod.clean_query(
        [q.strip() for q in (p1_query_list or []) if q and str(q).strip()],
        max_queries=cfg.get("max_queries_p1", 8),
    )
    p1_batch = run_plane("P1", "precision", p1_queries)
    if p1_batch:
        all_articles = merge_and_dedupe_articles(all_articles, p1_batch)
        best_plane = "P1"
    passed, conf, gate_meta = passes_retrieval_quality_gate(all_articles, input_text)
    meta["quality_gate"]["P1"] = gate_meta
    if short_circuit and passed:
        meta["retrieval_confidence"] = _confidence_from_best_plane("P1", conf)
        return rerank_tiered_articles(all_articles, input_text), meta

    # P2 — relaxed title/keywords
    title = resolve_title(title_text, input_text)
    p2_queries = _cascade_generate_queries(title or input_text, max_queries=8) if title or input_text else []
    p2_batch = run_plane("P2", "relaxed", p2_queries)
    if p2_batch:
        all_articles = merge_and_dedupe_articles(all_articles, p2_batch)
        if not best_plane:
            best_plane = "P2"
    passed, conf, gate_meta = passes_retrieval_quality_gate(all_articles, input_text)
    meta["quality_gate"]["P2"] = gate_meta
    if short_circuit and passed:
        meta["retrieval_confidence"] = _confidence_from_best_plane(best_plane, conf)
        return rerank_tiered_articles(all_articles, input_text), meta

    # P3 — domain facet suffix
    p3_seed = p1_queries or p2_queries or _cascade_generate_queries(input_text, max_queries=4)
    p3_batch = run_plane("P3", "facet", p3_seed)
    if p3_batch:
        all_articles = merge_and_dedupe_articles(all_articles, p3_batch)
        if not best_plane:
            best_plane = "P3"
    passed, conf, gate_meta = passes_retrieval_quality_gate(all_articles, input_text)
    meta["quality_gate"]["P3"] = gate_meta
    if short_circuit and passed:
        meta["retrieval_confidence"] = _confidence_from_best_plane(best_plane, conf)
        return rerank_tiered_articles(all_articles, input_text), meta

    # P4 — broad expansion
    p4_queries: list = []
    seen_q: set = set()
    for prompt in (GENERAL_QUERY_PROMPT, _CASCADE_BROAD_QUERY_PROMPT):
        batch = _cascade_generate_queries(input_text, general_prompt=prompt, max_queries=max_p4)
        for q in batch:
            if q not in seen_q:
                seen_q.add(q)
                p4_queries.append(q)
    p4_queries = cq_mod.clean_query(p4_queries, max_queries=max_p4)
    det = deterministic_backup_queries(input_text, max_queries=8)
    for q in det:
        if q not in seen_q and len(p4_queries) < max_p4:
            seen_q.add(q)
            p4_queries.append(q)
    p4_batch = run_plane("P4", "broad", p4_queries)
    if p4_batch:
        all_articles = merge_and_dedupe_articles(all_articles, p4_batch)
        if not best_plane:
            best_plane = "P4"
    passed, conf, gate_meta = passes_retrieval_quality_gate(all_articles, input_text)
    meta["quality_gate"]["P4"] = gate_meta
    if short_circuit and passed:
        meta["retrieval_confidence"] = _confidence_from_best_plane(best_plane, conf)
        return rerank_tiered_articles(all_articles, input_text), meta

    # P5 — gap-fill missing terms
    if "P5" in planes_enabled:
        terms = extract_key_terms(input_text, title)
        corpus = _article_corpus_text(all_articles)
        missing = [t for t in terms if t.lower() not in corpus]
        gap_queries = build_gap_fill_queries(input_text, title, missing)
        p5_batch = run_plane("P5", "gap_fill", gap_queries)
        if p5_batch:
            all_articles = merge_and_dedupe_articles(all_articles, p5_batch)
            if not best_plane:
                best_plane = "P5"

    passed, conf, gate_meta = passes_retrieval_quality_gate(all_articles, input_text)
    meta["quality_gate"]["final"] = gate_meta
    meta["retrieval_confidence"] = _confidence_from_best_plane(best_plane, conf)
    meta["article_count"] = len(all_articles)
    log(
        f"DONE planes={meta['planes_run']} articles={len(all_articles)} "
        f"confidence={meta['retrieval_confidence']}"
    )
    return rerank_tiered_articles(all_articles, input_text), meta


if os.getenv("RATE_LIMIT_CURL_RESILIENCE", "1").lower() in ("1", "true", "yes", "on"):
    try:
        install_rate_limit_curl_resilience()
    except Exception as _rate_res_err:
        logging.warning("Rate-limit curl resilience not installed: %s", _rate_res_err)
