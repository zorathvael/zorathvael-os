import logging
from lib.plugin_sdk.plugin_sdk import PluginRegistry, PluginLoader, BasePlugin
from lib.integrations.official_integrations import OfficialIntegrationManager
from lib.marketplace.workflow_marketplace import WorkflowMarketplace
from lib.workers.ai_workers import AIWorkersLibrary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuickStartDemo")

def main():
    logger.info("Initializing Zorathvael OS DX Onboarding Kit Demo...")

    # 1. Test Plugin SDK
    class SamplePlugin(BasePlugin):
        def initialize(self, config): self.config = config
        def execute(self, payload): return {"status": "ok"}
    
    registry = PluginRegistry()
    plugin = PluginLoader.load_plugin(SamplePlugin, {"mode": "demo"})
    registry.register(plugin)

    # 2. Test Official Integrations
    integrations = OfficialIntegrationManager()
    res_int = integrations.execute_integration("github", "create_issue", {"title": "Test Issue"})
    logger.info(f"Integration Result: {res_int}")

    # 3. Test Workflow Marketplace
    marketplace = WorkflowMarketplace()
    res_wf = marketplace.execute_marketplace_workflow("Content Marketing", {"topic": "AI Automation"})
    logger.info(f"Workflow Result: {res_wf}")

    # 4. Test AI Workers
    workers = AIWorkersLibrary()
    ceo = workers.get_worker("CEO")
    logger.info(f"AI Worker Loaded: {ceo.role}")

    logger.info("Zorathvael OS Onboarding Kit Demo completed successfully!")

if __name__ == "__main__":
    main()
