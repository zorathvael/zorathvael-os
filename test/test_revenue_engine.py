from lib.profit_engine.revenue import Lead, make_opportunity, score_lead, select_offer


def test_high_intent_lead_scores_above_low_intent():
    high, evidence = score_lead("Need help automate manual workflow", "Looking for API integration and webhook automation")
    low, _ = score_lead("Question about documentation", "How do I install this?")
    assert high > low
    assert "automation" in evidence
    assert select_offer(high, evidence).product_id == "automation_blueprint"


def test_revenue_opportunity_uses_measured_prior_as_estimate():
    lead = Lead("test", "1", "Need automation", "https://example.test", "owner/repo", "owner", ("automation",), 80, "public_repo_audit", "https://github.com/owner", "now")
    opportunity = make_opportunity(lead, prior_conversion=0.02)
    assert opportunity.expected_value == 10.0
    assert opportunity.cost == 0.0
    assert opportunity.evidence["estimated"] is True
    assert 0.01 <= opportunity.probability <= 0.20


def test_generic_bug_issue_is_not_a_sales_lead():
    score, _ = score_lead("API crash", "Manual workaround is possible")
    assert score == 0
