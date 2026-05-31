"""
Elasticsearch MCP Server for Academic Commander.

Provides tools to index parsed PDF content, run semantic searches over
academic documents, extract deadline dates from raw text, and aggregate
curriculum topics from the ``academic_documents`` index.

Environment variables
---------------------
ELASTIC_URL : str
    Elasticsearch cluster URL (e.g. ``https://my-cluster.es.us-east-1.aws.found.io:9243``).
ELASTIC_API_KEY : str
    Base-64 encoded Elasticsearch API key for authentication.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from mcp.server.fastmcp import FastMCP

load_dotenv()

ELASTIC_URL: str = os.getenv("ELASTIC_URL", "")
ELASTIC_API_KEY: str = os.getenv("ELASTIC_API_KEY", "")
INDEX_NAME: str = "academic_documents"

mcp = FastMCP("Elasticsearch MCP – Academic Commander")

# ---------------------------------------------------------------------------
# Helper: lazy Elasticsearch client
# ---------------------------------------------------------------------------
_es_client: Elasticsearch | None = None


def _get_es() -> Elasticsearch:
    """Return a reusable Elasticsearch client, created on first call."""
    global _es_client
    if _es_client is None:
        if not ELASTIC_URL:
            raise RuntimeError("ELASTIC_URL environment variable is not set.")
        if not ELASTIC_API_KEY:
            raise RuntimeError("ELASTIC_API_KEY environment variable is not set.")
        _es_client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY)
    return _es_client


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def index_document(
    doc_id: str,
    title: str,
    content: str,
    doc_type: str,
) -> dict[str, Any]:
    """Index a parsed PDF document into the ``academic_documents`` index.

    Parameters
    ----------
    doc_id : str
        A unique identifier for the document (e.g. a hash of the filename).
    title : str
        Human-readable document title.
    content : str
        Full extracted text content of the document.
    doc_type : str
        Category label such as ``syllabus``, ``lecture_notes``, ``exam_paper``.

    Returns
    -------
    dict
        Elasticsearch indexing result with ``_id`` and ``result`` fields.
    """
    try:
        es = _get_es()
        body = {
            "title": title,
            "content": content,
            "doc_type": doc_type,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
        }
        result = es.index(index=INDEX_NAME, id=doc_id, document=body)
        return {
            "doc_id": result["_id"],
            "result": result["result"],
            "index": INDEX_NAME,
        }
    except Exception as exc:
        return {"error": f"Failed to index document: {exc}"}


@mcp.tool()
def semantic_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """Search over indexed academic documents using a multi-match query.

    The query runs against both the ``title`` and ``content`` fields with
    Elasticsearch's built-in BM25 ranking.

    Parameters
    ----------
    query : str
        Natural-language search query.
    top_k : int, optional
        Maximum number of results to return (default ``5``).

    Returns
    -------
    dict
        A list of matching documents with scores.
    """
    try:
        es = _get_es()
        body = {
            "size": top_k,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^2", "content"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            },
            "_source": ["title", "doc_type", "indexed_at"],
            "highlight": {
                "fields": {"content": {"fragment_size": 200, "number_of_fragments": 2}}
            },
        }
        resp = es.search(index=INDEX_NAME, body=body)
        hits = []
        for hit in resp["hits"]["hits"]:
            entry: dict[str, Any] = {
                "doc_id": hit["_id"],
                "score": hit["_score"],
                **hit["_source"],
            }
            if "highlight" in hit:
                entry["snippets"] = hit["highlight"].get("content", [])
            hits.append(entry)
        return {"query": query, "total": resp["hits"]["total"]["value"], "results": hits}
    except Exception as exc:
        return {"error": f"Semantic search failed: {exc}"}


@mcp.tool()
def extract_deadlines(content: str) -> dict[str, Any]:
    """Parse dates and exam windows from raw text using regex patterns.

    Recognises the following formats:
    * ``June 11``, ``June 11, 2026``
    * ``MM/DD/YYYY``, ``DD-MM-YYYY``, ``YYYY-MM-DD``
    * Keywords: *exam*, *deadline*, *submission*, *midterm*, *final*, *due*,
      *quiz*, *test*, *assignment*

    Parameters
    ----------
    content : str
        Raw document text (e.g. from a syllabus PDF).

    Returns
    -------
    dict
        A list of extracted deadline objects, each with ``date``, ``keyword``,
        and ``context`` (surrounding sentence).
    """
    try:
        # Date regex patterns
        date_patterns: list[str] = [
            # Month DD, YYYY  or  Month DD
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
            r"\s+\d{1,2}(?:,?\s*\d{4})?",
            # MM/DD/YYYY
            r"\d{1,2}/\d{1,2}/\d{4}",
            # DD-MM-YYYY
            r"\d{1,2}-\d{1,2}-\d{4}",
            # YYYY-MM-DD
            r"\d{4}-\d{1,2}-\d{1,2}",
        ]

        keywords_pattern = re.compile(
            r"\b(exam|deadline|submission|midterm|final|due|quiz|test|assignment)\b",
            re.IGNORECASE,
        )

        combined_date_re = re.compile("|".join(date_patterns), re.IGNORECASE)

        # Split into sentences (rough)
        sentences = re.split(r"(?<=[.!?])\s+", content)

        deadlines: list[dict[str, Any]] = []
        seen: set[str] = set()

        for sentence in sentences:
            dates_found = combined_date_re.findall(sentence)
            keywords_found = keywords_pattern.findall(sentence)

            if dates_found and keywords_found:
                for date_str in dates_found:
                    key = f"{date_str}|{sentence.strip()[:80]}"
                    if key not in seen:
                        seen.add(key)
                        deadlines.append(
                            {
                                "date": date_str.strip(),
                                "keywords": [kw.lower() for kw in keywords_found],
                                "context": sentence.strip()[:300],
                            }
                        )

        return {"deadlines": deadlines, "count": len(deadlines)}
    except Exception as exc:
        return {"error": f"Failed to extract deadlines: {exc}"}


@mcp.tool()
def get_curriculum_topics() -> dict[str, Any]:
    """Aggregate and return all indexed topic entities.

    Uses an Elasticsearch ``terms`` aggregation on the ``doc_type`` field
    and a ``significant_terms`` aggregation on the ``content`` field to
    surface prominent curriculum topics.

    Returns
    -------
    dict
        Lists of document types and significant content terms.
    """
    try:
        es = _get_es()
        body = {
            "size": 0,
            "aggs": {
                "doc_types": {
                    "terms": {"field": "doc_type.keyword", "size": 50}
                },
                "top_terms": {
                    "significant_terms": {"field": "content", "size": 30}
                },
            },
        }
        resp = es.search(index=INDEX_NAME, body=body)

        doc_types = [
            {"type": bucket["key"], "count": bucket["doc_count"]}
            for bucket in resp["aggregations"]["doc_types"]["buckets"]
        ]
        top_terms = [
            {"term": bucket["key"], "score": bucket["score"], "doc_count": bucket["doc_count"]}
            for bucket in resp["aggregations"]["top_terms"]["buckets"]
        ]

        return {"doc_types": doc_types, "top_terms": top_terms}
    except Exception as exc:
        return {"error": f"Failed to get curriculum topics: {exc}"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
