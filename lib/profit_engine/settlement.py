from __future__ import annotations

import json
import os
from pathlib import Path

from .delivery import audit_repository, ci_failure_recovery
from .ledger import ProfitLedger
from .order_flow import RevenueOrder, mark_paid
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


def settle_verified_order(order: RevenueOrder, result: VerificationResult, ledger: ProfitLedger | None = None) -> dict:
    if not result.verified:
        return {"recorded": False, "delivered": False, "delivery_path": None, "status": result.status, "reason": result.reason}

    ledger = ledger or ProfitLedger(os.getenv("ZORATHVAEL_PROFIT_LEDGER", "data/profit_ledger.jsonl"))
    recorded = ledger.record_verified_payment(
        order_id=order.order_id,
        tx_hash=result.tx_hash or "",
        revenue=float(result.amount),
        method=order.method,
    )
    if not recorded:
        return {"recorded": False, "delivered": False, "delivery_path": None, "status": "already_recorded", "reason": "transaction hash already recorded"}

    mark_paid(order.order_id)

    try:
        if order.product_id == "ci_failure_recovery":
            report = ci_failure_recovery(order.target_repository, os.getenv("GITHUB_TOKEN", ""))
        else:
            report = audit_repository(order.target_repository, os.getenv("GITHUB_TOKEN", ""), order.product_id)
        delivered = True
    except Exception as exc:
        report = (
            "# Delivery pending\n\n"
            "Payment was verified and recorded, but automatic analysis failed with "
            f"{type(exc).__name__}. The paid order remains recorded and is eligible for retry."
        )
        delivered = False

    delivery_path = Path(f"data/delivery_{order.order_id}.md")
    delivery_path.write_text(report, encoding="utf-8")
    update_metrics(float(result.amount), delivered)
    return {
        "recorded": True,
        "delivered": delivered,
        "delivery_path": str(delivery_path),
        "status": "delivered" if delivered else "delivery_pending",
        "reason": result.reason,
    }


def verify_and_settle(order: RevenueOrder, tx_hash: str, verifier: PaymentVerifier | None = None) -> dict:
    intent = PaymentIntent(
        order_id=order.order_id,
        amount=order.amount,
        currency=order.currency,
        method=order.method,
        destination=order.destination,
        created_at=order.created_at,
        expires_at=order.expires_at,
    )
    result = (verifier or PaymentVerifier()).verify_usdt_tx(intent, tx_hash)
    settlement = settle_verified_order(order, result)
    return {
        "verified": result.verified,
        "order_id": order.order_id,
        "amount": str(result.amount),
        "tx_hash": result.tx_hash,
        "status": settlement["status"],
        "reason": settlement["reason"],
        "recorded": settlement["recorded"],
        "delivered": settlement["delivered"],
        "delivery_path": settlement["delivery_path"],
    }
