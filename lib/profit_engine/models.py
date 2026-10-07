from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

OpportunityType = Literal["product", "service", "affiliate", "market", "automation"]

@dataclass(frozen=True)
class Opportunity:
    name: str
    kind: OpportunityType
    expected_value: float
    cost: float
    probability: float
    effort_minutes: int
    risk: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)

    @property
    def expected_profit(self) -> float:
        return self.expected_value * self.probability - self.cost

    @property
    def profit_per_hour(self) -> float:
        if self.effort_minutes <= 0:
            return 0.0
        return self.expected_profit * 60.0 / self.effort_minutes

    @property
    def score(self) -> float:
        if self.expected_profit <= 0:
            return 0.0
        return max(0.0, self.profit_per_hour * (1.0 - min(max(self.risk, 0.0), 1.0)))

@dataclass(frozen=True)
class Outcome:
    opportunity: str
    revenue: float
    cost: float
    status: Literal["won", "lost", "cancelled"]
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def net_profit(self) -> float:
        return self.revenue - self.cost
