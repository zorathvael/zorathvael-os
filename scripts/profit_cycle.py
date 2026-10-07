from __future__ import annotations

import json
import os

from lib.profit_engine import Opportunity, ProfitEngine, ProfitLedger

def main() -> int:
    # Inputs are intentionally data-driven: no fake revenue is created.
    raw = os.getenv("ZORATHVAEL_OPPORTUNITIES", "[]")
    opportunities = [Opportunity(**item) for item in json.loads(raw)]
    engine = ProfitEngine()
    selected = engine.select(opportunities, limit=int(os.getenv("ZORATHVAEL_MAX_OPPORTUNITIES", "3")))
    ledger = ProfitLedger(os.getenv("ZORATHVAEL_PROFIT_LEDGER", "data/profit_ledger.jsonl"))
    print(json.dumps({"selected": selected, "measured": ledger.summary()}, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
