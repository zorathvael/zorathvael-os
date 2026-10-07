from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .models import Opportunity

class ProfitEngine:
    """Selects economically viable work instead of generating decorative reports."""

    def rank(self, opportunities: Iterable[Opportunity]) -> list[Opportunity]:
        viable = [item for item in opportunities if item.expected_profit > 0 and item.cost >= 0 and item.effort_minutes > 0]
        return sorted(viable, key=lambda item: (item.score, item.expected_profit), reverse=True)

    def select(self, opportunities: Iterable[Opportunity], limit: int = 3) -> list[dict]:
        if limit <= 0:
            return []
        return [asdict(item) | {
            "expected_profit": item.expected_profit,
            "profit_per_hour": item.profit_per_hour,
            "score": item.score,
        } for item in self.rank(opportunities)[:limit]]
