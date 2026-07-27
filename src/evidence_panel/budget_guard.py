"""Hard caps on model calls, wall-clock, and output size — so a panel can't run away."""
from __future__ import annotations

import time

from .schemas import BudgetLimits


class BudgetExceeded(RuntimeError):
    pass


class BudgetGuard:
    def __init__(self, limits: BudgetLimits | None = None):
        self.limits = limits or BudgetLimits()
        self._start = time.monotonic()

    def elapsed(self) -> float:
        return time.monotonic() - self._start

    def check_time(self) -> None:
        if self.elapsed() > self.limits.max_seconds:
            raise BudgetExceeded(f"exceeded {self.limits.max_seconds}s")

    def register_call(self) -> None:
        self.limits.calls_made += 1
        if self.limits.calls_made > self.limits.max_model_calls:
            raise BudgetExceeded(
                f"exceeded {self.limits.max_model_calls} model calls")
        self.check_time()

    def clamp_output(self, text: str) -> str:
        if len(text) > self.limits.max_output_chars:
            return text[: self.limits.max_output_chars]
        return text
