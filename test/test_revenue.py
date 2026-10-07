from lib.profit_engine.revenue import Lead, rank_outreach_leads, is_commercial_noise


def make_lead(number: str, title: str, evidence: tuple[str, ...], score: int) -> Lead:
    return Lead(
        source="github_issue_search",
        external_id=number,
        title=title,
        url=f"https://github.com/example/repo/issues/{number}",
        repository="example/repo",
        author="owner",
        evidence=evidence,
        score=score,
        offer_id="automation_blueprint",
        contact_url="https://github.com/owner",
        discovered_at="2026-10-07T00:00:00+00:00",
    )


def test_commercial_filter_rejects_promotional_noise() -> None:
    assert is_commercial_noise("Best AngularJS Development company in Chennai", "") is True


def test_rank_outreach_leads_prefers_active_failure_over_generic_automation() -> None:
    failure = make_lead(
        "879",
        "Deployment failed and needs recovery",
        ("deploy failed", "workflow", "build", "failed", "78 comments"),
        88,
    )
    generic = make_lead(
        "53",
        "Automation roadmap",
        ("automation", "workflow"),
        65,
    )
    promotional = make_lead(
        "315",
        "Best software development company",
        ("automation", "api"),
        90,
    )

    ranked = rank_outreach_leads([generic, promotional, failure], limit=2)

    assert [lead.external_id for lead in ranked] == ["879", "53"]


def test_rank_outreach_leads_deduplicates_by_issue_url() -> None:
    first = make_lead("1", "Workflow failed", ("workflow failed", "failed"), 70)
    duplicate = make_lead("1", "Workflow failed", ("workflow failed", "failed"), 95)

    ranked = rank_outreach_leads([first, duplicate], limit=10)

    assert len(ranked) == 1
    assert ranked[0].score == 95


def test_buyer_intent_prioritizes_explicit_failure_and_help() -> None:
    failure = make_lead("2", "CI failed", ("ci failed", "failed", "12 comments"), 60)
    generic = make_lead("3", "Automation", ("automation",), 90)

    from lib.profit_engine.revenue import buyer_intent_score

    assert buyer_intent_score(failure) > buyer_intent_score(generic)


def test_refresh_metrics_records_timestamp_and_preserves_revenue() -> None:
    import json
    from pathlib import Path
    from tempfile import TemporaryDirectory
    from scripts.revenue_cycle import refresh_metrics

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "metrics.json"
        path.write_text(json.dumps({"paid_orders": 2, "revenue_usdt": 20.0}), encoding="utf-8")
        refresh_metrics(5, 3, 2, str(path))
        data = json.loads(path.read_text(encoding="utf-8"))

    assert data["paid_orders"] == 2
    assert data["revenue_usdt"] == 20.0
    assert data["qualified_leads"] == 5
    assert data["commercially_relevant_leads"] == 3
    assert data["outreach_ready_leads"] == 2
    assert data["last_updated"]
