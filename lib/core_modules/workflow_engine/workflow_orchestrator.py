import logging
from typing import List, Dict, Any
from lib.core_modules.ai_router.ai_client import AIClient
from lib.core_modules.memory_engine.memory_engine import MemoryEngine
from lib.core_modules.integration_engine.integration_client import ExternalIntegrationClient
from lib.core_modules.report_engine.report_engine import ReportEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowOrchestrator")

class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.ai_client = AIClient()
        self.memory = MemoryEngine()
        self.integration = ExternalIntegrationClient()
        self.report_engine = ReportEngine()

    def execute_scenario(self, scenario_id: int, user_request: str, provider: str) -> Dict[str, Any]:
        logger.info(f"Executing Workflow Scenario #{scenario_id}: {user_request}")
        try:
            # Step 1: Memory storage
            self.memory.store_memory(f"scenario_{scenario_id}_request", user_request)

            # Step 2: AI Routing
            ai_res = self.ai_client.execute_request(provider, user_request)

            # Step 3: External Integration
            int_res = self.integration.perform_action("github", "write", {"scenario": scenario_id, "prompt": user_request})

            # Step 4: Report Generation
            report = self.report_engine.generate_report(f"Scenario {scenario_id} Report", {"ai": ai_res, "integration": int_res})

            return {
                "scenario_id": scenario_id,
                "status": "success",
                "report": report
            }
        except Exception as e:
            logger.error(f"Scenario #{scenario_id} failed: {str(e)}")
            return {
                "scenario_id": scenario_id,
                "status": "error",
                "error": str(e)
            }
