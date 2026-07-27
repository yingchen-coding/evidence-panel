"""The collaboration workflow: lenses -> independent memos -> cross-review -> coalition ideas.

The synthesis step is model-backed and pluggable: pass any callable `model(prompt)->str`. The
package ships NO model and makes NO network call by itself; you wire your own. This keeps the repo
offline, testable, and provider-agnostic. A idea is parsed into an IdeaSeed and validated, so a
malformed or single-lens "idea" is rejected rather than published.
"""
from __future__ import annotations

import re
from typing import Callable

from .budget_guard import BudgetGuard
from .schemas import AuthorLens, BudgetLimits, IdeaSeed

Model = Callable[[str], str]


def build_prompt(lenses: list[AuthorLens], material: str, n: int) -> str:
    cards = "\n".join(
        f"- {l.name} (lens; {l.paper_count} papers: {', '.join(l.supporting_paper_ids)})"
        for l in lenses
    )
    return (
        "Use the author cards below as PAPER-METHOD LENSES ONLY. Never impersonate a living "
        "author, imitate wording, infer private beliefs, or claim an idea belongs to an author. "
        "Produce one independent memo per lens, then two cross-review rounds (method/evaluation, "
        "then adversarial falsification). Preserve >=1 unresolved dissent per final idea. Output "
        f"exactly {n} NEW falsifiable ideas, each backed by a coalition of >=2 lenses and named "
        "paper ids. Format each, separated by a line '---':\n"
        "TITLE: ...\nLENSES: a, b\nSOURCES: id1, id2\nCLAIM: ...\nTEST: ...\n"
        "FAILURE: ...\nDISSENT: ...\n\n"
        f"=== AUTHOR LENS CARDS ===\n{cards}\n\n=== MATERIAL ===\n{material}"
    )


def _field(block: str, label: str) -> str:
    m = re.search(rf"^{label}:\s*(.+)", block, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_ideas(text: str) -> list[IdeaSeed]:
    seeds: list[IdeaSeed] = []
    for block in text.split("---"):
        title = _field(block, "TITLE")
        if not title:
            continue
        seed = IdeaSeed(
            title=title,
            lenses=tuple(x.strip() for x in _field(block, "LENSES").split(",") if x.strip()),
            source_paper_ids=tuple(x.strip() for x in _field(block, "SOURCES").split(",") if x.strip()),
            falsifiable_claim=_field(block, "CLAIM"),
            smallest_test=_field(block, "TEST"),
            failure_condition=_field(block, "FAILURE"),
            preserved_dissent=_field(block, "DISSENT"),
        )
        try:
            seed.validate()
        except ValueError:
            continue  # drop malformed / single-lens ideas rather than emit them
        seeds.append(seed)
    return seeds


def brainstorm(lenses: list[AuthorLens], material: str, model: Model, n: int = 5,
               limits: BudgetLimits | None = None) -> list[IdeaSeed]:
    guard = BudgetGuard(limits)
    guard.register_call()
    raw = guard.clamp_output(model(build_prompt(lenses, material, n)))
    return parse_ideas(raw)
