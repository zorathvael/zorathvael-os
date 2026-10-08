from scripts.core_orchestrator import build_stages


def test_core_orchestrator_has_full_master_pipeline():
    names = [stage.name for stage in build_stages()]
    assert names == [
        "revenue_acquisition",
        "contact_discovery",
        "qualified_outreach",
        "github_response_observation",
        "email_response_observation",
        "payment_verification",
        "delivery_recovery",
        "agentmail_delivery",
        "revenue_learning",
    ]
