"""End-to-end tests for the evidence-panel engine. Offline, deterministic, no network."""
import json
from pathlib import Path

import pytest

from evidence_panel import (
    AuthorLens,
    BudgetExceeded,
    BudgetGuard,
    BudgetLimits,
    IdeaSeed,
    author_frequencies,
    brainstorm,
    load_corpus,
    parse_ideas,
    top_lenses,
)

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "openai_safety_2021_2024"


def test_corpus_loads_and_counts():
    papers = load_corpus(EXAMPLE / "corpus.json")
    assert len(papers) == 8
    freq = author_frequencies(papers)
    # Leike and Wu each co-authored 4 of the 8 public papers.
    assert freq["Leike"] == 4
    assert freq["Wu"] == 4


def test_duplicate_paper_id_is_rejected(tmp_path):
    bad = tmp_path / "dupe.json"
    bad.write_text(json.dumps([
        {"paper_id": "x", "title": "A", "year": 2020, "authors": ["P"]},
        {"paper_id": "x", "title": "B", "year": 2021, "authors": ["Q"]},
    ]))
    with pytest.raises(ValueError, match="duplicate paper_id"):
        load_corpus(bad)


def test_ranking_matches_expected_fixture():
    """top_lenses must reproduce the committed expected_top10.json exactly and deterministically."""
    papers = load_corpus(EXAMPLE / "corpus.json")
    lenses, cutoff_tie = top_lenses(papers, n=10)
    expected = json.loads((EXAMPLE / "expected_top10.json").read_text())
    got = [
        {"name": l.name, "paper_count": l.paper_count,
         "supporting_paper_ids": list(l.supporting_paper_ids)}
        for l in lenses
    ]
    assert got == expected["top_authors"]
    assert cutoff_tie == expected["cutoff_tie"]


def test_author_lens_requires_matching_paper_ids():
    with pytest.raises(ValueError, match="paper_count must equal"):
        AuthorLens(name="X", paper_count=3, supporting_paper_ids=("p1",))


def test_budget_guard_caps_model_calls():
    guard = BudgetGuard(BudgetLimits(max_model_calls=2))
    guard.register_call()
    guard.register_call()
    with pytest.raises(BudgetExceeded, match="model calls"):
        guard.register_call()


def test_budget_guard_clamps_output():
    guard = BudgetGuard(BudgetLimits(max_output_chars=5))
    assert guard.clamp_output("0123456789") == "01234"


def test_idea_seed_requires_two_lenses():
    seed = IdeaSeed(
        title="single-lens idea", lenses=("A",), source_paper_ids=("p1",),
        falsifiable_claim="c", smallest_test="t", failure_condition="f",
        preserved_dissent="d",
    )
    with pytest.raises(ValueError, match=">=2 lenses"):
        seed.validate()


def test_parse_ideas_drops_malformed_and_single_lens():
    text = (
        "TITLE: good idea\nLENSES: A, B\nSOURCES: p1, p2\nCLAIM: x compounds\n"
        "TEST: run 30 cases\nFAILURE: within noise\nDISSENT: A vs B\n"
        "---\n"
        "TITLE: bad idea\nLENSES: A\nSOURCES: p1\nCLAIM: y\nTEST: z\n"
        "FAILURE: w\nDISSENT: none\n"
    )
    seeds = parse_ideas(text)
    assert len(seeds) == 1
    assert seeds[0].title == "good idea"
    assert seeds[0].status == "PROPOSED EXPERIMENT"


def test_brainstorm_uses_pluggable_model_no_network():
    """The package ships no model; a fake callable proves the wiring and budget enforcement."""
    papers = load_corpus(EXAMPLE / "corpus.json")
    lenses, _ = top_lenses(papers, n=3)

    def fake_model(prompt: str) -> str:
        assert "AUTHOR LENS CARDS" in prompt  # the panel prompt was built
        return (
            "TITLE: reward drift under recursion\nLENSES: Leike, Wu\n"
            "SOURCES: leike2018-reward-modeling, wu2023-recursive\n"
            "CLAIM: error compounds >2x over 3 levels\nTEST: 30 chapters flat vs recursive\n"
            "FAILURE: drift <1.2x\nDISSENT: Wu expects reduction, Leike expects drift\n"
        )

    seeds = brainstorm(lenses, material="new paper abstract", model=fake_model, n=1)
    assert len(seeds) == 1
    assert set(seeds[0].lenses) == {"Leike", "Wu"}
