from __future__ import annotations

import json
import os
import urllib.request

from lib.profit_engine.outreach import append_event, load_events, make_event
from lib.profit_engine.revenue import Lead


def _get(url: str, token: str):
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Revenue-Engine",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    events = load_events()
    observed = {str(e.metadata.get("comment_id")) for e in events if e.event_type == "response_observed"}
    sent = [e for e in events if e.event_type == "outreach_sent"]
    count = 0
    for event in sent:
        if event.metadata.get("deduplicated"):
            continue
        comments = _get(f"https://api.github.com/repos/{event.repository}/issues/{event.issue_number}/comments?per_page=100", token)
        for comment in comments if isinstance(comments, list) else []:
            cid = str(comment.get("id", ""))
            body = str(comment.get("body", ""))
            author = str(comment.get("user", {}).get("login", ""))
            if not cid or cid in observed or "zorathvael-outreach:v1" in body or author.lower() in {"github-actions[bot]", "zorathvael"}:
                continue
            lead = Lead("github_issue_search", event.issue_number, "", event.lead_url, event.repository, author, (), 0, event.offer_id, "", event.occurred_at)
            append_event(make_event("response_observed", lead, {"comment_id": cid, "author": author, "channel": "github_issue_comment"}))
            observed.add(cid)
            count += 1
    print(json.dumps({"responses_observed_now": count}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
