# Scoring Methodology

Research Hunter ranks papers using a **transparent, additive** scoring model.

## Online search scoring (Semantic Scholar results)
Total score is **0–100**:

- **Relevance (0–60)**
  - Deterministic keyword scoring over: title + abstract + venue.
  - Each keyword contributes a weight if present (unique hits).
  - Capped at 60.

- **Impact (0–20)**
  - Based on citation count (bucketed, capped so extreme citation counts don't dominate):
    - 0 → 0
    - 1–9 → 2
    - 10–19 → 5
    - 20–49 → 8
    - 50–99 → 11
    - 100–199 → 14
    - 200–499 → 17
    - 500+ → 20

- **Recency (0–20)**
  - Linear decay across the last 10 years:
    - current year → 20
    - 5 years old → ~10
    - 10+ years old → 0

### Default keyword weights
See `research_hunter/scoring.py` (`DEFAULT_KEYWORDS`). These are meant as sensible starting points; edit them for your domain.

## Offline corpus scoring
The offline analyzer (`research_hunter/offline_analyzer.py`) uses a similar breakdown by default:
- relevance (0–60)
- impact (0–20)
- recency (0–20)

You can override topic keywords and weights with a JSON config.
