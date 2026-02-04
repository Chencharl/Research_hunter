from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class Score:
    """Scoring breakdown used by the public CLI."""

    total: int
    relevance: int
    impact: int
    recency: int
    note: str


DEFAULT_KEYWORDS: Dict[str, int] = {
    # Higher weights for multi-word, specific concepts
    "emotion regulation": 18,
    "affective computing": 18,
    "ecological momentary assessment": 18,
    "experience sampling": 14,
    "digital mental health": 16,
    # Medium
    "resilience": 10,
    "mental health": 10,
    "wearable": 8,
    "multimodal": 8,
    # Low / generic
    "emotion": 3,
}


def _impact_points(citations: int) -> int:
    """0..20 impact points from citation count (bucketed, capped)."""
    c = max(0, int(citations or 0))
    if c >= 500:
        return 20
    if c >= 200:
        return 17
    if c >= 100:
        return 14
    if c >= 50:
        return 11
    if c >= 20:
        return 8
    if c >= 10:
        return 5
    if c >= 1:
        return 2
    return 0


def _recency_points(year: int) -> int:
    """0..20 points, decays linearly over last 10 years."""
    y = int(year or 0)
    if y <= 0:
        return 0
    this_year = date.today().year
    age = max(0, this_year - y)
    if age >= 10:
        return 0
    return int(round(20 * (1 - age / 10)))


def score_text(text: str, keywords: Dict[str, int] | None = None) -> Tuple[int, List[str]]:
    """Return (relevance_points_0_60, hits).

    Relevance points are based on unique keyword hits with weights.
    """
    t = (text or "").lower()
    kws = keywords or DEFAULT_KEYWORDS

    hits: List[Tuple[str, int]] = []
    total = 0
    for kw, w in kws.items():
        if kw in t:
            total += int(w)
            hits.append((kw, int(w)))

    # Normalize to 0..60 by capping and scaling
    total = max(0, min(60, total))
    hits.sort(key=lambda x: (-x[1], x[0]))
    return int(total), [k for k, _ in hits]


def score_paper(paper: Dict[str, Any], keywords: Dict[str, int] | None = None) -> Score:
    """Score a Semantic Scholar-style paper dict.

    Total score (0..100) = relevance (0..60) + impact (0..20) + recency (0..20)
    """
    title = paper.get("title") or ""
    abstract = paper.get("abstract") or ""
    venue = paper.get("venue") or ""
    text = "\n".join([title, abstract, venue])

    relevance, hits = score_text(text, keywords=keywords)

    citations = paper.get("citationCount") or 0
    try:
        citations = int(citations)
    except Exception:
        citations = 0
    impact = _impact_points(citations)

    year = paper.get("year") or 0
    try:
        year = int(year)
    except Exception:
        year = 0
    recency = _recency_points(year)

    total = max(0, min(100, int(relevance + impact + recency)))

    note_bits = []
    if hits:
        note_bits.append("hits: " + ", ".join(hits[:6]))
    if citations:
        note_bits.append(f"citations={citations}")
    if year:
        note_bits.append(f"year={year}")

    return Score(total=total, relevance=relevance, impact=impact, recency=recency, note="; ".join(note_bits))
