from __future__ import annotations

import email
import imaplib
import json
import os
import re
from datetime import datetime, timezone
from email.header import decode_header
from pathlib import Path

from lib.profit_engine.outreach import append_event, load_events, make_event
from lib.profit_engine.customer_demand import classify_customer_response
from lib.profit_engine.revenue import Lead


def load_leads(path: str = "data/revenue_leads.jsonl") -> list[Lead]:
    target = Path(path)
    if not target.exists():
        return []
    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [
        Lead(
            source=row["source"], external_id=str(row["external_id"]), title=row["title"],
            url=row["url"], repository=row["repository"], author=row["author"],
            evidence=tuple(row.get("evidence", [])), score=int(row["score"]),
            offer_id=row["offer_id"], contact_url=row.get("contact_url", ""),
            discovered_at=row.get("discovered_at", ""),
            contact_email=row.get("contact_email"),
            contact_source=row.get("contact_source", "none"),
            problem_context=row.get("problem_context", ""),
        )
        for row in rows
    ]


def _decode(value: str | None) -> str:
    if not value:
        return ""
    parts = []
    for item, encoding in decode_header(value):
        if isinstance(item, bytes):
            parts.append(item.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(item)
    return "".join(parts)


def _text_from_message(message: email.message.Message) -> str:
    if message.is_multipart():
        return "\n".join(
            _text_from_message(part)
            for part in message.walk()
            if part.get_content_type() == "text/plain"
        )
    payload = message.get_payload(decode=True)
    if isinstance(payload, bytes):
        return payload.decode(message.get_content_charset() or "utf-8", errors="replace")
    return str(payload or "")


def main() -> int:
    host = os.getenv("ZORATHVAEL_IMAP_HOST", "").strip()
    username = os.getenv("ZORATHVAEL_IMAP_USERNAME", "").strip()
    password = os.getenv("ZORATHVAEL_IMAP_PASSWORD", "").strip()
    if not all((host, username, password)):
        print("email_response_observer: IMAP transport not configured")
        return 0

    leads = {
        lead.contact_email.lower(): lead
        for lead in load_leads()
        if lead.contact_email
    }
    events = load_events()
    sent = {
        event.lead_url: event
        for event in events
        if event.event_type == "email_outreach_sent"
    }
    observed_ids = {
        str(event.metadata.get("message_id"))
        for event in events
        if event.event_type == "email_response_observed"
    }

    if not sent:
        print("email_response_observer: no email outreach events")
        return 0

    mail = imaplib.IMAP4_SSL(host, int(os.getenv("ZORATHVAEL_IMAP_PORT", "993")))
    try:
        mail.login(username, password)
        mail.select(os.getenv("ZORATHVAEL_IMAP_FOLDER", "INBOX"), readonly=True)
        status, data = mail.uid("search", None, "ALL")
        if status != "OK":
            raise RuntimeError("imap_search_failed")

        observed = 0
        for raw_uid in data[0].split():
            status, msg_data = mail.uid("fetch", raw_uid, "(RFC822)")
            if status != "OK" or not msg_data:
                continue
            raw = next((item[1] for item in msg_data if isinstance(item, tuple)), None)
            if not isinstance(raw, bytes):
                continue
            message = email.message_from_bytes(raw)
            message_id = message.get("Message-ID", "").strip()
            if not message_id or message_id in observed_ids:
                continue

            sender = email.utils.parseaddr(message.get("From", ""))[1].lower()
            lead = leads.get(sender)
            if lead is None or lead.url not in sent:
                continue

            body = _text_from_message(message)
            subject = _decode(message.get("Subject"))
            sent_at = datetime.fromisoformat(sent[lead.url].occurred_at.replace("Z", "+00:00"))
            received_header = email.utils.parsedate_to_datetime(message.get("Date")) if message.get("Date") else None
            received_at = received_header.astimezone(timezone.utc) if received_header else datetime.now(timezone.utc)
            if received_at <= sent_at:
                continue

            append_event(make_event(
                "email_response_observed",
                lead,
                {
                    "channel": "email",
                    "message_id": message_id,
                    "sender": sender,
                    "subject": subject,
                    "preview": re.sub(r"\s+", " ", body).strip()[:500],
                    "response_intent": classify_customer_response(body),
                    "received_at": received_at.isoformat(),
                },
            ))
            observed += 1

        print(json.dumps({
            "email_response_observed": observed,
            "tracked_contacts": len(leads),
        }, indent=2, sort_keys=True))
    finally:
        try:
            mail.logout()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
