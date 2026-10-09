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
    sent = [e for e in events if e.event_type in {"outreach_sent", "email_outreach_sent"}]
    responses = [e for e in events if e.event_type in {"response_observed", "email_response_observed"}]
    paid = [o for o in orders if o.get("status") in {"paid", "delivered"}]
    delivered = [o for o in orders if o.get("status") == "delivered"]
    sent_by_offer = Counter(e.offer_id for e in sent)
    response_by_offer = Counter(e.offer_id for e in responses)
    paid_by_product = Counter(o.get("product_id", "") for o in paid)
    response_intents_by_offer: dict[str, Counter[str]] = {}
    for event in responses:
        intent = str(event.metadata.get("response_intent", "unclassified"))
        response_intents_by_offer.setdefault(event.offer_id, Counter())[intent] += 1
    stats = {}
    for offer in sorted(set(sent_by_offer) | set(response_by_offer) | set(paid_by_product)):
        s, r, p = sent_by_offer[offer], response_by_offer[offer], paid_by_product[offer]
        intents = response_intents_by_offer.get(offer, Counter())
        positive = intents["positive_interest"] + intents["request_for_details"]
        objections = intents["price_objection"] + intents["fit_objection"] + intents["timing_objection"]
        if p:
            demand_status = "paid_demand_observed"
        elif s < 5:
            demand_status = "insufficient_outreach_sample"
        elif r < 3:
            demand_status = "insufficient_response_sample"
        elif positive >= 2 and positive / r >= 0.30:
            demand_status = "early_interest_signal"
        else:
            demand_status = "interest_not_yet_demonstrated"
        stats[offer] = {
            "outreach_sent": s,
            "responses_observed": r,
            "paid_orders": p,
            "response_rate": round(r / s, 4) if s else 0.0,
            "payment_rate_per_outreach": round(p / s, 4) if s else 0.0,
            "response_intents": dict(intents),
            "positive_interest": positive,
            "objections": objections,
            "not_interested": intents["not_interested"],
            "demand_status": demand_status,
        }
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
