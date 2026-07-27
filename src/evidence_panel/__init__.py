"""evidence-panel: an evidence-grounded, budget-bounded multi-agent research-ideation engine.

Public papers -> author-frequency cohort -> author-as-method LENSES (never simulated people) ->
independent memos + cross-review -> falsifiable coalition ideas (always PROPOSED EXPERIMENT).
The package ships no model and makes no network call; plug in your own `model(prompt)->str`.
"""
from .budget_guard import BudgetExceeded, BudgetGuard
from .collaboration import brainstorm, build_prompt, parse_ideas
from .corpus import author_frequencies, author_paper_ids, load_corpus
from .ranking import top_lenses
from .schemas import AuthorLens, BudgetLimits, IdeaSeed, Paper

__version__ = "0.1.0"
__all__ = [
    "load_corpus", "author_frequencies", "author_paper_ids", "top_lenses",
    "brainstorm", "build_prompt", "parse_ideas",
    "Paper", "AuthorLens", "IdeaSeed", "BudgetLimits", "BudgetGuard", "BudgetExceeded",
]
