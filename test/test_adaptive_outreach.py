from datetime import datetime, timedelta, timezone

from lib.profit_engine.outreach import (
    adaptive_outreach_count,
    repository_health_score,
    select_auto_outreach,
)
from lib.profit_engine.revenue import Lead


def lead(repo: str, issue: str, score: int = 80) -> Lead:
    return Lead(
        source="github_issue_search",
        external_id=issue,
        title="GitHub Actions failed and need help",
        url=f"https://github.com/{repo}/issues/{issue}",
        repository=repo,
        author="owner",
        evidence=("github actions failed", "need help"),
        score=score,
        offer_id="ci_failure_recovery",
        contact_url="https://github.com/owner",
        discovered_at=datetime.now(timezone.utc).isoformat(),
    )


def test_repository_health_blocks_archived_and_stale_repositories():
    assert repository_health_score(
        {"archived": True, "disabled": False, "pushed_at": datetime.now(timezone.utc).isoformat()}
    )[0] == 0
    stale = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    score, reasons = repository_health_score(
        {"archived": False, "disabled": False, "pushed_at": stale}
    )
    assert score < 60
    assert "stale_repository" in reasons


def test_adaptive_outreach_count_scales_only_with_quality():
    assert adaptive_outreach_count([95, 92, 90, 88, 86, 84, 82, 80, 78, 76], 10) == 10
    assert adaptive_outreach_count([82, 81, 80, 79, 78, 77, 76], 10) == 8
    assert adaptive_outreach_count([72, 71, 70, 69, 68, 67], 10) == 6
    assert adaptive_outreach_count([61, 60, 59, 58, 57], 10) == 5
    assert adaptive_outreach_count([49, 45, 40, 35, 30], 10) == 0


def test_selection_enforces_repository_cooldown_and_daily_budget(monkeypatch):
    fresh = datetime.now(timezone.utc).isoformat()

    def fake_health(repository, issue_number, token=""):
        return 95, {"activity": 95, "issue_freshness": 95, "maintainer_activity": 95, "engagement": 95}, []

    monkeypatch.setattr("lib.profit_engine.outreach.fetch_repository_health", fake_health)

    events = [
        {
            "event_type": "outreach_sent",
            "repository": "owner/recent",
            "lead_url": "https://github.com/owner/recent/issues/1",
            "occurred_at": fresh,
            "metadata": {"channel": "github_issue_comment"},
        }
    ]
    leads = [lead("owner/recent", str(i), 90) for i in range(1, 11)]
    selected = select_auto_outreach(
        leads,
        already_contacted=set(),
        limit=10,
        events=events,
        token="token",
        now=datetime.now(timezone.utc),
        daily_limit=10,
        repository_cooldown_days=7,
    )
    assert selected == []
