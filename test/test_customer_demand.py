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
