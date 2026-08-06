import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from dotenv import load_dotenv
load_dotenv()

from lib.core_modules.ai_router.ai_router import AIRouter
from lib.core_modules.memory_engine.memory_engine import MemoryEngine
from lib.core_modules.workflow_engine.workflow_engine import WorkflowEngine

# Initialize Engines
ai_router = AIRouter()
memory_engine = MemoryEngine()
workflow_engine = WorkflowEngine()

# --- AI Router Example ---
print("\n--- AI Router Example ---")
print(ai_router.route_task("Summarize research paper", "research"))
print(ai_router.route_task("Generate code snippet", "engineering"))
print(ai_router.route_task("Write a marketing copy", "non_existent_department"))

# --- Memory Engine Example ---
print("\n--- Memory Engine Example ---")
memory_engine.store_memory("user_preference", "dark_mode")
memory_engine.store_memory("last_task", "summarize_report")
print(f"Retrieved user preference: {memory_engine.retrieve_memory('user_preference')}")
print(f"Retrieved non-existent memory: {memory_engine.retrieve_memory('temp_data')}")
print(f"All memories: {memory_engine.list_memories()}")

# --- Workflow Engine Example ---
print("\n--- Workflow Engine Example ---")
my_workflow_steps = [
    {"action": "store_memory", "key": "current_project", "value": "Zorathvael OS Development"},
    {"action": "route_ai_task", "department": "research", "task": "Find latest AI trends"},
    {"action": "retrieve_memory", "key": "current_project"},
    {"action": "route_ai_task", "department": "documentation", "task": "Draft project overview"}
]

workflow_engine.define_workflow("initial_setup_workflow", my_workflow_steps)
workflow_results = workflow_engine.execute_workflow("initial_setup_workflow")
print("Workflow Results:", workflow_results)
