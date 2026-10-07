from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from .revenue import offers


def _api_get(url: str, token: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Revenue-Engine",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def audit_repository(repository_url: str, token: str, product_id: str = "public_repo_audit") -> str:
    parts = [part for part in urllib.parse.urlparse(repository_url).path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("invalid GitHub repository URL")
    owner, repo = parts
    api = f"https://api.github.com/repos/{owner}/{repo}"
    metadata = _api_get(api, token)
    languages = _api_get(f"{api}/languages", token)
    workflows = _api_get(f"{api}/actions/workflows?per_page=100", token)
    issues = _api_get(f"{api}/issues?state=open&per_page=20&sort=updated&direction=desc", token)
    workflow_count = len(workflows.get("workflows", []))
    issue_count = len([item for item in issues if "pull_request" not in item])
    language_names = ", ".join(list(languages.keys())[:8]) or "not detected"
    gaps: list[str] = []
    if workflow_count == 0:
        gaps.append("No GitHub Actions workflow detected.")
    if issue_count >= 10:
        gaps.append(f"{issue_count} open issues indicate a meaningful automation/maintenance backlog.")
    if not metadata.get("has_wiki"):
        gaps.append("A lightweight operational knowledge base could reduce repeated maintenance work.")
    if not gaps:
        gaps.append("Existing automation is present; next value is optimization, observability, and measurable cost/time reduction.")
    now = datetime.now(timezone.utc).isoformat()
    blueprint = []
    if product_id == "automation_blueprint":
        blueprint = [
            "",
            "## Implementation blueprint",
            "### Phase 1 — deterministic automation",
            "Define one trigger, one input contract, one processing step, and one measurable output.",
            "### Phase 2 — reliability",
            "Add idempotency keys, retries with backoff, failure notifications, and execution logs.",
            "### Phase 3 — economics",
            "Track minutes saved, execution success rate, operating cost, and payback period.",
            "### Phase 4 — scale",
            "Only after positive measured ROI, add more workflows and external integrations.",
        ]
    return "\n".join([
        f"# Zorathvael AI Automation Audit — {metadata.get('full_name', repository_url)}",
        "",
        f"Generated: {now}",
        "",
        "## Repository baseline",
        f"- Stars: {metadata.get('stargazers_count', 0)}",
        f"- Forks: {metadata.get('forks_count', 0)}",
        f"- Open issues: {metadata.get('open_issues_count', 0)}",
        f"- Primary language: {metadata.get('language') or 'not detected'}",
        f"- Languages sampled: {language_names}",
        f"- GitHub Actions workflows: {workflow_count}",
        "",
        "## Highest-value automation observations",
        *[f"1. {item}" for item in gaps],
        "",
        "## Recommended first actions",
        "1. Identify one repetitive task with a measurable time cost.",
        "2. Convert it into a deterministic workflow with explicit inputs and outputs.",
        "3. Add failure handling, idempotency, and an execution log.",
        "4. Measure time saved, successful executions, and operating cost.",
        "5. Only expand the automation after the first workflow demonstrates positive ROI.",
        "",
        "## Delivery boundary",
        "This audit uses public repository data only. It does not claim access to private systems or credentials.",
        *blueprint,
    ])


def offer_delivery_text(product_id: str) -> str:
    offer = offers()[product_id]
    return f"{offer.name}\n\n{offer.description}\n\nDelivery: {offer.delivery}"
