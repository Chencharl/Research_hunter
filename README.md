# Research Hunter

Research Hunter automates the tedious first step of a literature review: **finding papers, filtering noise, and prioritizing what to read next**.

## Why use this?
When you search manually, you tend to:
- run the same queries repeatedly across sessions
- lose track of what you already skimmed
- get overwhelmed by volume and miss the highest-impact items

Research Hunter helps by producing a ranked, exportable shortlist so you can spend time reading—not wrangling search results.

## What does it search?
Right now, Research Hunter uses the **Semantic Scholar Graph API**, which indexes millions of papers across disciplines.

## What is the effect?
Research Hunter doesn’t just *retrieve* papers—it **scores and ranks** them using a transparent 0–100 rubric:
- **Relevance** (keyword matches)
- **Impact** (citations)
- **Recency** (publication year)

Outputs are written to:
- `outputs/results.csv`
- `outputs/results.json`

## Install
Requires **Python 3.10+**.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Configuration
Create a `.env` file (see `.env.example`).

Optional but recommended:
- `SEMANTIC_SCHOLAR_API_KEY` to increase rate limits

If you hit HTTP 429 (rate limit), add the key and retry.

More details: `docs/api_setup.md`.

## Quick comparison

| Feature | Standard search engines | Research Hunter |
|---|---|---|
| Transparent, adjustable scoring | ❌ | ✅ (documented + configurable) |
| Relevance + impact + recency ranking | Mixed / implicit | ✅ (explicit 0–100 rubric) |
| Export clean CSV/JSON | Sometimes | ✅ |
| Offline corpus analysis (no API calls) | ❌ | ✅ (`analyze` mode) |
| Reproducible runs (config-driven) | ❌ | ✅ |

## Pipeline (high level)

```mermaid
flowchart LR
  A[Data Input\n(online search or local JSON)] --> B[Scoring Engine\nRelevance + Impact + Recency]
  B --> C[Ranked Output\nCSV + JSON]
```

## Usage
Search for papers and export results:

```bash
research-hunter search \
  --query "emotion regulation ecological momentary assessment" \
  --limit 25 \
  --outdir outputs
```

Offline scoring of a local corpus (recommended for reproducible workflows):

```bash
research-hunter analyze \
  --input samples/sample_corpus.json \
  --output outputs/results.csv \
  --config configs/scoring_config.example.json
```

## Output format
See `samples/` for example CSV/JSON outputs.

## Docs
- `docs/architecture.md`
- `docs/scoring_methodology.md`
- `docs/api_setup.md`

## How to cite
A `CITATION.cff` is provided for GitHub/Zenodo-friendly citation metadata.

If you use Research Hunter in academic work, cite the software repository (and include the version/tag you used).

## Contributing
Issues and PRs are welcome. Keep changes:
- reproducible
- transparent (document scoring changes)
- free of secrets (never commit `.env`)

## License
MIT (see `LICENSE`).
