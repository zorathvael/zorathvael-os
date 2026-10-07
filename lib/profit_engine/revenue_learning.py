from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .outreach import OutreachEvent, load_events


def _load_orders(path: str = "data/revenue_orders.jsonl") -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_learning_snapshot(events: list[OutreachEvent] | None = None, orders: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    events = events if events is not None else load_events()
    orders = orders if orders is not None else _load_orders()
    sent = [e for e in events if e.event_type == "outreach_sent"]
    responses = [e for e in events if e.event_type == "response_observed"]
    paid = [o for o in orders if o.get("status") == "paid"]
    delivered = [o for o in orders if o.get("status") == "delivered"]
    sent_by_offer = Counter(e.offer_id for e in sent)
    response_by_offer = Counter(e.offer_id for e in responses)
    paid_by_product = Counter(o.get("product_id", "") for o in paid)
    stats = {}
    for offer in sorted(set(sent_by_offer) | set(response_by_offer) | set(paid_by_product)):
        s, r, p = sent_by_offer[offer], response_by_offer[offer], paid_by_product[offer]
        stats[offer] = {"outreach_sent": s, "responses_observed": r, "paid_orders": p,
                        "response_rate": round(r / s, 4) if s else 0.0,
                        "payment_rate_per_outreach": round(p / s, 4) if s else 0.0}
    return {
        "outreach_sent": len(sent), "responses_observed": len(responses),
        "paid_orders": len(paid), "delivered_orders": len(delivered),
        "revenue_usdt": round(sum(float(o.get("amount", 0) or 0) for o in paid if str(o.get("currency", "")).upper() == "USDT"), 8),
        "offer_stats": stats,
    }


def write_learning_snapshot(path: str = "data/revenue_learning.json") -> dict[str, Any]:
    snapshot = build_learning_snapshot()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return snapshot
