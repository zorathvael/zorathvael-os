from lib.profit_engine.customer_demand import classify_customer_response
from lib.profit_engine.revenue import extract_problem_context


def test_response_classifier_separates_interest_objections_and_disinterest():
    assert classify_customer_response("Interested, please send details") == "request_for_details"
    assert classify_customer_response("This is too expensive for our budget") == "price_objection"
    assert classify_customer_response("We already fixed this issue") == "fit_objection"
    assert classify_customer_response("No thanks, not interested") == "not_interested"


def test_neutral_or_empty_comments_are_not_demand_responses():
    assert classify_customer_response("") == "neutral"
    assert classify_customer_response("I pushed a commit to update the docs") == "neutral"


def test_problem_context_prefers_problem_sentence_and_strips_html_comments():
    body = (
        "General background paragraph that explains the project context and architecture.\n\n"
        "The deployment fails with a timeout after the build succeeds, blocking every release.\n\n"
        "<!-- internal note -->"
    )
    context = extract_problem_context("Deploy broken", body)
    assert "deployment fails with a timeout" in context
    assert "internal note" not in context


def test_problem_context_falls_back_to_issue_title():
    assert extract_problem_context("CI build failed", "") == "CI build failed"


def test_outreach_message_uses_issue_context_and_a_specific_value_proposition():
    from lib.profit_engine.outreach import build_outreach_message
    from lib.profit_engine.revenue import Lead

    lead = Lead(
        source="test",
        external_id="7",
        title="Deployment fails",
        url="https://github.com/example/repo/issues/7",
        repository="example/repo",
        author="maintainer",
        evidence=("deployment failed",),
        score=90,
        offer_id="ci_failure_recovery",
        contact_url="https://github.com/maintainer",
        discovered_at="2026-10-09T00:00:00+00:00",
        problem_context="The deployment fails with a timeout after the build succeeds.",
    )
    message = build_outreach_message(lead)
    assert lead.problem_context in message
    assert "failing workflow" in message.lower() or "error fingerprint" in message.lower()
    assert "10 USDT" in message
    assert "Would this outcome be useful" in message


def test_demand_snapshot_marks_small_samples_inconclusive():
    from lib.profit_engine.outreach import OutreachEvent
    from lib.profit_engine.revenue_learning import build_learning_snapshot

    events = [
        OutreachEvent(
            event_id=f"sent:{i}",
            event_type="outreach_sent",
            lead_url=f"https://github.com/example/repo/issues/{i}",
            repository="example/repo",
            issue_number=str(i),
            offer_id="ci_failure_recovery",
            occurred_at="2026-10-09T00:00:00+00:00",
            metadata={"channel": "github_issue_comment"},
        )
        for i in range(4)
    ]
    snapshot = build_learning_snapshot(events=events, orders=[])
    assert snapshot["offer_stats"]["ci_failure_recovery"]["demand_status"] == "insufficient_outreach_sample"


def test_rendered_draft_includes_a_working_order_portal_url(tmp_path):
    from lib.profit_engine.revenue import Lead, render_drafts

    lead = Lead(
        source="test",
        external_id="8",
        title="CI workflow fails on deploy",
        url="https://github.com/example/repo/issues/8",
        repository="example/repo",
        author="maintainer",
        evidence=("workflow failed",),
        score=90,
        offer_id="ci_failure_recovery",
        contact_url="https://github.com/maintainer",
        discovered_at="2026-10-09T00:00:00+00:00",
        problem_context="The CI workflow fails during deployment and blocks releases.",
    )
    output = tmp_path / "drafts.md"
    render_drafts([lead], str(output))
    draft = output.read_text(encoding="utf-8")
    assert "https://zorathvael.github.io/zorathvael-os/order/?service=ci_failure_recovery" in draft
