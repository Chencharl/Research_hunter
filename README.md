# Research Hunter

Automate the most painful parts of literature review: **finding**, **triaging**, and **exporting** relevant papers.

## Why this exists
Manual literature searches are slow and inconsistent:
- you repeat the same searches across multiple sources
- you lose track of what you saw and why it mattered
- exporting to a spreadsheet / bib manager is tedious

Research Hunter is a small, scriptable CLI that pulls results from open APIs, assigns a transparent relevance score, and exports clean CSV/JSON for further work.

## What it does
- Search Semantic Scholar (public API)
- Rank results with a transparent keyword rubric
- Export to `outputs/results.csv` and `outputs/results.json`

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

Optional:
- `SEMANTIC_SCHOLAR_API_KEY` to increase rate limits (recommended)

If you hit HTTP 429 (rate limit), add the key and retry.

## Usage
Search for papers and export results:

```bash
research-hunter search \
  --query "emotion regulation ecological momentary assessment" \
  --limit 25 \
  --outdir outputs
```

## Output format
See `samples/` for example CSV/JSON outputs.

## How to cite
A `CITATION.cff` is provided. If you use Research Hunter in academic work, cite the software repository.

## Contributing
Issues and PRs are welcome. Keep changes:
- reproducible
- transparent (document scoring changes)
- free of secrets (never commit `.env`)

## License
MIT (see `LICENSE`).
