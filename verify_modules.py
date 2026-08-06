from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine
from lib.core_modules.workflow_engine.workflow_engine import WorkflowEngine
from lib.core_modules.automation_engine.automation_engine import AutomationEngine
from lib.core_modules.integration_engine.integration_engine import IntegrationEngine
from lib.core_modules.report_engine.report_engine import ReportEngine
from lib.core_modules.mission_center.mission_center import MissionCenter
from lib.core_modules.dashboard.dashboard import Dashboard

def verify_all():
    print("Initializing all core modules...")
    router = AIRouter()
    memory = MemoryEngine()
    workflow = WorkflowEngine()
    automation = AutomationEngine()
    integration = IntegrationEngine()
    report = ReportEngine()
    mission = MissionCenter()
    dashboard = Dashboard()
    
    print("All core modules instantiated successfully!")
    print(f"Dashboard metrics: {dashboard.get_system_metrics()}")

if __name__ == "__main__":
    verify_all()
