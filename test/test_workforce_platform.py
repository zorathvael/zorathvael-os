import pytest
from lib.workforce.organization_engine import OrganizationManager
from lib.workforce.enterprise_structure import setup_enterprise_organization
from lib.workforce.ai_worker_framework import EnterpriseAIWorker
from lib.workforce.workforce_communication import WorkforceCommunicationBus
from lib.workforce.shared_memory import SharedMemorySystem
from lib.workforce.mission_execution import MissionExecutionEngine
from lib.workforce.approval_system import HumanApprovalSystem
from lib.workforce.workforce_analytics import WorkforceAnalytics
from lib.workforce.enterprise_templates import EnterpriseOrganizationTemplates
from lib.workforce.business_scenarios import BusinessScenariosLibrary

def test_organization_engine():
    org = OrganizationManager()
    org.register_department("Engineering", "CTO")
    org.register_worker("w1", "Developer", "Engineering")
    org.delegate_task("w1", "w1", {"title": "Code Review"})
    org.escalate_issue("w1", "Build failure")
    app_id = org.request_approval("w1", "Deploy to Production")
    assert app_id == "app_1"

def test_enterprise_structure():
    org = setup_enterprise_organization()
    assert "Executive Board" in org.departments
    assert "Engineering" in org.departments

def test_ai_worker_framework():
    worker = EnterpriseAIWorker("w2", "Software Engineer", "Engineering", "Build SaaS")
    res = worker.execute_assigned_task({"title": "Write API"})
    assert res["status"] == "completed"

def test_workforce_communication():
    bus = WorkforceCommunicationBus()
    bus.send_message("CEO", "CTO", "task_assignment", {"title": "System Architecture"})
    msgs = bus.get_messages_for("CTO")
    assert len(msgs) == 1
    assert msgs[0]["sender"] == "CEO"

def test_shared_memory():
    mem = SharedMemorySystem()
    mem.set_personal("w1", "focus", "Backend")
    assert mem.get_personal("w1", "focus") == "Backend"
    mem.set_department("Engineering", "standards", "Clean Code")
    mem.set_org("vision", "Global Scale")

def test_mission_execution():
    engine = MissionExecutionEngine()
    engine.create_mission("m1", "SaaS Launch", "Build and launch SaaS")
    res = engine.execute_mission_pipeline("m1")
    assert res["status"] == "success"

def test_approval_system():
    approval = HumanApprovalSystem()
    approval.create_request("req_1", "w1", "Delete DB")
    approval.handle_approval("req_1", "approved")
    assert approval.requests["req_1"]["status"] == "approved"

def test_analytics():
    analytics = WorkforceAnalytics()
    report = analytics.get_analytics_report()
    assert report["status"] == "success"
    assert "completed_tasks" in report["metrics"]

def test_templates():
    template = EnterpriseOrganizationTemplates.get_template("Startup")
    assert template["template_name"] == "Startup"

def test_business_scenarios():
    scenario = BusinessScenariosLibrary.get_scenario("Build a SaaS Product")
    assert scenario["status"] == "success"
