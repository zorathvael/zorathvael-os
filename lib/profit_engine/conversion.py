from __future__ import annotations

from collections import Counter
from typing import Any


def _repo(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    marker = "github.com/"
    if marker not in value:
        return value.lower()
    return value.split(marker, 1)[1].split("?", 1)[0].lower()


def build_conversion_funnel(leads: list[dict[str, Any]], orders: list[dict[str, Any]]) -> dict[str, Any]:
    lead_repositories = {_repo(row.get("repository", "")) for row in leads if row.get("repository")}
    lead_by_repo = Counter(_repo(row.get("repository", "")) for row in leads if row.get("repository"))
    paid = [row for row in orders if row.get("status") in {"paid", "delivered"}]
    attributed = [row for row in paid if _repo(row.get("target_repository", "")) in lead_repositories]
    unattributed = [row for row in paid if _repo(row.get("target_repository", "")) not in lead_repositories]

    revenue_usdt = 0.0
    revenue_idr = 0
    for row in paid:
        amount = float(row.get("amount", 0) or 0)
        if str(row.get("currency", "")).upper() == "USDT":
            revenue_usdt += amount
        elif str(row.get("currency", "")).upper() == "IDR":
            revenue_idr += int(amount)

    return {
        "lead_count": len(leads),
        "unique_lead_repositories": len(lead_by_repo),
        "paid_orders": len(paid),
        "attributed_paid_orders": len(attributed),
        "unattributed_paid_orders": len(unattributed),
        "paid_revenue_orders": len(paid),
        "paid_revenue_usdt": revenue_usdt,
        "paid_revenue_idr": revenue_idr,
    }
