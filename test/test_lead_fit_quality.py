import json
from datetime import datetime, timezone

from scripts.revenue_cycle import merge_leads
from lib.profit_engine.revenue import extract_problem_context


def test_problem_context_falls_back_to_title_for_unrelated_or_meta_text():
    assert extract_problem_context(
        "CI workflow times out",
        "While you were away: a one-line recap of the whole workspace.",
    ) == "CI workflow times out"
    assert extract_problem_context(
        "Test does not wait for the event",
        "The user's rule. A number in a test falls into one of three cases.",
    ) == "Test does not wait for the event"


def test_merge_leads_drops_legacy_generic_fit_and_repairs_stale_offer(tmp_path):
    path = tmp_path / "revenue_leads.jsonl"
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "source": "github_issue_search", "external_id": "1",
            "title": "Automation and API integration", "url": "https://github.com/example/repo/issues/1",
            "repository": "example/repo", "author": "maintainer",
            "evidence": ["automation", "api"], "score": 70, "offer_id": "public_repo_audit",
            "contact_url": "https://github.com/maintainer", "discovered_at": now,
            "problem_context": "", "contact_email": None, "contact_source": "none",
        },
        {
            "source": "github_issue_search", "external_id": "2",
            "title": "Build failed during deployment", "url": "https://github.com/example/repo/issues/2",
            "repository": "example/repo", "author": "maintainer",
            "evidence": ["build failed"], "score": 80, "offer_id": "public_repo_audit",
            "contact_url": "https://github.com/maintainer", "discovered_at": now,
            "problem_context": "While you were away: a one-line recap of the whole workspace.",
            "contact_email": None, "contact_source": "none",
        },
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    leads = merge_leads(str(path), [])

    assert [lead.url for lead in leads] == ["https://github.com/example/repo/issues/2"]
    assert leads[0].offer_id == "ci_failure_recovery"
    assert leads[0].problem_context == "Build failed during deployment"
    persisted = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert len(persisted) == 1
    assert persisted[0]["offer_id"] == "ci_failure_recovery"
