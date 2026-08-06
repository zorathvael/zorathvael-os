import logging
from typing import Dict, List, Any, Optional
from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowEngine")

class WorkflowEngine:
    def __init__(self):
        self.ai_router = AIRouter()
        self.memory_engine = MemoryEngine()
        self.workflows: Dict[str, List[Dict[str, Any]]] = {}

    def define_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]) -> None:
        """Defines a new workflow with a sequence of steps."""
        self.workflows[workflow_name] = steps
        logger.info(f"Workflow '{workflow_name}' defined with {len(steps)} steps.")

    def execute_workflow(self, workflow_name: str, initial_context: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Executes a defined workflow."""
        if workflow_name not in self.workflows:
            logger.error(f"Workflow '{workflow_name}' not found.")
            return [f"Workflow '{workflow_name}' not found."]

        current_context = initial_context if initial_context is not None else {}
        results: List[Any] = []

        logger.info(f"Executing workflow: {workflow_name}")
        for i, step in enumerate(self.workflows[workflow_name]):
            action = step.get('action')
            logger.info(f"  Step {i+1}: {action}")
            
            if action == 'route_ai_task':
                department = step.get('department')
                task = step.get('task')
                if department and task:
                    ai_result = self.ai_router.route_task(task, department)
                    results.append(ai_result)
                    current_context[f'step_{i+1}_result'] = ai_result
                else:
                    results.append("Error: Missing department or task for AI routing.")
            elif action == 'store_memory':
                key = step.get('key')
                value = step.get('value')
                if key and value:
                    self.memory_engine.store_memory(key, value)
                    results.append(f"Memory stored: {key}")
                else:
                    results.append("Error: Missing key or value for memory storage.")
            elif action == 'retrieve_memory':
                key = step.get('key')
                if key:
                    retrieved_value = self.memory_engine.retrieve_memory(key)
                    results.append(f"Memory retrieved: {key} = {retrieved_value}")
                    current_context[f'step_{i+1}_result'] = retrieved_value
                else:
                    results.append("Error: Missing key for memory retrieval.")
            else:
                results.append(f"Unknown action: {action}")
        
        logger.info(f"Workflow '{workflow_name}' completed.")
        return results
