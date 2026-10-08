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
    customer_email: str = ""
    source: str = "github_issue"
    external_id: str = ""
    tx_hash: str = ""
    updated_at: str = ""


FIELD_PATTERN = re.compile(r"^###\s+([^\n]+)\n\s*([^\n]+)", re.MULTILINE)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TX_HASH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")


def _fields(body: str) -> dict[str, str]:
    return {key.strip().lower(): value.strip() for key, value in FIELD_PATTERN.findall(body or "")}


def parse_order_body(body: str) -> tuple[str, str, str]:
    fields = _fields(body)
    return fields.get("product", ""), fields.get("target repository", ""), fields.get("payment method", "").lower()


def parse_customer_email(body: str) -> str:
    fields = _fields(body)
    value = fields.get("customer email", fields.get("email", "")).strip()
    if value and not EMAIL_PATTERN.match(value):
        raise ValueError("customer email is invalid")
    return value


def validate_tx_hash(value: str) -> str:
    value = value.strip()
    if not TX_HASH_PATTERN.fullmatch(value):
        raise ValueError("BSC transaction hash must be a 0x-prefixed 64-character hexadecimal value")
    return value


def validate_repository_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError("target repository must be a public GitHub URL")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("target repository must use https://github.com/OWNER/REPO")
    return f"https://github.com/{parts[0]}/{parts[1]}"


def build_order(issue_number: int, product_id: str, repository: str, method: str, customer_email: str = "", *, source: str = "github_issue", external_id: str = "", tx_hash: str = "") -> RevenueOrder:
    catalog = offers()
    if product_id not in catalog:
        raise ValueError(f"unknown product: {product_id}")
    repository = validate_repository_url(repository)
    if method not in {"qris", "usdt_bep20"}:
        raise ValueError("payment method must be qris or usdt_bep20")
    if customer_email and not EMAIL_PATTERN.match(customer_email):
        raise ValueError("customer email is invalid")
    if tx_hash:
        tx_hash = validate_tx_hash(tx_hash)
    offer: ProductOffer = catalog[product_id]
    amount = Decimal(str(offer.price_idr if method == "qris" else offer.price_usdt))
    currency = "IDR" if method == "qris" else "USDT"
    now = datetime.now(timezone.utc)
    return RevenueOrder(
        f"ZOR-{uuid.uuid4().hex[:12].upper()}",
        int(issue_number),
        product_id,
        repository,
        amount,
        currency,
        method,
        PaymentRouter.get(method).destination,
        "pending",
        now.isoformat(),
        (now + timedelta(hours=24)).isoformat(),
        customer_email,
        source,
        external_id,
        tx_hash,
        now.isoformat(),
    )


def save_order(order: RevenueOrder, path: str = "data/revenue_orders.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = load_orders(path)
    if any(item.order_id == order.order_id for item in existing):
        return
    if order.external_id and any(item.source == order.source and item.external_id == order.external_id for item in existing):
        return
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
            orders.append(RevenueOrder(
                row["order_id"], int(row["issue_number"]), row["product_id"], row["target_repository"],
                Decimal(str(row["amount"])), row["currency"], row["method"], row["destination"],
                row.get("status", "pending"), row.get("created_at", ""), row.get("expires_at", ""),
                row.get("customer_email", ""),
                row.get("source", "github_issue"),
                row.get("external_id", ""),
                row.get("tx_hash", ""),
                row.get("updated_at", row.get("created_at", "")),
            ))
    return orders


def find_pending_issue(issue_number: int, path: str = "data/revenue_orders.jsonl") -> RevenueOrder | None:
    matches = [item for item in load_orders(path) if item.issue_number == int(issue_number) and item.status == "pending"]
    return matches[-1] if matches else None


def find_order_by_external_id(source: str, external_id: str, path: str = "data/revenue_orders.jsonl") -> RevenueOrder | None:
    matches = [item for item in load_orders(path) if item.source == source and item.external_id == str(external_id)]
    return matches[-1] if matches else None


def find_order_by_tx_hash(tx_hash: str, path: str = "data/revenue_orders.jsonl") -> RevenueOrder | None:
    normalized = tx_hash.lower()
    matches = [item for item in load_orders(path) if item.tx_hash and item.tx_hash.lower() == normalized]
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
            row["updated_at"] = datetime.now(timezone.utc).isoformat()
            changed = True
    if changed:
        target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def attach_tx_hash(order_id: str, tx_hash: str, path: str = "data/revenue_orders.jsonl") -> None:
    tx_hash = validate_tx_hash(tx_hash)
    target = Path(path)
    if not target.exists():
        return
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    changed = False
    now = datetime.now(timezone.utc).isoformat()
    for row in rows:
        if row.get("order_id") == order_id:
            row["tx_hash"] = tx_hash
            row["updated_at"] = now
            changed = True
    if changed:
        target.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def mark_paid(order_id: str, path: str = "data/revenue_orders.jsonl") -> None:
    mark_status(order_id, "paid", path)
