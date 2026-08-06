from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine

class WorkflowEngine:
    def __init__(self):
        self.ai_router = AIRouter()
        self.memory_engine = MemoryEngine()
        self.workflows = {}

    def define_workflow(self, workflow_name: str, steps: list):
        """Defines a new workflow with a sequence of steps."""
        self.workflows[workflow_name] = steps
        print(f"Workflow '{workflow_name}' defined with {len(steps)} steps.")

    def execute_workflow(self, workflow_name: str, initial_context: dict = None):
        """Executes a defined workflow."""
        if workflow_name not in self.workflows:
            return f"Workflow '{workflow_name}' not found."

        current_context = initial_context if initial_context is not None else {}
        results = []

        print(f"Executing workflow: {workflow_name}")
        for i, step in enumerate(self.workflows[workflow_name]):
            print(f"  Step {i+1}: {step['action']}")
            if step['action'] == 'route_ai_task':
                department = step.get('department')
                task = step.get('task')
                if department and task:
                    ai_result = self.ai_router.route_task(task, department)
                    results.append(ai_result)
                    current_context[f'step_{i+1}_result'] = ai_result
                else:
                    results.append("Error: Missing department or task for AI routing.")
            elif step['action'] == 'store_memory':
                key = step.get('key')
                value = step.get('value')
                if key and value:
                    self.memory_engine.store_memory(key, value)
                    results.append(f"Memory stored: {key}")
                else:
                    results.append("Error: Missing key or value for memory storage.")
            elif step['action'] == 'retrieve_memory':
                key = step.get('key')
                if key:
                    retrieved_value = self.memory_engine.retrieve_memory(key)
                    results.append(f"Memory retrieved: {key} = {retrieved_value}")
                    current_context[f'step_{i+1}_result'] = retrieved_value
                else:
                    results.append("Error: Missing key for memory retrieval.")
            else:
                results.append(f"Unknown action: {step['action']}")
        
        print(f"Workflow '{workflow_name}' completed.")
        return results
