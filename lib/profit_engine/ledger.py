from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Outcome

class ProfitLedger:
    """Append-only local ledger for measured economic outcomes."""

    def __init__(self, path: str = "data/profit_ledger.jsonl") -> None:
        self.path = Path(path)

    def record(self, outcome: Outcome) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "opportunity": outcome.opportunity,
                "revenue": outcome.revenue,
                "cost": outcome.cost,
                "status": outcome.status,
                "recorded_at": outcome.recorded_at,
                "net_profit": outcome.net_profit,
            }, sort_keys=True) + "\n")

    def summary(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"trades": 0, "wins": 0, "losses": 0, "revenue": 0.0, "cost": 0.0, "net_profit": 0.0, "win_rate": 0.0}
        rows = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        wins = sum(row["status"] == "won" for row in rows)
        losses = sum(row["status"] == "lost" for row in rows)
        revenue = sum(float(row["revenue"]) for row in rows)
        cost = sum(float(row["cost"]) for row in rows)
        return {
            "trades": len(rows),
            "wins": wins,
            "losses": losses,
            "revenue": revenue,
            "cost": cost,
            "net_profit": revenue - cost,
            "win_rate": wins / len(rows) if rows else 0.0,
        }
