"""
builders/query_expander.py

Query Expansion pre-processor for the OVI RAG pipeline.

Sits BEFORE the Retriever. Given a raw user query (potentially in Arabic,
with typos, slang, or vague phrasing), it:

  1. Detects the user's language ("en" or "ar")
  2. Normalizes typos / colloquial phrasing
  3. Generates 2-3 clean English search variants optimized for our
     vector index vocabulary (entity_type names and canonical field names)

Uses a fast, cheap Groq model (llama-3.1-8b-instant) — this step adds
~0.3-0.7 s before retrieval, which is acceptable.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Knowledge base vocabulary hint — tells the LLM what categories exist so it
# can generate queries that will actually match our keyword boost map.
# ---------------------------------------------------------------------------
_KB_CATEGORIES = (
    "basic_info, personal_info, certification, project, experience, "
    "education, achievement, benefits"
)

_EXPANSION_SYSTEM_PROMPT = f"""You are a search query optimizer for an AI portfolio assistant.
The knowledge base contains information about Ahmed Ameen, organized into these categories:
{_KB_CATEGORIES}

Your task:
1. Detect the language of the user's question. Return "ar" for Arabic (any dialect), "en" for English.
2. Generate 1 to 3 clean, short English search queries that best capture the user's intent.
   - Queries must use vocabulary that matches the knowledge base categories listed above.
   - Fix typos and slang. Translate Arabic to English.
   - Each query should be 3-8 words. No full sentences.
   - If the user is asking for a list of all items (e.g. "all projects", "all certifications"), include the word "all" and the category name.

CRITICAL JSON FORMAT RULES:
- Return ONLY a valid JSON object. No explanation, no conversational text, no markdown block wrappers.
- You MUST use standard double quotes (") for all keys and string values. Never use single quotes (') as delimiters.
- If a query contains an apostrophe, escape it or use standard double quotes around the query string.

JSON Template:
{{"language": "en" or "ar", "search_queries": ["query1", "query2"]}}

Examples:
- Input: "ايه مشاريع احمد؟" -> {{"language": "ar", "search_queries": ["Ahmed projects portfolio", "projects Ahmed built", "list all projects"]}}
- Input: "What is ahmed experices?" -> {{"language": "en", "search_queries": ["Ahmed work experience", "Ahmed employment history", "experience positions"]}}
- Input: "whar collage ahmed in?" -> {{"language": "en", "search_queries": ["Ahmed university education degree", "Ahmed college faculty"]}}
- Input: "شهاداته ايه؟" -> {{"language": "ar", "search_queries": ["Ahmed certifications", "Ahmed courses completed", "list all certifications"]}}
- Input: "who is ahmed?" -> {{"language": "en", "search_queries": ["who is Ahmed Ameen", "Ahmed biography basic info"]}}
"""


class QueryExpander:
    """
    Pre-processes a raw user query into optimized search variants
    before it reaches the vector retriever.

    On failure (network error, malformed JSON, etc.) it falls back
    gracefully to returning the original query as-is with language="en".
    """

    def __init__(
        self,
        model_name: str = "openai/gpt-oss-20b",
        timeout: float = 8.0,
    ) -> None:
        self.model_name = model_name
        self.timeout = timeout
        self._client: Any = None

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from groq import Groq
        except ImportError as exc:
            raise ImportError(
                "The 'groq' package is not installed. Run: pip install groq"
            ) from exc

        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")

        self._client = Groq(api_key=api_key)
        return self._client

    def expand(self, raw_query: str) -> dict[str, Any]:
        """
        Expand a raw user query into optimized search variants.

        Returns a dict:
        {
            "original":       str,        # the raw input, unchanged
            "language":       "en"|"ar",  # detected language
            "search_queries": list[str]   # 1-3 English search strings
        }

        Never raises - falls back to {"language": "en", "search_queries": [raw_query]}
        on any error.
        """
        fallback = {
            "original": raw_query,
            "language": "en",
            "search_queries": [raw_query],
        }

        try:
            client = self._get_client()
            completion = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": _EXPANSION_SYSTEM_PROMPT},
                    {"role": "user", "content": raw_query},
                ],
                temperature=0.0,
                max_tokens=200,
                stream=False,
            )
            raw_content = completion.choices[0].message.content or ""
            raw_content = raw_content.strip()

            import re

            # Robust extraction of JSON substring between first { and last }
            match = re.search(r"\{.*\}", raw_content, re.DOTALL)
            if match:
                raw_content = match.group(0).strip()

            parsed = None
            try:
                parsed = json.loads(raw_content)
            except json.JSONDecodeError:
                # If standard loading failed, let's try to repair single quotes.
                # Specifically replace single quotes that are used as delimiters:
                # e.g., 'language': 'en' or 'search_queries': ['abc', 'def']
                repaired = raw_content
                # Replace single quotes surrounding dict keys/values, except apostrophes inside words.
                # 1. replace '{ and }'
                repaired = re.sub(r"\'(\s*[\{\}])", r'"\1', repaired)
                repaired = re.sub(r"(([\{\}])\s*)\'", r'\1"', repaired)
                # 2. replace key/value single quotes
                repaired = re.sub(r"\'\s*:\s*\'", '": "', repaired)
                repaired = re.sub(r"\'\s*,\s*\'", '", "', repaired)
                repaired = re.sub(r"\[\s*\'", '["', repaired)
                repaired = re.sub(r"\'\s*\]", '"]', repaired)
                repaired = re.sub(r"\{\s*\'", '{"', repaired)
                repaired = re.sub(r"\'\s*\}", '"}', repaired)
                repaired = re.sub(r"\'\s*:", '":', repaired)
                repaired = re.sub(r":\s*\'", ':"', repaired)
                repaired = re.sub(r",\s*\'", ',"', repaired)
                repaired = re.sub(r"\'\s*,", '",', repaired)
                try:
                    parsed = json.loads(repaired)
                except Exception:
                    # Final fallback: replace ALL single quotes (will break internal apostrophes, but allows loading)
                    try:
                        parsed = json.loads(raw_content.replace("'", '"'))
                    except Exception:
                        pass

            if not parsed:
                raise ValueError("Could not parse JSON response even after repair attempts")

            language = parsed.get("language", "en")
            search_queries = parsed.get("search_queries", [])

            if not isinstance(search_queries, list) or not search_queries:
                raise ValueError("search_queries missing or empty")

            # Sanitize: ensure all queries are non-empty strings
            search_queries = [str(q).strip() for q in search_queries if str(q).strip()]
            if not search_queries:
                raise ValueError("All search_queries were empty after sanitization")

            return {
                "original": raw_query,
                "language": language if language in ("en", "ar") else "en",
                "search_queries": search_queries,
            }

        except Exception as exc:
            logger.warning(
                "QueryExpander failed for %r (%s: %s). Falling back to raw query.",
                raw_query,
                type(exc).__name__,
                exc,
            )
            # Detect Arabic script as a best-effort fallback for language detection
            has_arabic = any("\u0600" <= ch <= "\u06ff" for ch in raw_query)
            fallback["language"] = "ar" if has_arabic else "en"
            return fallback
