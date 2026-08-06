# Zorathvael OS — API Reference

## Core Engines API

### AIRouter
- `route_task(task_description: str, department: str) -> str`: Routes a task to the appropriate AI provider.
- `get_available_ais() -> list`: Returns list of configured AI departments.

### MemoryEngine
- `store_memory(key: str, value: str) -> None`: Stores a key-value pair in memory.
- `retrieve_memory(key: str) -> str`: Retrieves value for a given key.
- `list_memories() -> list`: Lists all stored memory keys.

### WorkflowEngine
- `define_workflow(workflow_name: str, steps: list) -> None`: Defines a workflow sequence.
- `execute_workflow(workflow_name: str, initial_context: dict) -> list`: Executes the workflow steps.
