import logging
from typing import Dict, Any, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutomationEngine")

class AutomationEngine:
    def __init__(self) -> None:
        try:
            self.tasks: Dict[str, Callable[..., Any]] = {}
            logger.info("AutomationEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize AutomationEngine: {e}")
            raise

    def register_task(self, name: str, func: Callable[..., Any]) -> None:
        """Registers an automated task with validation."""
        try:
            if not name or not isinstance(name, str):
                raise ValueError("Task name must be a valid non-empty string.")
            if not callable(func):
                raise TypeError("Task handler must be callable.")
            
            self.tasks[name] = func
            logger.info(f"Automation task registered: {name}")
        except Exception as e:
            logger.error(f"Error registering automation task '{name}': {e}")
            raise

    def trigger_task(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Triggers a registered automated task with exception protection."""
        try:
            if name not in self.tasks:
                logger.error(f"Automation task not found: {name}")
                raise ValueError(f"Task '{name}' is not registered.")
            
            logger.info(f"Triggering automation task: {name}")
            return self.tasks[name](*args, **kwargs)
        except Exception as e:
            logger.error(f"Error executing automation task '{name}': {e}")
            raise
