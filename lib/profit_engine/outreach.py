from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .revenue import Lead, buyer_intent_score, commercial_relevance_score, offers


ORDER_PORTAL_URL = "https://zorathvael.github.io/zorathvael-os/order/"
OUTREACH_MARKER = "<!-- zorathvael-outreach:v1 -->"
DEFAULT_DAILY_GITHUB_LIMIT = 10
DEFAULT_REPOSITORY_COOLDOWN_DAYS = 7
DEFAULT_MAX_PER_RUN = 3


@dataclass(frozen=True)
class OutreachEvent:
    event_id: str
    event_type: str
    lead_url: str
    repository: str
    issue_number: str
    offer_id: str
    occurred_at: str
    metadata: dict[str, object]


def _explicit_intent(lead: Lead) -> bool:
    evidence = set(lead.evidence)
    return bool(evidence.intersection({
        "need help", "looking for", "github actions failed", "actions failed",
        "workflow failed", "failing workflow", "ci failed", "build failed",
        "deployment failed", "deploy failed", "pipeline failed", "cant deploy",
        "cannot deploy",
    }))


def _github_get_json(url: str, token: str, timeout: float = 15.0) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}" if token else "",
        "X-GitHub-Api-Version": "2026-03-10",
        "User-Agent": "Zorathvael-Revenue-Engine",
    }
    request = urllib.request.Request(url, headers={k: v for k, v in headers.items() if v})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub API response is not an object")
    return payload


def _parse_time(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def repository_health_score(
    repository_data: dict[str, Any],
    *,
    now: datetime | None = None,
    issue_updated_at: str = "",
    issue_state: str = "open",
) -> tuple[int, list[str]]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if repository_data.get("archived") or repository_data.get("disabled"):
        return 0, ["repository_archived_or_disabled"]

    pushed_at = _parse_time(str(repository_data.get("pushed_at", "")))
    issue_time = _parse_time(issue_updated_at)
    reasons: list[str] = []
    activity = 0

    if pushed_at is None:
        reasons.append("repository_activity_unknown")
    else:
        age_days = max((now - pushed_at).total_seconds() / 86400, 0)
        if age_days <= 7:
            activity = 100
        elif age_days <= 30:
            activity = 85
        elif age_days <= 60:
            activity = 70
        elif age_days <= 90:
            activity = 55
        else:
            activity = 25
            reasons.append("stale_repository")

    issue_freshness = 0
    if issue_state.lower() != "open":
        reasons.append("issue_not_open")
    elif issue_time is not None:
        issue_age = max((now - issue_time).total_seconds() / 86400, 0)
        if issue_age <= 7:
            issue_freshness = 100
        elif issue_age <= 30:
            issue_freshness = 85
        elif issue_age <= 60:
            issue_freshness = 65
        elif issue_age <= 90:
            issue_freshness = 45
        else:
            issue_freshness = 20
            reasons.append("stale_issue")
    else:
        reasons.append("issue_freshness_unknown")

    stars = max(int(repository_data.get("stargazers_count", 0) or 0), 0)
    forks = max(int(repository_data.get("forks_count", 0) or 0), 0)
    engagement = min(100, 40 + min(stars, 1000) / 1000 * 40 + min(forks, 200) / 200 * 20)
    maintainer_activity = activity
    score = round(
        activity * 0.35 + issue_freshness * 0.35
        + maintainer_activity * 0.15 + engagement * 0.15
    )
    if issue_state.lower() != "open" or score < 55:
        reasons.append("repository_health_below_outreach_threshold")
    return max(0, min(score, 100)), reasons


def fetch_repository_health(
    repository: str,
    issue_number: str,
    token: str = "",
    *,
    now: datetime | None = None,
) -> tuple[int, dict[str, int], list[str]]:
    repository_url = f"https://api.github.com/repos/{repository}"
    issue_url = f"https://api.github.com/repos/{repository}/issues/{urllib.parse.quote(str(issue_number), safe='')}"
    try:
        repo = _github_get_json(repository_url, token)
        issue = _github_get_json(issue_url, token)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError, ValueError, KeyError):
        return 0, {}, ["github_health_lookup_failed"]

    score, reasons = repository_health_score(
        repo,
        now=now,
        issue_updated_at=str(issue.get("updated_at", "")),
        issue_state=str(issue.get("state", "open")),
    )
    metrics = {"activity": score, "issue_freshness": score, "maintainer_activity": score, "engagement": score}
    return score, metrics, reasons


def _event_value(event: OutreachEvent | dict[str, Any], name: str, default: Any = "") -> Any:
    return event.get(name, default) if isinstance(event, dict) else getattr(event, name, default)


