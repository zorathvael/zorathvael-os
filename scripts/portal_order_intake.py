from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any

from lib.profit_engine.email_delivery import send_delivery_email
from lib.profit_engine.order_flow import build_order, find_order_by_external_id, save_order
from lib.profit_engine.payment_verification import PaymentVerifier
from lib.profit_engine.settlement import verify_and_settle

PROJECT_ID = int(os.getenv("ZORATHVAEL_WP_PROJECT_ID", "29784"))
FORM_NAME = os.getenv("ZORATHVAEL_WP_FORM_NAME", "order_portal")
BASE_URL = "https://api.websitepublisher.ai"
TX_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")

SERVICE_MAP = {
    "ci_failure_recovery": "ci_failure_recovery",
    "public_repo_audit": "public_repo_audit",
    "automation_blueprint": "automation_blueprint",
}


def _token() -> str:
    token = os.getenv("WPS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("WPS_TOKEN is not configured")
    return token


def _request(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers={
            "Authorization": f"Bearer {_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"WebsitePublisher API {exc.code}: {detail}") from exc


def get_new_leads() -> list[dict[str, Any]]:
    leads: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = _request(
            f"/iapi/project/{PROJECT_ID}/leads/get-leads",
            {"page": page, "per_page": 100, "status": "new", "form_name": FORM_NAME},
        )
        data = payload.get("data", payload)
        batch = data.get("leads", data.get("results", [])) if isinstance(data, dict) else []
        if not batch:
            break
        leads.extend(batch)
        pagination = data.get("pagination", {}) if isinstance(data, dict) else {}
        if not pagination.get("has_next") and len(batch) < 100:
            break
        page += 1
    return leads


def update_lead(lead_id: int, status: str) -> None:
    _request(
        f"/iapi/project/{PROJECT_ID}/leads/update-status",
        {"lead_id": int(lead_id), "status": status},
    )


def process_lead(lead: dict[str, Any]) -> dict[str, Any]:
    lead_id = int(lead.get("id") or lead.get("lead_id"))
    fields = lead.get("fields") or {}
    service = str(fields.get("service", "")).strip()
    product_id = SERVICE_MAP.get(service)
    if not product_id:
        update_lead(lead_id, "rejected")
        return {"lead_id": lead_id, "status": "rejected", "reason": "unknown service"}

    tx_hash = str(fields.get("tx_hash", "")).strip()
    if not TX_PATTERN.fullmatch(tx_hash):
        return {"lead_id": lead_id, "status": "pending", "reason": "invalid or missing TX hash"}

    existing = find_order_by_external_id("websitepublisher", str(lead_id))
    if existing:
        if existing.status == "delivered":
            update_lead(lead_id, "won")
            return {"lead_id": lead_id, "order_id": existing.order_id, "status": "already_delivered"}
        return {"lead_id": lead_id, "order_id": existing.order_id, "status": existing.status}

    repository = str(fields.get("repository", "")).strip()
    email = str(fields.get("email", "")).strip()
    try:
        order = build_order(
            lead_id,
            product_id,
            repository,
            "usdt_bep20",
            email,
            source="websitepublisher",
            external_id=str(lead_id),
            tx_hash=tx_hash,
        )
    except ValueError as exc:
        update_lead(lead_id, "rejected")
        return {"lead_id": lead_id, "status": "rejected", "reason": str(exc)}

    save_order(order)
    result = verify_and_settle(order, tx_hash, verifier=PaymentVerifier())
    if result["verified"]:
        if result["status"] == "delivery_ready":
            try:
                result["delivery"] = send_delivery_email(order, result["delivery_path"])
            except Exception as exc:
                result["delivery"] = {"status": "queued", "reason": f"{type(exc).__name__}: {exc}"}
        update_lead(lead_id, "won")
    elif result["status"] == "pending":
        # Leave the lead as new; the next cycle retries finality.
        pass
    else:
        update_lead(lead_id, "rejected")
    return {"lead_id": lead_id, "order_id": order.order_id, **result}


def main() -> int:
    leads = get_new_leads()
    results = []
    for lead in leads:
        try:
            results.append(process_lead(lead))
        except Exception as exc:
            results.append({"lead_id": lead.get("id"), "status": "error", "reason": f"{type(exc).__name__}: {exc}"})
    print(json.dumps({
        "project_id": PROJECT_ID,
        "form_name": FORM_NAME,
        "leads_checked": len(leads),
        "results": results,
    }, indent=2, sort_keys=True))
    return 1 if any(item.get("status") == "error" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
