import pytest
import os
from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine
from lib.core_modules.workflow_engine.workflow_engine import WorkflowEngine
from lib.core_modules.automation_engine.automation_engine import AutomationEngine
from lib.core_modules.integration_engine.integration_engine import IntegrationEngine
from lib.core_modules.report_engine.report_engine import ReportEngine
from lib.core_modules.mission_center.mission_center import MissionCenter
from lib.core_modules.dashboard.dashboard import Dashboard

def test_ai_router():
    os.environ["OPENAI_API_KEY"] = "fake-key"
    router = AIRouter()
    result = router.route_task("Test task", "command_center")
    assert "processed by command_center AI" in result
    assert "command_center" in router.get_available_ais()

def test_memory_engine():
    memory = MemoryEngine()
    memory.store_memory("test_key", "test_value")
    assert memory.retrieve_memory("test_key") == "test_value"
    assert "test_key" in memory.list_memories()
    assert memory.retrieve_memory("non_existent") == "Memory not found"

def test_workflow_engine():
    workflow = WorkflowEngine()
    steps = [
        {"action": "store_memory", "key": "workflow_test", "value": "success"},
        {"action": "retrieve_memory", "key": "workflow_test"}
    ]
    workflow.define_workflow("test_flow", steps)
    results = workflow.execute_workflow("test_flow")
    assert len(results) == 2
    assert "Memory stored: workflow_test" in results[0]
    assert "Memory retrieved: workflow_test = success" in results[1]

def test_automation_engine():
    auto = AutomationEngine()
    auto.register_task("sample", lambda x: x * 2)
    assert auto.trigger_task("sample", 5) == 10

def test_integration_engine():
    integration = IntegrationEngine()
    integration.register_integration("api_service", {"url": "https://api.example.com"})
    config = integration.get_integration("api_service")
    assert config["url"] == "https://api.example.com"

def test_report_engine():
    report_engine = ReportEngine()
    report = report_engine.generate_report("System Health", {"cpu": "10%"})
    assert report["title"] == "System Health"
    assert report["status"] == "Generated"
    assert len(report_engine.list_reports()) == 1

def test_mission_center():
    mission_center = MissionCenter()
    mission = mission_center.create_mission("Alpha", ["Deploy Core"])
    assert mission["mission_name"] == "Alpha"
    assert len(mission_center.get_missions()) == 1

def test_dashboard():
    dashboard = Dashboard()
    metrics = dashboard.get_system_metrics()
    assert metrics["status"] == "Operational"
    assert metrics["active_modules"] == 8
