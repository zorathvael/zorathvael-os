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



def _api_text(url: str, token: str) -> str:
    import urllib.request
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2026-03-10", "User-Agent": "Zorathvael-Revenue-Engine"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def _failure_fingerprint(log: str) -> tuple[str, str]:
    patterns = (
        ("dependency-install", ("ModuleNotFoundError", "No matching distribution", "npm ERR!", "Could not resolve dependencies")),
        ("test-failure", ("AssertionError", "FAILED", "test failed", "tests failed")),
        ("authentication", ("401 Unauthorized", "403 Forbidden", "authentication failed", "permission denied")),
        ("missing-secret", ("secret", "environment variable", "not set", "required variable")),
        ("network", ("timeout", "timed out", "connection refused", "Temporary failure in name resolution")),
        ("build", ("build failed", "compilation failed", "syntax error", "exit code 1")),
        ("deployment", ("deployment failed", "deploy failed", "release failed")),
    )
    lower = log.lower()
    for fingerprint, needles in patterns:
        for needle in needles:
            if needle.lower() in lower:
                return fingerprint, needle
    return "unclassified", "no known error fingerprint"


def ci_failure_recovery(repository_url: str, token: str) -> str:
    parts = [part for part in urllib.parse.urlparse(repository_url).path.split("/") if part]
    if len(parts) != 2:
        raise ValueError("invalid GitHub repository URL")
    owner, repo = parts
    api = f"https://api.github.com/repos/{owner}/{repo}"
    metadata = _api_get(api, token)
    runs = _api_get(f"{api}/actions/runs?status=failure&per_page=10&exclude_pull_requests=false", token).get("workflow_runs", [])
    lines = [
        f"# Zorathvael CI Failure Recovery — {metadata.get('full_name', repository_url)}",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Evidence",
        f"- Recent failed workflow runs inspected: {len(runs)}",
        "- Source: public GitHub Actions workflow metadata, failed-job metadata, and job logs.",
        "- No private credentials or repository write access are required.",
        "",
    ]
    if not runs:
        lines.extend([
            "## Result",
            "No failed GitHub Actions run was available in the inspected window.",
            "No remediation is claimed without failure evidence.",
            "",
            "## Next action",
            "Retry this diagnostic after a failed workflow run is visible.",
        ])
        return "\n".join(lines)

    remediation = {
        "dependency-install": ["Pin or correct the dependency version, then rerun the same workflow.", "Confirm the runtime/package-manager version matches the lockfile."],
        "test-failure": ["Inspect the failing assertion/test fixture before changing production behavior.", "Reproduce the same test command locally or in a controlled CI rerun."],
        "authentication": ["Verify the referenced credential/permission exists and is available to the workflow.", "Do not paste secrets into issue comments or committed files."],
        "missing-secret": ["Identify the exact missing environment variable or secret name.", "Configure it in the appropriate GitHub Actions secret/environment scope."],
        "network": ["Retry after checking the external service and runner network path.", "Add bounded retries/backoff only when the operation is safe to repeat."],
        "build": ["Inspect the first compiler/syntax error rather than the final exit-code line.", "Fix the source/configuration error and rerun the same workflow."],
        "deployment": ["Inspect the deployment provider response and authentication state.", "Verify the target environment and required deployment variables."],
        "unclassified": ["Use the failed-step log excerpt below to isolate the first actionable error.", "Do not claim a root cause until the failure can be reproduced or the error is explicit."],
    }
    diagnoses: list[str] = []
    for run in runs[:3]:
        run_id = run.get("id")
        jobs = _api_get(f"{api}/actions/runs/{run_id}/jobs?filter=latest&per_page=100", token).get("jobs", [])
        failed_jobs = [job for job in jobs if job.get("conclusion") == "failure"]
        lines.extend([
            f"## Run {run_id}",
            f"- Workflow: {run.get('name', 'unknown')}",
            f"- Created: {run.get('created_at', 'unknown')}",
            f"- Commit: {run.get('head_sha', 'unknown')}",
            f"- Run: {run.get('html_url', 'unavailable')}",
            f"- Failed jobs: {len(failed_jobs)}",
            "",
        ])
        for job in failed_jobs[:3]:
            failed_steps = [step for step in job.get("steps", []) if step.get("conclusion") == "failure"]
            step_name = failed_steps[-1].get("name", "unknown") if failed_steps else "unknown"
            try:
                log = _api_text(f"{api}/actions/jobs/{job.get('id')}/logs", token)
            except Exception as exc:
                log = f"log retrieval failed: {type(exc).__name__}"
            fingerprint, evidence = _failure_fingerprint(log)
            excerpt = "\n".join(log.splitlines()[-25:])[-5000:]
            lines.extend([
                f"### Failed job: {job.get('name', 'unknown')}",
                f"- Failing step: {step_name}",
                f"- Fingerprint: {fingerprint}",
                f"- Evidence token: {evidence}",
                "",
                "### Remediation path",
                *remediation.get(fingerprint, remediation["unclassified"]),
                "",
                "### Log excerpt",
                "~~~text",
                excerpt,
                "~~~",
                "",
            ])
            diagnoses.append(f"{run.get('name', 'workflow')} / {job.get('name', 'job')}: {fingerprint}")
    lines.extend(["## Recovery summary", *[f"- {item}" for item in diagnoses], "", "This is an evidence-based diagnostic, not a guarantee that the proposed remediation will fix the repository."])
    return "\n".join(lines)


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
