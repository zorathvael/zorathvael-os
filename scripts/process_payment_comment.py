from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from lib.profit_engine.delivery import audit_repository
from lib.profit_engine.ledger import ProfitLedger
from lib.profit_engine.order_flow import find_pending_issue, mark_paid
from lib.profit_engine.payment_verification import PaymentIntent, PaymentVerifier

TX_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{64}\b")


def update_metrics(revenue: float, delivered: bool, path: str = "data/revenue_metrics.json") -> None:
    target = Path(path)
    data = {"qualified_leads": 0, "paid_orders": 0, "delivered_orders": 0, "revenue_usdt": 0.0, "last_updated": None}
    if target.exists():
        try:
            data.update(json.loads(target.read_text(encoding="utf-8")))
        except (ValueError, OSError):
            pass
    data["paid_orders"] = int(data.get("paid_orders", 0)) + 1
    if delivered:
        data["delivered_orders"] = int(data.get("delivered_orders", 0)) + 1
    data["revenue_usdt"] = float(data.get("revenue_usdt", 0.0)) + float(revenue)
    from datetime import datetime, timezone
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", type=int, required=True)
    parser.add_argument("--comment", required=True)
    args = parser.parse_args()

    match = TX_PATTERN.search(args.comment)
    if not match:
        print(json.dumps({"status": "ignored", "reason": "no BSC transaction hash found"}))
        return 0

    order = find_pending_issue(args.issue_number)
    if order is None:
        print(json.dumps({"status": "ignored", "reason": "no pending revenue order for issue"}))
        return 0
    if order.method != "usdt_bep20":
        print(json.dumps({"status": "manual_review", "reason": "QRIS payment requires provider verification"}))
        return 0

    intent = PaymentIntent(
        order_id=order.order_id,
        amount=order.amount,
        currency=order.currency,
        method=order.method,
        destination=order.destination,
        created_at=order.created_at,
        expires_at=order.expires_at,
    )
    result = PaymentVerifier().verify_usdt_tx(intent, match.group(0))
    payload = {
        "status": result.status,
        "verified": result.verified,
        "order_id": result.order_id,
        "amount": str(result.amount),
        "tx_hash": result.tx_hash,
        "reason": result.reason,
        "delivery_path": None,
    }
    if not result.verified:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    ledger = ProfitLedger(os.getenv("ZORATHVAEL_PROFIT_LEDGER", "data/profit_ledger.jsonl"))
    recorded = ledger.record_verified_payment(order_id=order.order_id, tx_hash=match.group(0), revenue=float(result.amount), method=order.method)
    if not recorded:
        payload["status"] = "already_recorded"
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    mark_paid(order.order_id)
    try:
        report = audit_repository(order.target_repository, os.getenv("GITHUB_TOKEN", ""), order.product_id)
        delivered = True
    except Exception as exc:
        report = "# Delivery pending\n\nPayment was verified and recorded. Automatic analysis failed with " + type(exc).__name__ + "; the paid order can be retried."
        delivered = False

    delivery_path = Path(f"data/delivery_{order.order_id}.md")
    delivery_path.write_text(report, encoding="utf-8")
    update_metrics(float(result.amount), delivered)
    payload["delivery_path"] = str(delivery_path)
    payload["recorded"] = True
    payload["delivered"] = delivered
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
