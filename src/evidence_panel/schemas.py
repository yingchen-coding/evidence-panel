"""Typed records for the evidence panel. No I/O, no network — just the data contract."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Paper:
    """One paper in the public corpus. `authors` is an ordered author list."""
    paper_id: str
    title: str
    year: int
    authors: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.paper_id or not self.title:
            raise ValueError("paper_id and title are required")
        if not self.authors:
            raise ValueError(f"{self.paper_id}: at least one author required")


@dataclass(frozen=True)
class AuthorLens:
    """An author used ONLY as a paper-method lens — never a simulated person.

    `supporting_paper_ids` grounds every lens in real papers; a lens with no papers is invalid.
    """
    name: str
    paper_count: int
    supporting_paper_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.paper_count != len(self.supporting_paper_ids):
            raise ValueError(f"{self.name}: paper_count must equal len(supporting_paper_ids)")


@dataclass
class IdeaSeed:
    """A generated research idea. Always PROPOSED EXPERIMENT until independently run."""
    title: str
    lenses: tuple[str, ...]
    source_paper_ids: tuple[str, ...]
    falsifiable_claim: str
    smallest_test: str
    failure_condition: str
    preserved_dissent: str
    status: str = "PROPOSED EXPERIMENT"

    def validate(self) -> None:
        if len(self.lenses) < 2:
            raise ValueError(f"{self.title!r}: a coalition needs >=2 lenses")
        for name, val in (("falsifiable_claim", self.falsifiable_claim),
                          ("smallest_test", self.smallest_test),
                          ("failure_condition", self.failure_condition),
                          ("preserved_dissent", self.preserved_dissent)):
            if not val.strip():
                raise ValueError(f"{self.title!r}: {name} is required")
        if not self.source_paper_ids:
            raise ValueError(f"{self.title!r}: at least one source paper id required")
        if self.status != "PROPOSED EXPERIMENT":
            raise ValueError("generated ideas must stay PROPOSED EXPERIMENT until run")


@dataclass
class BudgetLimits:
    max_model_calls: int = 4
    max_seconds: float = 900.0
    max_output_chars: int = 20000
    calls_made: int = field(default=0)
