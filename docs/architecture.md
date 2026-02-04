# Architecture

Research Hunter is organized as a small set of modules with clear responsibilities:

1. **Searcher (online)**
   - `research_hunter/clients/semantic_scholar.py`
   - Talks to the Semantic Scholar Graph API.
   - Returns paper metadata (title/abstract/year/venue/url/citations).

2. **Scorer (deterministic, offline-friendly)**
   - `research_hunter/scoring.py`
   - Produces a transparent score breakdown:
     - relevance (keyword matches)
     - impact (citations bucket)
     - recency (publication year)

3. **Exporter**
   - `research_hunter/cli.py`
   - Writes `results.csv` and `results.json`.

4. **Offline corpus analyzer (no network calls)**
   - `research_hunter/offline_analyzer.py`
   - Scores a local JSON corpus and exports a CSV.

The CLI is intentionally thin: it wires modules together and handles file I/O.
