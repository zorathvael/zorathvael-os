from lib.profit_engine.revenue import Lead, rank_outreach_leads, is_commercial_noise, is_non_buying_meta_issue


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

    assert [lead.external_id for lead in ranked] == ["879"]


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


def test_conversion_funnel_matches_orders_to_leads_without_inventing_attribution(tmp_path):
    from lib.profit_engine.conversion import build_conversion_funnel

    leads = [
        {"url": "https://github.com/acme/app/issues/1", "repository": "acme/app", "offer_id": "ci_failure_recovery"},
        {"url": "https://github.com/acme/other/issues/2", "repository": "acme/other", "offer_id": "automation_blueprint"},
    ]
    orders = [
        {"order_id": "ZOR-1", "target_repository": "https://github.com/acme/app", "product_id": "ci_failure_recovery", "status": "paid"},
        {"order_id": "ZOR-2", "target_repository": "https://github.com/acme/unknown", "product_id": "ci_failure_recovery", "status": "paid"},
    ]

    funnel = build_conversion_funnel(leads, orders)

    assert funnel["lead_count"] == 2
    assert funnel["paid_orders"] == 2
    assert funnel["attributed_paid_orders"] == 1
    assert funnel["unattributed_paid_orders"] == 1
    assert funnel["paid_revenue_orders"] == 2


def test_auto_outreach_requires_explicit_buyer_intent_and_is_idempotent() -> None:
    from lib.profit_engine.outreach import build_outreach_message, select_auto_outreach

    lead = make_lead(
        "42",
        "CI failed and I need help deploying",
        ("ci failed", "need help", "deploy failed"),
        92,
    )
    selected = select_auto_outreach([lead], already_contacted=set(), limit=3)

    assert len(selected) == 1
    message = build_outreach_message(lead)
    assert "CI failed" in message
    assert "Zorathvael" in message
    assert "order" in message.lower()

    selected_again = select_auto_outreach([lead], already_contacted={lead.url}, limit=3)
    assert selected_again == []


def test_auto_outreach_does_not_contact_generic_low_intent_leads() -> None:
    from lib.profit_engine.outreach import select_auto_outreach

    lead = make_lead("43", "Automation ideas", ("automation", "workflow"), 80)
    assert select_auto_outreach([lead], already_contacted=set(), limit=3) == []


def test_non_buying_meta_issues_are_not_outreach_candidates():
    assert is_non_buying_meta_issue("Roadmap + Owner Acceptance Board", "") is True
    assert is_non_buying_meta_issue("[EPIC] First-class watchdog", "") is True
    assert is_non_buying_meta_issue("CI failed on deploy", "") is False


def test_rank_outreach_leads_excludes_meta_coordination_issues():
    meta = make_lead(
        "99",
        "Roadmap + Owner Acceptance Board",
        ("need help", "workflow failed"),
        99,
    )
    actionable = make_lead(
        "100",
        "CI failed and need help deploying",
        ("ci failed", "need help", "deploy failed"),
        92,
    )
    ranked = rank_outreach_leads([meta, actionable], limit=10)
    assert [lead.external_id for lead in ranked] == ["100"]


def test_contact_discovery_prefers_public_email_and_rejects_private_or_invalid_values():
    from lib.profit_engine.contact_discovery import extract_public_email, extract_contact_urls

    assert extract_public_email({"email": "owner@example.com"}) == "owner@example.com"
    assert extract_public_email({"email": None}) is None
    assert extract_public_email({"email": "not-an-email"}) is None
    assert extract_contact_urls({"html_url": "https://github.com/owner", "blog": "https://example.com"}) == [
        "https://example.com",
        "https://github.com/owner",
    ]


def test_contact_route_uses_email_before_github():
    from lib.profit_engine.contact_discovery import choose_contact_route

    assert choose_contact_route("owner@example.com", "https://github.com/owner") == "email"
    assert choose_contact_route(None, "https://github.com/owner") == "github"
    assert choose_contact_route(None, None) == "none"


def test_email_outreach_message_contains_problem_specific_offer_and_opt_out():
    from lib.profit_engine.outreach import build_email_outreach_message

    lead = make_lead(
        "44",
        "CI failed and deployment is blocked",
        ("ci failed", "deploy failed"),
        92,
    )
    message = build_email_outreach_message(lead, "owner@example.com")
    assert "CI Failure Recovery" in message
    assert lead.url in message
    assert "no credentials" in message.lower()
    assert "reply" in message.lower()
