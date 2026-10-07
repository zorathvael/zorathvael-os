from __future__ import annotations

import json
import os
from pathlib import Path

from .delivery import audit_repository, ci_failure_recovery
from .ledger import ProfitLedger
from .order_flow import RevenueOrder, mark_paid, mark_status
from .payment_verification import PaymentVerifier, PaymentIntent, VerificationResult


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


def deliver_order(order: RevenueOrder, path: str | None = None) -> tuple[bool, str]:
    if order.product_id == "ci_failure_recovery":
        report = ci_failure_recovery(order.target_repository, os.getenv("GITHUB_TOKEN", ""))
    else:
        report = audit_repository(order.target_repository, os.getenv("GITHUB_TOKEN", ""), order.product_id)
    delivery_path = Path(path or f"data/delivery_{order.order_id}.md")
    delivery_path.write_text(report, encoding="utf-8")
    mark_status(order.order_id, "delivered")
    return True, str(delivery_path)


def settle_verified_order(order: RevenueOrder, result: VerificationResult, ledger: ProfitLedger | None = None) -> dict:
    if not result.verified:
        return {"recorded": False, "delivered": False, "delivery_path": None, "status": result.status, "reason": result.reason}

    ledger = ledger or ProfitLedger(os.getenv("ZORATHVAEL_PROFIT_LEDGER", "data/profit_ledger.jsonl"))
    recorded = ledger.record_verified_payment(order_id=order.order_id, tx_hash=result.tx_hash or "", revenue=float(result.amount), method=order.method)
    if not recorded:
        return {"recorded": False, "delivered": False, "delivery_path": None, "status": "already_recorded", "reason": "transaction hash already recorded"}

    mark_paid(order.order_id)
    try:
        delivered, delivery_path = deliver_order(order)
        update_metrics(float(result.amount), delivered)
        return {"recorded": True, "delivered": delivered, "delivery_path": delivery_path, "status": "delivered", "reason": result.reason}
    except Exception as exc:
        mark_status(order.order_id, "delivery_pending")
        report = "# Delivery pending\n\nPayment was verified and recorded, but automatic delivery failed. The order is queued for retry.\n"
        delivery_path = Path(f"data/delivery_{order.order_id}.md")
        delivery_path.write_text(report, encoding="utf-8")
        update_metrics(float(result.amount), False)
        return {"recorded": True, "delivered": False, "delivery_path": str(delivery_path), "status": "delivery_pending", "reason": f"{type(exc).__name__}: {exc}"}


def verify_and_settle(order: RevenueOrder, tx_hash: str, verifier: PaymentVerifier | None = None) -> dict:
    intent = PaymentIntent(order.order_id, order.amount, order.currency, order.method, order.destination, order.created_at, order.expires_at)
    result = (verifier or PaymentVerifier()).verify_usdt_tx(intent, tx_hash)
    settlement = settle_verified_order(order, result)
    return {"verified": result.verified, "order_id": order.order_id, "amount": str(result.amount), "tx_hash": result.tx_hash, "status": settlement["status"], "reason": settlement["reason"], "recorded": settlement["recorded"], "delivered": settlement["delivered"], "delivery_path": settlement["delivery_path"]}
