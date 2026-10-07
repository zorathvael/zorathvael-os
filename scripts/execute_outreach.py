from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from lib.profit_engine.outreach import (
    append_event,
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
    request = urllib.request.Request(url, data=data, method=method, headers={**headers, "Content-Type": "application/json"})
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


def main() -> int:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required for outreach execution")

    events = load_events()
    contacted = {event.lead_url for event in events if event.event_type == "outreach_sent"}
    leads = load_leads()
    selected = select_auto_outreach(
        leads, contacted, limit=int(os.getenv("ZORATHVAEL_OUTREACH_LIMIT", "3"))
    )

    sent = 0
    failures = []
    for lead in selected:
        try:
            if remote_outreach_exists(lead, token):
                append_event(make_event("outreach_sent", lead, {"channel": "github_issue_comment", "deduplicated": True}))
                continue
            comment_id = post_comment(lead, build_outreach_message(lead), token)
            append_event(make_event(
                "outreach_sent", lead,
                {"comment_id": comment_id, "channel": "github_issue_comment"},
            ))
            sent += 1
        except (OSError, urllib.error.HTTPError, KeyError, ValueError) as exc:
            failures.append({"lead_url": lead.url, "error": f"{type(exc).__name__}: {exc}"})
            append_event(make_event(
                "outreach_failed", lead,
                {"error": f"{type(exc).__name__}: {exc}"},
            ))

    print(json.dumps({
        "selected": len(selected),
        "sent": sent,
        "failures": failures,
        "event_log": "data/revenue_events.jsonl",
    }, indent=2, sort_keys=True))
    # Failures are recorded per lead so state persistence can continue.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
