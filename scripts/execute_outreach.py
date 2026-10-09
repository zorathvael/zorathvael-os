from __future__ import annotations

import json
import os
import smtplib
import ssl
import urllib.error
import urllib.request
from email.message import EmailMessage
from pathlib import Path

from lib.profit_engine.outreach import (
    append_event,
    build_email_outreach_message,
    build_outreach_message,
    load_events,
    make_event,
    select_auto_outreach,
)
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


def _request(url: str, token: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Revenue-Engine",
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={**headers, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def remote_outreach_exists(lead: Lead, token: str) -> bool:
    url = f"https://api.github.com/repos/{lead.repository}/issues/{lead.external_id}/comments?per_page=100"
    comments = _request(url, token)
    if not isinstance(comments, list):
        return False
    return any("<!-- zorathvael-outreach:v1 -->" in str(item.get("body", "")) for item in comments)


def post_comment(lead: Lead, message: str, token: str) -> int:
    url = f"https://api.github.com/repos/{lead.repository}/issues/{lead.external_id}/comments"
    data = _request(url, token, "POST", {"body": message})
    return int(data["id"])


def email_configured() -> bool:
    return all(
        os.getenv(name, "").strip()
        for name in (
            "ZORATHVAEL_SMTP_HOST",
            "ZORATHVAEL_SMTP_USERNAME",
            "ZORATHVAEL_SMTP_PASSWORD",
            "ZORATHVAEL_EMAIL_FROM",
        )
    )


def send_email(lead: Lead) -> str:
    if not lead.contact_email:
        raise ValueError("public contact email is missing")
    if not email_configured():
        raise RuntimeError("email_transport_not_configured")

    host = os.environ["ZORATHVAEL_SMTP_HOST"]
    username = os.environ["ZORATHVAEL_SMTP_USERNAME"]
    password = os.environ["ZORATHVAEL_SMTP_PASSWORD"]
    sender = os.environ["ZORATHVAEL_EMAIL_FROM"]
    port = int(os.getenv("ZORATHVAEL_SMTP_PORT", "").strip() or "587")
    subject = f"Zorathvael — {lead.offer_id.replace('_', ' ')}: {lead.title}"

    message = EmailMessage()
    message["From"] = sender
    message["To"] = lead.contact_email
    message["Subject"] = subject
    message.set_content(build_email_outreach_message(lead, lead.contact_email))

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls(context=context)
        smtp.login(username, password)
        smtp.send_message(message)
    return message["Message-ID"] or ""


def main() -> int:
    token = os.getenv("ZORATHVAEL_OUTREACH_TOKEN", "").strip()
    fallback_token = os.getenv("GITHUB_TOKEN", "").strip()

    events = load_events()
    contacted = {
        event.lead_url
        for event in events
        if event.event_type in {"outreach_sent", "email_outreach_sent"}
    }
    leads = load_leads()
    selection_diagnostics: dict[str, object] = {}
    selected = select_auto_outreach(
        leads,
        contacted,
        limit=int(os.getenv("ZORATHVAEL_OUTREACH_LIMIT", "3")),
        events=events,
        token=token or fallback_token,
        daily_limit=int(os.getenv("ZORATHVAEL_GITHUB_DAILY_OUTREACH_LIMIT", "10")),
        repository_cooldown_days=int(
            os.getenv("ZORATHVAEL_GITHUB_REPOSITORY_COOLDOWN_DAYS", "7")
        ),
        diagnostics=selection_diagnostics,
    )

    sent = 0
    failures = []
    blocked = []
    own_repository = os.getenv("GITHUB_REPOSITORY", "zorathvael/zorathvael-os").lower()

    external_selected = [
        lead for lead in selected
        if lead.repository.lower() != own_repository
        and not (lead.contact_email and email_configured())
    ]
    if external_selected and not token:
        message = (
            "External outreach is required but ZORATHVAEL_OUTREACH_TOKEN is missing. "
            "GITHUB_TOKEN cannot write to repositories other than the workflow repository. "
            f"selected_external={len(external_selected)}"
        )
        for lead in external_selected:
            append_event(make_event(
                "outreach_blocked",
                lead,
                {"reason": "external_write_token_missing", "fatal": True},
            ))
        print(json.dumps({
            "selected": len(selected),
            "selection_diagnostics": selection_diagnostics,
            "sent": 0,
            "blocked": [{"lead_url": lead.url, "reason": "external_write_token_missing"} for lead in external_selected],
            "failures": [],
            "email_transport_configured": email_configured(),
            "external_transport_configured": False,
            "error": message,
            "event_log": "data/revenue_events.jsonl",
        }, indent=2, sort_keys=True))
        return 2

    for lead in selected:
        # Email is the primary route when a public email was discovered and
        # an SMTP transport is configured. GitHub is the fallback route.
        if lead.contact_email and email_configured():
            try:
                message_id = send_email(lead)
                append_event(make_event(
                    "email_outreach_sent",
                    lead,
                    {
                        "channel": "email",
                        "recipient": lead.contact_email,
                        "contact_source": lead.contact_source,
                        "message_id": message_id,
                    },
                ))
                sent += 1
                continue
            except (OSError, smtplib.SMTPException, ValueError, RuntimeError) as exc:
                failures.append({
                    "lead_url": lead.url,
                    "channel": "email",
                    "error": f"{type(exc).__name__}: {exc}",
                })
                append_event(make_event(
                    "email_outreach_failed",
                    lead,
                    {
                        "recipient": lead.contact_email,
                        "error": f"{type(exc).__name__}: {exc}",
                    },
                ))

        target_token = token
        if lead.repository.lower() == own_repository:
            target_token = token or fallback_token
        elif not token:
            blocked.append({
                "lead_url": lead.url,
                "reason": "external_write_token_missing",
            })
            append_event(make_event(
                "outreach_blocked",
                lead,
                {"reason": "external_write_token_missing"},
            ))
            continue

        try:
            if remote_outreach_exists(lead, target_token):
                append_event(make_event(
                    "outreach_sent",
                    lead,
                    {"channel": "github_issue_comment", "deduplicated": True},
                ))
                continue

            comment_id = post_comment(lead, build_outreach_message(lead), target_token)
            append_event(make_event(
                "outreach_sent",
                lead,
                {"comment_id": comment_id, "channel": "github_issue_comment"},
            ))
            sent += 1
        except (OSError, urllib.error.HTTPError, KeyError, ValueError) as exc:
            failures.append({
                "lead_url": lead.url,
                "channel": "github_issue_comment",
                "error": f"{type(exc).__name__}: {exc}",
            })
            append_event(make_event(
                "outreach_failed",
                lead,
                {"error": f"{type(exc).__name__}: {exc}"},
            ))

    result = {
        "selected": len(selected),
        "selection_diagnostics": selection_diagnostics,
        "sent": sent,
        "blocked": blocked,
        "failures": failures,
        "email_transport_configured": email_configured(),
        "external_transport_configured": bool(token),
        "event_log": "data/revenue_events.jsonl",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if selected and sent == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
