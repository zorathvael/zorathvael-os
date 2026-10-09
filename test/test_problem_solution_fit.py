from lib.profit_engine.revenue import select_offer


def test_ci_failure_maps_to_recovery_only_when_failure_evidence_exists():
    offer = select_offer(80, ("workflow failed", "build failed"))
    assert offer is not None
    assert offer.product_id == "ci_failure_recovery"


def test_explicit_automation_implementation_need_maps_to_blueprint():
    offer = select_offer(75, ("how to automate", "manual process"))
    assert offer is not None
    assert offer.product_id == "automation_blueprint"


def test_explicit_audit_or_bottleneck_need_maps_to_audit():
    offer = select_offer(65, ("bottleneck", "audit"))
    assert offer is not None
    assert offer.product_id == "public_repo_audit"


def test_generic_help_request_does_not_get_forced_into_a_product():
    assert select_offer(80, ("need help", "api")) is None


def test_low_quality_signal_does_not_get_a_product_even_with_category_keywords():
    assert select_offer(20, ("workflow failed",)) is None


def test_manual_repository_intake_does_not_assign_an_unrelated_product(monkeypatch):
    from scripts import ingest_repository_request

    monkeypatch.setattr(
        ingest_repository_request,
        "_github_json",
        lambda url, token="": {"description": "A generic API toolkit"},
    )
    monkeypatch.setattr(ingest_repository_request, "append_unique", lambda record, path: True)
    monkeypatch.setattr(ingest_repository_request, "append_lead", lambda lead, path="data/revenue_leads.jsonl": True)

    result = ingest_repository_request.ingest(
        "https://github.com/example/api-toolkit",
        context="Need help with our API",
    )
    assert result["qualified"] is False
    assert result["status"] == "needs_problem_clarification"
    assert result["offer_id"] is None
    assert result["lead_created"] is False


def test_ranked_legacy_lead_is_reassigned_to_the_evidence_matched_offer():
    from lib.profit_engine.revenue import Lead, rank_outreach_leads

    lead = Lead(
        source="test",
        external_id="88",
        title="GitHub Actions workflow failed",
        url="https://github.com/example/repo/issues/88",
        repository="example/repo",
        author="maintainer",
        evidence=("workflow failed", "build failed"),
        score=90,
        offer_id="automation_blueprint",
        contact_url="https://github.com/maintainer",
        discovered_at="2026-10-09T00:00:00+00:00",
    )
    ranked = rank_outreach_leads([lead])
    assert len(ranked) == 1
    assert ranked[0].offer_id == "ci_failure_recovery"
