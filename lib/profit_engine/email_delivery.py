from __future__ import annotations

import base64
import json
import mimetypes
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentmail import AgentMail

from .order_flow import RevenueOrder, mark_status

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _load_events(path: str = "data/email_delivery.jsonl") -> list[dict[str, Any]]:
    target = Path(path)
    if not target.exists(): return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]

def _append_event(event: dict[str, Any], path: str = "data/email_delivery.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")

def _sent_event(order_id: str) -> dict[str, Any] | None:
    for event in reversed(_load_events()):
        if event.get("order_id") == order_id and event.get("status") == "sent": return event
    return None

def _required_config() -> tuple[str, str]:
    api_key = os.getenv("AGENTMAIL_API_KEY", "").strip()
    inbox_id = os.getenv("AGENTMAIL_INBOX_ID", "").strip()
    if not api_key: raise RuntimeError("AGENTMAIL_API_KEY is not configured")
    if not inbox_id: raise RuntimeError("AGENTMAIL_INBOX_ID is not configured")
    return api_key, inbox_id

def send_delivery_email(order: RevenueOrder, delivery_path: str, *, dry_run: bool = False) -> dict[str, Any]:
    previous = _sent_event(order.order_id)
    if previous: return {"status": "already_sent", "order_id": order.order_id, "message_id": previous.get("message_id")}
    if not order.customer_email: raise RuntimeError(f"customer email is missing for {order.order_id}")
    artifact = Path(delivery_path)
    if not artifact.exists(): raise FileNotFoundError(f"delivery artifact not found: {artifact}")
    filename = artifact.name
    mime_type = mimetypes.guess_type(filename)[0] or "text/markdown"
    attachment = {"filename": filename, "content_type": mime_type, "content": base64.b64encode(artifact.read_bytes()).decode("ascii")}
    subject = f"Zorathvael delivery — {order.product_id} — {order.order_id}"
    text = (f"Hello,\n\nYour payment for order {order.order_id} has been verified and your requested {order.product_id} deliverable is ready.\n\nThe completed report is attached to this email.\n\nZorathvael Core\nAutonomous Delivery")
    if dry_run: return {"status":"dry_run","order_id":order.order_id,"to":order.customer_email,"subject":subject,"attachment":filename,"attachment_bytes":artifact.stat().st_size}
    api_key, inbox_id = _required_config()
    response = AgentMail(api_key=api_key).inboxes.messages.send(inbox_id, to=order.customer_email, subject=subject, text=text, attachments=[attachment], idempotency_key=f"zorathvael-delivery-{order.order_id}")
    event = {"order_id":order.order_id,"issue_number":order.issue_number,"customer_email":order.customer_email,"product_id":order.product_id,"artifact":str(artifact),"status":"sent","message_id":str(getattr(response,"message_id","") or ""),"thread_id":str(getattr(response,"thread_id","") or ""),"sent_at":_now()}
    _append_event(event)
    mark_status(order.order_id, "delivered")
    return event
