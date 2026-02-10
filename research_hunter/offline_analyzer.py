"""Offline corpus analyzer.

This module is a refactored + sanitized version of an internal research
prioritization script. It is designed to run **fully offline** on a local JSON
corpus that you provide.

Use case:
- You already have a harvested set of paper metadata (title/abstract/year/url)
- You want a deterministic, transparent ranking to prioritize reading

No network calls are made.

Input JSON format (list[dict]):
Each item should include at least:
- title (str)
- abstract (str, optional)
- year (int, optional)
- url or doi (str, optional)
- citationCount (int, optional)
- authors (list[str] or list[{name: str}], optional)

Outputs:
- CSV of scored papers
- Optional per-topic bundles (if topic keywords are provided)

All knobs are configurable via a JSON config file; defaults are safe/generic.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None or isinstance(x, bool):
            return None
        return int(x)
    except Exception:
        return None


def _tokenize(text: str) -> str:
    t = _norm(text)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"```.*?```", " ", t, flags=re.DOTALL)
    t = re.sub(r"`[^`]*`", " ", t)
    t = t.replace("/", " ").replace(":", " ").replace(";", " ")
    t = re.sub(r"[\(\)\[\]\{\}\*\_\"“”]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


DEFAULT_CONFIG: Dict[str, Any] = {
    "weights": {
        "relevance_max": 60,
        "impact_max": 20,
        "recency_max": 20,
    },
    "relevance": {
        "points_per_hit": 6,  # unique keyword hits
        "max_unique_hits": 10,
        "stopwords": [
            "and",
            "the",
            "with",
            "from",
            "into",
            "for",
            "to",
            "of",
            "in",
            "on",
            "by",
            "using",
            "based",
            "approach",
            "framework",
            "system",
            "model",
            "data",
        ],
    },
    # Optional: user-provided topical keywords to bias scoring
    "topic_keywords": [
        "emotion regulation",
        "ecological momentary assessment",
        "experience sampling",
        "digital mental health",
        "affective computing",
        "multimodal",
        "wearable",
    ],
    # Optional: author affinity (leave empty by default)
    "preferred_authors": [],
}


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    data = json.loads(path.read_text(encoding="utf-8"))
    # shallow merge
    cfg = dict(DEFAULT_CONFIG)
    for k, v in data.items():
        cfg[k] = v
    return cfg


@dataclass(frozen=True)
class PaperScore:
    score: int
    relevance: int
    impact: int
    recency: int
    reason: str


def _extract_author_names(p: Dict[str, Any]) -> List[str]:
    a = p.get("authors") or []
    out: List[str] = []
    if isinstance(a, list):
        for item in a:
            if isinstance(item, str):
                out.append(item)
            elif isinstance(item, dict) and item.get("name"):
                out.append(str(item.get("name")))
    return [_norm(x) for x in out if _norm(x)]


def _relevance_points(
    text: str,
    keywords: Sequence[str],
    stopwords: Set[str],
    max_hits: int,
    pph: int,
) -> Tuple[int, List[str]]:
    t = _tokenize(text)
    hits: List[str] = []
    for kw in keywords:
        k = _norm(kw)
        if not k:
            continue
        if k in stopwords:
            continue
        if k in t:
            hits.append(k)

    # unique hits only
    uniq = sorted(set(hits))
    uniq = uniq[:max_hits]
    pts = min(max_hits * pph, len(uniq) * pph)
    return int(pts), uniq


def _impact_points(citation_count: Optional[int], max_points: int) -> int:
    """Map citation counts to a capped impact score.

    Uses a log-ish bucket function so 10 vs 100 citations doesn't dominate.
    """
    c = citation_count or 0
    if c <= 0:
        return 0
    if c >= 500:
        return max_points
    if c >= 200:
        return int(max_points * 0.85)
    if c >= 100:
        return int(max_points * 0.7)
    if c >= 50:
        return int(max_points * 0.55)
    if c >= 20:
        return int(max_points * 0.4)
    if c >= 10:
        return int(max_points * 0.25)
    return int(max_points * 0.1)


def _recency_points(year: Optional[int], max_points: int, this_year: int) -> int:
    y = year or 0
    if y <= 0:
        return 0
    # 0..max_points over last 10 years
    age = max(0, this_year - y)
    if age >= 10:
        return 0
    return int(round(max_points * (1 - age / 10)))


def score_paper(p: Dict[str, Any], cfg: Dict[str, Any], this_year: int) -> PaperScore:
    w = cfg.get("weights") or {}
    relevance_max = int(w.get("relevance_max", 60))
    impact_max = int(w.get("impact_max", 20))
    recency_max = int(w.get("recency_max", 20))

    rel_cfg = cfg.get("relevance") or {}
    pph = int(rel_cfg.get("points_per_hit", 6))
    max_hits = int(rel_cfg.get("max_unique_hits", 10))
    stopwords = set(map(_norm, rel_cfg.get("stopwords") or []))

    topic_keywords = list(cfg.get("topic_keywords") or [])

    title = p.get("title") or ""
    abstract = p.get("abstract") or ""
    venue = p.get("venue") or ""
    text = "\n".join([title, abstract, venue])

    relevance_pts, hits = _relevance_points(text, topic_keywords, stopwords, max_hits, pph)
    relevance_pts = min(relevance_max, relevance_pts)

    citations = _safe_int(p.get("citationCount"))
    impact_pts = min(impact_max, _impact_points(citations, impact_max))

    year = _safe_int(p.get("year"))
    recency_pts = min(recency_max, _recency_points(year, recency_max, this_year=this_year))

    total = int(min(100, relevance_pts + impact_pts + recency_pts))

    reason_bits = []
    if hits:
        reason_bits.append("kw=" + ",".join(hits[:6]))
    if citations is not None:
        reason_bits.append(f"citations={citations}")
    if year:
        reason_bits.append(f"year={year}")

    return PaperScore(
        score=total,
        relevance=relevance_pts,
        impact=impact_pts,
        recency=recency_pts,
        reason="; ".join(reason_bits),
    )


def load_papers(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list[dict] (or a dict with key 'data').")
    return [x for x in data if isinstance(x, dict)]


def write_scored_csv(out_path: Path, rows: List[Dict[str, Any]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "score",
        "relevance",
        "impact",
        "recency",
        "year",
        "citationCount",
        "title",
        "venue",
        "url",
        "reason",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def analyze_corpus(
    input_json: Path,
    out_csv: Path,
    cfg_path: Optional[Path] = None,
    this_year: int = 2026,
) -> None:
    cfg = load_config(cfg_path)
    papers = load_papers(input_json)

    scored: List[Dict[str, Any]] = []
    for p in papers:
        sc = score_paper(p, cfg, this_year=this_year)
        scored.append(
            {
                "score": sc.score,
                "relevance": sc.relevance,
                "impact": sc.impact,
                "recency": sc.recency,
                "year": p.get("year") or "",
                "citationCount": p.get("citationCount") or "",
                "title": p.get("title") or "",
                "venue": p.get("venue") or "",
                "url": p.get("url") or p.get("doi") or "",
                "reason": sc.reason,
            }
        )

    scored.sort(key=lambda r: (r.get("score", 0), r.get("year") or 0), reverse=True)
    write_scored_csv(out_csv, scored)
