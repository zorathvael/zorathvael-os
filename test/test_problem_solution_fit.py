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