def _event_metadata(event: OutreachEvent | dict[str, Any]) -> dict[str, Any]:
    value = _event_value(event, "metadata", {})
    return value if isinstance(value, dict) else {}


def _event_is_github_send(event: OutreachEvent | dict[str, Any]) -> bool:
    return (
        _event_value(event, "event_type") == "outreach_sent"
        and _event_metadata(event).get("channel") == "github_issue_comment"
    )


def _event_time(event: OutreachEvent | dict[str, Any]) -> datetime | None:
    return _parse_time(str(_event_value(event, "occurred_at", "")))


def github_sends_today(events: list[OutreachEvent | dict[str, Any]], now: datetime | None = None) -> int:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return sum(
        1 for event in events
        if _event_is_github_send(event)
        and (event_time := _event_time(event)) is not None
        and event_time.date() == now.date()
    )


def repository_recently_contacted(
    repository: str,
    events: list[OutreachEvent | dict[str, Any]],
    now: datetime,
    cooldown_days: int,
) -> bool:
    cutoff = now - timedelta(days=max(cooldown_days, 0))
    return any(
        _event_value(event, "repository", "").lower() == repository.lower()
        and _event_value(event, "event_type") in {"outreach_sent", "email_outreach_sent"}
        and (event_time := _event_time(event)) is not None
        and event_time >= cutoff
        for event in events
    )


def adaptive_outreach_count(scores: list[int], maximum: int = DEFAULT_MAX_PER_RUN) -> int:
    scores = sorted((max(0, min(int(score), 100)) for score in scores), reverse=True)
    maximum = max(0, min(int(maximum), DEFAULT_MAX_PER_RUN))
    if not scores or maximum == 0:
        return 0
    sample = scores[: min(len(scores), maximum)]
    if not sample:
        return 0
    average = sum(sample) / len(sample)
    if average >= 80:
        target = 3
    elif average >= 70:
        target = 2
    elif average >= 60:
        target = 1
    else:
        target = 0
    return min(target, maximum, len(scores))


def select_auto_outreach(
    leads: list[Lead],
    already_contacted: set[str],
    limit: int = DEFAULT_MAX_PER_RUN,
    *,
    events: list[OutreachEvent | dict[str, Any]] | None = None,
    token: str = "",
    now: datetime | None = None,
    daily_limit: int = DEFAULT_DAILY_GITHUB_LIMIT,
    repository_cooldown_days: int = DEFAULT_REPOSITORY_COOLDOWN_DAYS,
    diagnostics: dict[str, object] | None = None,
) -> list[Lead]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    events = events or []
    safety_mode = bool(token or events)
    daily_remaining = max(int(daily_limit) - github_sends_today(events, now), 0) if safety_mode else max(int(limit), 0)
    hard_limit = min(max(int(limit), 0), DEFAULT_MAX_PER_RUN, daily_remaining)

    diagnostic_counts = {
        "total_leads": len(leads),
        "already_contacted": 0,
        "explicit_intent_missing": 0,
        "buyer_intent_below_45": 0,
        "commercial_relevance_below_70": 0,
        "repository_cooldown": 0,
        "eligible_before_health": 0,
        "health_lookup_failed": 0,
        "health_below_55": 0,
        "eligible_after_health": 0,
        "daily_quota_exhausted": int(hard_limit <= 0),
    }

    candidates: list[Lead] = []
    for lead in leads:
        if lead.url in already_contacted:
            diagnostic_counts["already_contacted"] += 1
            continue
        if not _explicit_intent(lead):
            diagnostic_counts["explicit_intent_missing"] += 1
            continue
        if buyer_intent_score(lead) < 45:
            diagnostic_counts["buyer_intent_below_45"] += 1
            continue
        if commercial_relevance_score(lead) < 70:
            diagnostic_counts["commercial_relevance_below_70"] += 1
            continue
        if safety_mode and repository_recently_contacted(
            lead.repository, events, now, repository_cooldown_days
        ):
            diagnostic_counts["repository_cooldown"] += 1
            continue
        candidates.append(lead)

    diagnostic_counts["eligible_before_health"] = len(candidates)

    scored: list[tuple[Lead, int]] = []
    health_cache: dict[str, tuple[int, dict[str, int], list[str]]] = {}
    for lead in candidates:
        if not safety_mode:
            scored.append((
                lead,
                round(
                    buyer_intent_score(lead) * 0.40
                    + commercial_relevance_score(lead) * 0.40
                    + lead.score * 0.20
                ),
            ))
            continue
        if lead.repository not in health_cache:
            health_cache[lead.repository] = fetch_repository_health(
                lead.repository, lead.external_id, token=token, now=now
            )
        health, _, reasons = health_cache[lead.repository]
        if health == 0 and "github_health_lookup_failed" in reasons:
            diagnostic_counts["health_lookup_failed"] += 1
            continue
        if health < 55 or reasons:
            diagnostic_counts["health_below_55"] += 1
            continue
        quality = round(
            buyer_intent_score(lead) * 0.30
            + commercial_relevance_score(lead) * 0.30
            + lead.score * 0.15
            + health * 0.25
        )
        scored.append((lead, quality))

    diagnostic_counts["eligible_after_health"] = len(scored)
    scored.sort(key=lambda item: item[1], reverse=True)
    if not scored or hard_limit <= 0:
        if diagnostics is not None:
            diagnostics.clear()
            diagnostics.update({
                **diagnostic_counts,
                "daily_sends": github_sends_today(events, now) if safety_mode else 0,
                "daily_limit": int(daily_limit),
                "daily_remaining": daily_remaining,
                "hard_limit": hard_limit,
                "scored_candidates": len(scored),
                "selected_target": 0,
                "selected": 0,
            })
        return []

    # Strict per-lead gates use the repository's published lead score.
    # Composite quality still determines ranking, but a strong average can
    # never promote a weak lead into the outreach quota.
    ranked = scored[:hard_limit]
    high_quality = [item for item in ranked if item[0].score >= 80]
    qualified_70 = [item for item in ranked if item[0].score >= 70]
    if len(high_quality) >= 3:
        target = 3
    elif len(qualified_70) >= 2:
        target = 2
    elif len(qualified_70) >= 1:
        target = 1
    else:
        target = 0

    selected = [lead for lead, _ in ranked[:target]]
    if diagnostics is not None:
        diagnostics.clear()
        diagnostics.update({
            **diagnostic_counts,
            "daily_sends": github_sends_today(events, now) if safety_mode else 0,
            "daily_limit": int(daily_limit),
            "daily_remaining": daily_remaining,
            "hard_limit": hard_limit,
            "scored_candidates": len(scored),
            "ranked_candidates": len(ranked),
            "high_quality_80_plus": len(high_quality),
            "qualified_70_plus": len(qualified_70),
            "selected_target": target,
            "selected": len(selected),
        })
    return selected


