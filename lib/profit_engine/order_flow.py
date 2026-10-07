from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from .payments import PaymentRouter
from .revenue import ProductOffer, offers


@dataclass(frozen=True)
class RevenueOrder:
    order_id: str
    issue_number: int
    product_id: str
    target_repository: str
    amount: Decimal
    currency: str
    method: str
    destination: str
    status: str
    created_at: str
    expires_at: str


FIELD_PATTERN = re.compile(r"^###\s+([^\n]+)\n\s*([^\n]+)", re.MULTILINE)


def parse_order_body(body: str) -> tuple[str, str, str]:
    fields = {key.strip().lower(): value.strip() for key, value in FIELD_PATTERN.findall(body or "")}
    return fields.get("product", ""), fields.get("target repository", ""), fields.get("payment method", "").lower()


def validate_repository_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError("target repository must be a public GitHub URL")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("target repository must use https://github.com/OWNER/REPO")
    return f"https://github.com/{parts[0]}/{parts[1]}"


def build_order(issue_number: int, product_id: str, repository: str, method: str) -> RevenueOrder:
    catalog = offers()
    if product_id not in catalog:
        raise ValueError(f"unknown product: {product_id}")
    repository = validate_repository_url(repository)
    if method not in {"qris", "usdt_bep20"}:
        raise ValueError("payment method must be qris or usdt_bep20")
    offer: ProductOffer = catalog[product_id]
    amount = Decimal(str(offer.price_idr if method == "qris" else offer.price_usdt))
    currency = "IDR" if method == "qris" else "USDT"
    now = datetime.now(timezone.utc)
    return RevenueOrder(f"ZOR-{uuid.uuid4().hex[:12].upper()}", int(issue_number), product_id, repository, amount, currency, method, PaymentRouter.get(method).destination, "pending", now.isoformat(), (now + timedelta(hours=24)).isoformat())


def save_order(order: RevenueOrder, path: str = "data/revenue_orders.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(order), default=str, sort_keys=True) + "\n")


def load_orders(path: str = "data/revenue_orders.jsonl") -> list[RevenueOrder]:
    target = Path(path)
    if not target.exists():
        return []
    orders = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            orders.append(RevenueOrder(row["order_id"], int(row["issue_number"]), row["product_id"], row["target_repository"], Decimal(str(row["amount"])), row["currency"], row["method"], row["destination"], row.get("status", "pending"), row.get("created_at", ""), row.get("expires_at", "")))
    return orders


def find_pending_issue(issue_number: int, path: str = "data/revenue_orders.jsonl") -> RevenueOrder | None:
    matches = [item for item in load_orders(path) if item.issue_number == int(issue_number) and item.status == "pending"]
    return matches[-1] if matches else None


def mark_status(order_id: str, status: str, path: str = "data/revenue_orders.jsonl") -> None:
    target = Path(path)
    if not target.exists():
        return
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    changed = False
    for row in rows:
        if row.get("order_id") == order_id:
            row["status"] = status
            changed = True
    if changed:
        target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def mark_paid(order_id: str, path: str = "data/revenue_orders.jsonl") -> None:
    mark_status(order_id, "paid", path)
