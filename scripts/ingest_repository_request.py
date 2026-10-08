from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse

from lib.profit_engine.revenue import (
    Lead,
    commercial_relevance_score,
    is_commercial_noise,
    is_non_buying_meta_issue,
    score_lead,
    select_offer,
)

GITHUB_RE = re.compile(r"^https://github\.com/([^/]+)/([^/#?]+?)/?$")
ISSUE_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/issues/(\d+)/?$")


def _github_json(url: str, token: str = "") -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Repository-Intake",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"GitHub API request failed ({exc.code}): {detail}") from exc


def normalize_repository_url(value: str) -> tuple[str, str]:
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ValueError("target repository must use https://github.com/OWNER/REPO")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) == 2 and parts[1].endswith(".git"):
        parts[1] = parts[1][:-4]
    if len(parts) != 2 or not all(parts):
        raise ValueError("target repository must use https://github.com/OWNER/REPO")
    owner, repo = parts
    return f"https://github.com/{owner}/{repo}", f"{owner}/{repo}"


def parse_issue_url(value: str, repository: str) -> tuple[str, int] | None:
    if not value.strip():
        return None
    match = ISSUE_RE.fullmatch(value.strip())
    if not match:
        raise ValueError("issue URL must use https://github.com/OWNER/REPO/issues/NUMBER")
    owner, repo, number = match.groups()
    if f"{owner}/{repo}".lower() != repository.lower():
        raise ValueError("issue URL must belong to the target repository")
    return f"https://github.com/{owner}/{repo}/issues/{number}", int(number)


def request_key(repository: str, issue_url: str, context: str) -> str:
    raw = f"{repository.lower()}|{issue_url.strip().lower()}|{context.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def load_records(path: str) -> list[dict]:
    target = Path(path)
    if not target.exists():
        return []
    return [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_unique(record: dict, path: str) -> bool:
    target = Path(path)
    records = load_records(path)
    if any(item.get("request_key") == record["request_key"] for item in records):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return True


def append_lead(lead: Lead, path: str = "data/revenue_leads.jsonl") -> bool:
    target = Path(path)
    records = load_records(path)
    if any(item.get("url") == lead.url for item in records):
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(lead), sort_keys=True) + "\n")
    return True


def ingest(repository_url: str, issue_url: str = "", context: str = "", token: str = "") -> dict:
    normalized_url, repository = normalize_repository_url(repository_url)
    parsed_issue = parse_issue_url(issue_url, repository)
    repo_data = _github_json(f"https://api.github.com/repos/{repository}", token)
    issue_data = (
        _github_json(f"https://api.github.com/repos/{repository}/issues/{parsed_issue[1]}", token)
        if parsed_issue
        else {}
    )

    repo_description = (repo_data.get("description") or "").strip()
    issue_title = (issue_data.get("title") or "").strip()
    issue_body = (issue_data.get("body") or "").strip()
    analysis_title = issue_title or f"Manual repository intake: {repository}"
    analysis_body = "\n".join(part for part in (context.strip(), issue_body, repo_description) if part)
    comments = int(issue_data.get("comments", 0) or 0)
    score, evidence = score_lead(analysis_title, analysis_body, comments)
    buying_noise = is_commercial_noise(analysis_title, analysis_body) or is_non_buying_meta_issue(analysis_title, analysis_body)
    qualified = score >= 30 and not buying_noise
    offer = select_offer(score, evidence)
    now = datetime.now(timezone.utc).isoformat()
    public_issue_url = parsed_issue[0] if parsed_issue else normalized_url
    key = request_key(repository, public_issue_url, context)

    lead = Lead(
        "manual_repository_intake",
        str(parsed_issue[1]) if parsed_issue else key,
        analysis_title,
        public_issue_url,
        repository,
        issue_data.get("user", {}).get("login", ""),
        evidence,
        score,
        offer.product_id,
        issue_data.get("user", {}).get("html_url", normalized_url),
        now,
    )

    record = {
        "request_key": key,
        "source": "manual_repository_intake",
        "status": "qualified" if qualified else "queued",
        "repository": repository,
        "repository_url": normalized_url,
        "issue_url": parsed_issue[0] if parsed_issue else "",
        "issue_number": parsed_issue[1] if parsed_issue else None,
        "issue_title": issue_title,
        "problem_context": context.strip(),
        "repository_description": repo_description,
        "score": score,
        "evidence": list(evidence),
        "commercial_relevance": commercial_relevance_score(lead) if qualified else 0,
        "offer_id": offer.product_id,
        "created_at": now,
    }
    created = append_unique(record, "data/manual_repository_requests.jsonl")
    lead_created = append_lead(lead) if qualified and parsed_issue else False

    return {
        "created": created,
        "lead_created": lead_created,
        "request_key": key,
        "repository": repository,
        "issue_url": parsed_issue[0] if parsed_issue else "",
        "score": score,
        "qualified": qualified,
        "offer_id": offer.product_id,
        "commercial_relevance": record["commercial_relevance"],
        "status": record["status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--issue-url", default="")
    parser.add_argument("--context", default="")
    args = parser.parse_args()
    result = ingest(
        args.repository,
        args.issue_url,
        args.context,
        os.getenv("GITHUB_TOKEN", ""),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
