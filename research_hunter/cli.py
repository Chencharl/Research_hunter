from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from research_hunter.clients.semantic_scholar import search_papers
from research_hunter.scoring import score_text


def _write_outputs(outdir: Path, rows: list[dict]) -> None:
    outdir.mkdir(parents=True, exist_ok=True)

    (outdir / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # lightweight CSV
    import csv

    cols = ["score", "year", "title", "venue", "url", "score_note"]
    with (outdir / "results.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def cmd_search(args: argparse.Namespace) -> int:
    papers = search_papers(query=args.query, limit=args.limit)

    rows: list[dict] = []
    for p in papers:
        text = "\n".join([p.get("title") or "", p.get("abstract") or "", p.get("venue") or ""])
        sc = score_text(text)
        rows.append(
            {
                "score": sc.value,
                "score_note": sc.note,
                "year": p.get("year") or "",
                "title": p.get("title") or "",
                "venue": p.get("venue") or "",
                "url": p.get("url") or "",
            }
        )

    rows.sort(key=lambda r: (r.get("score", 0), r.get("year") or 0), reverse=True)
    _write_outputs(Path(args.outdir), rows)
    print(f"[OK] wrote outputs to: {args.outdir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-hunter")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Search papers and export ranked results")
    s.add_argument("--query", required=True)
    s.add_argument("--limit", type=int, default=25)
    s.add_argument("--outdir", default="outputs")
    s.set_defaults(func=cmd_search)

    return p


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
