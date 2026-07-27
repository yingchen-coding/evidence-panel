"""Load a public paper manifest and compute author frequencies. Deterministic, offline."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .schemas import Paper


def load_corpus(path: str | Path) -> list[Paper]:
    """Read a JSON manifest: [{"paper_id","title","year","authors":[...]}]."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("corpus manifest must be a JSON list of papers")
    papers = [
        Paper(
            paper_id=str(p["paper_id"]),
            title=str(p["title"]),
            year=int(p["year"]),
            authors=tuple(str(a) for a in p["authors"]),
        )
        for p in data
    ]
    ids = [p.paper_id for p in papers]
    dupes = [pid for pid, n in Counter(ids).items() if n > 1]
    if dupes:
        raise ValueError(f"duplicate paper_id(s): {dupes}")
    return papers


def author_frequencies(papers: list[Paper]) -> Counter:
    """Count papers per author (any authorship position)."""
    freq: Counter = Counter()
    for p in papers:
        for author in set(p.authors):  # a paper counts once per distinct author
            freq[author] += 1
    return freq


def author_paper_ids(papers: list[Paper]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in papers:
        for author in set(p.authors):
            out.setdefault(author, []).append(p.paper_id)
    return out
