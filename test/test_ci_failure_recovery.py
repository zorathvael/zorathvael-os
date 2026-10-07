from lib.profit_engine.delivery import _failure_fingerprint
from lib.profit_engine.revenue import score_lead, select_offer


def test_ci_failure_intent_routes_to_outcome_product():
    score, evidence = score_lead(
        "GitHub Actions failed and I need help",
        "The workflow failed and deployment is blocked.",
    )
    assert score >= 30
    assert "workflow failed" in evidence
    assert select_offer(score, evidence).product_id == "ci_failure_recovery"


def test_ci_log_fingerprint_is_deterministic():
    fingerprint, evidence = _failure_fingerprint(
        "Run tests\nModuleNotFoundError: No module named 'requests'\nProcess completed with exit code 1"
    )
    assert fingerprint == "dependency-install"
    assert evidence == "ModuleNotFoundError"


def test_ci_failure_without_logs_does_not_claim_root_cause():
    fingerprint, _ = _failure_fingerprint("Process completed with exit code 1")
    assert fingerprint == "unclassified"
