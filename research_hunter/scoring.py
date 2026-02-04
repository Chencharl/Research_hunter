from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class Score:
    value: int
    note: str


DEFAULT_KEYWORDS: Dict[str, int] = {
    # Higher weights for multi-word, specific concepts
    "emotion regulation": 20,
    "affective computing": 20,
    "ecological momentary assessment": 18,
    "experience sampling": 16,
    "digital mental health": 18,
    # Medium
    "resilience": 12,
    "mental health": 12,
    "wearable": 10,
    "multimodal": 10,
    # Low / generic
    "emotion": 4,
}


def score_text(text: str, keywords: Dict[str, int] | None = None) -> Score:
    """Deterministic keyword scoring.

    Score is the sum of weights for unique keywords present.
    """
    t = (text or "").lower()
    kws = keywords or DEFAULT_KEYWORDS

    hits: List[Tuple[str, int]] = []
    total = 0
    for kw, w in kws.items():
        if kw in t:
            total += int(w)
            hits.append((kw, int(w)))

    # cap 0..100
    total = max(0, min(100, total))

    hits.sort(key=lambda x: (-x[1], x[0]))
    note = "hits: " + ", ".join(k for k, _ in hits[:6]) if hits else ""
    return Score(value=total, note=note)
