"""Rank the top-N authors as method lenses, disclosing any tie at the cutoff."""
from __future__ import annotations

from .corpus import author_frequencies, author_paper_ids
from .schemas import AuthorLens, Paper


def top_lenses(papers: list[Paper], n: int = 10) -> tuple[list[AuthorLens], list[str]]:
    """Return (top-n lenses, cutoff_tie_names).

    Ordering is deterministic: by paper count desc, then author name asc. If authors just below
    the cutoff share the last included author's count, they are surfaced as `cutoff_tie` so the
    selection is never silently arbitrary.
    """
    freq = author_frequencies(papers)
    ids = author_paper_ids(papers)
    ordered = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    if n <= 0:
        return [], []
    top = ordered[:n]
    cutoff_count = top[-1][1] if top else 0
    tie = [name for name, cnt in ordered[n:] if cnt == cutoff_count]
    lenses = [
        AuthorLens(name=name, paper_count=cnt, supporting_paper_ids=tuple(sorted(ids[name])))
        for name, cnt in top
    ]
    return lenses, tie
