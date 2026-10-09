from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone

from lib.profit_engine.outreach import append_event, load_events, make_event
from lib.profit_engine.customer_demand import classify_customer_response
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
            response_intent = classify_customer_response(body)
            created_at = str(comment.get("created_at", ""))
            author = str(comment.get("user", {}).get("login", ""))
            if not cid or cid in observed or "zorathvael-outreach:v1" in body or author.lower() in {"github-actions[bot]", "zorathvael"}:
                continue
            try:
                if datetime.fromisoformat(created_at.replace("Z", "+00:00")) <= datetime.fromisoformat(event.occurred_at.replace("Z", "+00:00")):
                    continue
            except ValueError:
                continue
            # Issue comments are flat, so attribution is heuristic. Ignore neutral
            # comments to avoid counting unrelated discussion as customer interest.
            if response_intent == "neutral":
                continue
            lead = Lead("github_issue_search", event.issue_number, "", event.lead_url, event.repository, author, (), 0, event.offer_id, "", event.occurred_at)
            append_event(make_event("response_observed", lead, {
                "comment_id": cid,
                "author": author,
                "channel": "github_issue_comment",
                "response_intent": response_intent,
                "response_text": body[:500],
                "attribution_method": "post_outreach_comment_heuristic",
            }))
            observed.add(cid)
            count += 1
    print(json.dumps({"responses_observed_now": count}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
