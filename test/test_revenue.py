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
