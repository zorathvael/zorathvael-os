import scripts.portal_order_intake as intake


def test_service_map():
    assert intake.SERVICE_MAP["ci_failure_recovery"] == "ci_failure_recovery"
    assert intake.SERVICE_MAP["public_repo_audit"] == "public_repo_audit"
    assert intake.SERVICE_MAP["automation_blueprint"] == "automation_blueprint"


def test_process_lead_rejects_missing_or_invalid_tx(monkeypatch):
    monkeypatch.setattr(intake, "find_order_by_external_id", lambda *args, **kwargs: None)
    monkeypatch.setattr(intake, "update_lead", lambda *args, **kwargs: None)
    result = intake.process_lead({
        "id": 99,
        "fields": {
            "service": "ci_failure_recovery",
            "tx_hash": "not-a-hash",
        },
    })
    assert result["status"] == "pending"
