# evidence-panel

An evidence-grounded, budget-bounded engine for **research ideation from a paper corpus**. Give it
a set of papers; it ranks the recurring authors into **paper-method lenses**, has those lenses
cross-review each other, and emits **falsifiable proposed experiments** — each backed by a coalition
of at least two lenses and named source papers.

It ships **no model and makes no network call**. You plug in your own `model(prompt) -> str`, so the
package stays offline, deterministic where it can be, and provider-agnostic.

## Why lenses, not personas

An author here is a **method lens over their cited papers** — never a simulation of the real person.
The engine attributes methods at the corpus level, never claims to know what an author believes, and
never imitates anyone's writing. Byline frequency only selects which papers' methods to study.

## What it does

1. **Rank** — count papers per author, take the top *N* as lenses, and disclose any tie at the
   cutoff so the selection is never silently arbitrary (`top_lenses`).
2. **Prompt** — build a single panel prompt instructing independent memos, two cross-review rounds,
   and preserved dissent (`build_prompt`).
3. **Parse & validate** — turn the model's output into `IdeaSeed`s, dropping any idea that isn't a
   ≥2-lens coalition with a falsifiable claim, smallest test, failure condition, and dissent
   (`parse_ideas`). Every idea stays labeled `PROPOSED EXPERIMENT` until independently run.
4. **Bound** — a `BudgetGuard` caps model calls, wall-clock, and output size so a panel can't run
   away.

## Install

```bash
pip install -e ".[test]"
```

Zero runtime dependencies (Python 3.9+). Only the tests need `pytest`.

## Quick start

```python
from evidence_panel import load_corpus, top_lenses, brainstorm

papers = load_corpus("examples/openai_safety_2021_2024/corpus.json")
lenses, cutoff_tie = top_lenses(papers, n=10)

def my_model(prompt: str) -> str:
    ...  # call whatever LLM you want; the package bundles none

seeds = brainstorm(lenses, material="abstract of a new paper", model=my_model, n=5)
for s in seeds:
    print(s.title, "<-", s.lenses)   # each is a PROPOSED EXPERIMENT
```

## Example fixture

`examples/openai_safety_2021_2024/` contains 8 **public** OpenAI-safety papers (RLHF-from-preferences,
reward modeling, summarize-from-feedback, InstructGPT, weak-to-strong, recursive summarization, …)
and the ranking they deterministically produce (`expected_top10.json`). The test suite reproduces
that ranking exactly.

## Scope

This is a **method**: structure, ranking, validation, and budget bounds for turning a paper corpus
into falsifiable experiment proposals. It does not claim any specific generated idea is novel or
correct — an `IdeaSeed` is a hypothesis to test, not a result. Verifying an idea (running the
experiment, independent evaluation, prior-art search) is out of scope and left to the caller.

## Tests

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
