from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
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
    rows = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return [
        Lead(
            source=row["source"],
            external_id=str(row["external_id"]),
            title=row["title"],
            url=row["url"],
            repository=row["repository"],
            author=row["author"],
            evidence=tuple(row.get("evidence", [])),
            score=int(row["score"]),
            offer_id=row["offer_id"],
            contact_url=row.get("contact_url", ""),
            discovered_at=row.get("discovered_at", ""),
        )
        for row in rows
    ]


def post_comment(lead: Lead, message: str, token: str) -> int:
    payload = json.dumps({"body": message}).encode("utf-8")
    url = f"https://api.github.com/repos/{lead.repository}/issues/{lead.external_id}/comments"
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "Zorathvael-Revenue-Engine",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    return int(data["id"])


def main() -> int:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required for outreach execution")

    events = load_events()
    contacted = {
        event.lead_url
        for event in events
        if event.event_type == "outreach_sent"
    }
    leads = load_leads()
    selected = select_auto_outreach(leads, contacted, limit=int(os.getenv("ZORATHVAEL_OUTREACH_LIMIT", "3")))

    sent = 0
    failures = []
    for lead in selected:
        try:
            comment_id = post_comment(lead, build_outreach_message(lead), token)
            append_event(
                make_event(
                    "outreach_sent",
                    lead,
                    {"comment_id": comment_id, "channel": "github_issue_comment"},
                )
            )
            sent += 1
        except (OSError, urllib.error.HTTPError, KeyError, ValueError) as exc:
            failures.append({"lead_url": lead.url, "error": f"{type(exc).__name__}: {exc}"})

    print(
        json.dumps(
            {
                "selected": len(selected),
                "sent": sent,
                "failures": failures,
                "event_log": "data/revenue_events.jsonl",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
