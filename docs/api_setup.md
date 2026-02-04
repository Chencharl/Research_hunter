# API Setup

Research Hunter currently supports the **Semantic Scholar Graph API**.

## Semantic Scholar
- Docs: https://api.semanticscholar.org/api-docs/
- API key (optional but recommended for higher rate limits):
  - Obtain a key following Semantic Scholar's instructions.
  - Put it in your `.env` file as:

```bash
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

### Common errors
- **HTTP 429 (rate limit)**: add `SEMANTIC_SCHOLAR_API_KEY` and retry later.

## Notes
Research Hunter is designed to run with *minimal* dependencies and to degrade gracefully if an API key is not provided.
