from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

API_BASE = "https://api.semanticscholar.org/graph/v1"


def search_papers(
    query: str,
    limit: int = 25,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search Semantic Scholar.

    Uses the public Graph API. API key is optional.
    """
    q = (query or "").strip()
    if not q:
        return []

    headers = {}
    key = api_key or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if key:
        headers["x-api-key"] = key

    params = {
        "query": q,
        "limit": int(limit),
        "fields": "title,year,authors,venue,abstract,url,externalIds,citationCount",
    }
    r = requests.get(f"{API_BASE}/paper/search", params=params, headers=headers, timeout=30)

    if r.status_code == 429:
        raise RuntimeError(
            "Semantic Scholar rate limit hit (HTTP 429). "
            "Set SEMANTIC_SCHOLAR_API_KEY in your .env to increase limits, or retry later."
        )

    r.raise_for_status()
    data = r.json()
    return list(data.get("data") or [])