def build_email_outreach_message(lead: Lead, recipient: str) -> str:
    offer = offers()[lead.offer_id]
    return (
        f"Hello @{lead.author},\n\n"
        f"I found your public issue: {lead.title}\n"
        f"Zorathvael can provide a {offer.name} for this specific problem.\n"
        f"{lead.url}\n\n"
        "The deliverable is based only on public repository evidence; no credentials are required.\n\n"
        f"Fixed price: {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}.\n"
        f"Order securely through the Zorathvael portal: {ORDER_PORTAL_URL}?service={lead.offer_id}\n\n"
        "If this is not relevant, reply with 'no thanks' and we will not contact this address again.\n\n"
        "— Zorathvael Core\n"
        f"Reference: {lead.url}\n"
    )


def build_outreach_message(lead: Lead) -> str:
    offer = offers()[lead.offer_id]
    return (
        f"{OUTREACH_MARKER}\n"
        f"Hi @{lead.author} — I found this public issue ({lead.title}) while looking for "
        "specific problems where I can provide a concrete outcome. "
        f"Zorathvael can deliver {offer.name.lower()} for this case. "
        f"The fixed price is {offer.price_usdt:g} USDT or Rp{offer.price_idr:,}. "
        "No repository credentials are required; the service uses public repository evidence. "
        f"Order securely through the Zorathvael portal: {ORDER_PORTAL_URL}?service={lead.offer_id}"
    )


def load_events(path: str = "data/revenue_events.jsonl") -> list[OutreachEvent]:
    target = Path(path)
    if not target.exists():
        return []
    events: list[OutreachEvent] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(OutreachEvent(**json.loads(line)))
    return events


def append_event(event: OutreachEvent, path: str = "data/revenue_events.jsonl") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")


def make_event(event_type: str, lead: Lead, metadata: dict[str, object] | None = None) -> OutreachEvent:
    occurred_at = datetime.now(timezone.utc).isoformat()
    return OutreachEvent(
        event_id=f"{event_type}:{lead.url}:{occurred_at}",
        event_type=event_type,
        lead_url=lead.url,
        repository=lead.repository,
        issue_number=lead.external_id,
        offer_id=lead.offer_id,
        occurred_at=occurred_at,
        metadata=metadata or {},
    )
