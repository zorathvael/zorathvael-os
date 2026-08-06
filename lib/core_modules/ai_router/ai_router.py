import os
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIRouter")

class AIRouter:
    def __init__(self) -> None:
        try:
            self.ai_models: Dict[str, Optional[str]] = {
                "command_center": os.getenv("OPENAI_API_KEY"),
                "research": os.getenv("GEMINI_API_KEY"),
                "documentation": os.getenv("CLAUDE_API_KEY"),
                "engineering": os.getenv("DEEPSEEK_API_KEY"),
                "knowledge": os.getenv("NOTEBOOKLM_API_KEY"),
            }
            logger.info("AIRouter initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize AIRouter: {e}")
            raise

    def route_task(self, task_description: str, department: str) -> str:
        """Routes a task to the appropriate AI model based on the department with full exception handling."""
        try:
            if not task_description or not isinstance(task_description, str):
                raise ValueError("Task description must be a valid non-empty string.")
            if not department or not isinstance(department, str):
                raise ValueError("Department must be a valid non-empty string.")

            if department in self.ai_models and self.ai_models[department]:
                logger.info(f"Routing task to {department} AI model.")
                return f"Task '{task_description}' processed by {department} AI."
            else:
                logger.warning(f"No AI model configured or available for department: {department}")
                return f"No AI model configured or available for department: {department}"
        except Exception as e:
            logger.error(f"Error during task routing for department '{department}': {e}")
            return f"Routing error: {str(e)}"

    def get_available_ais(self) -> List[str]:
        """Returns a list of configured AI departments."""
        try:
            return [dept for dept, key in self.ai_models.items() if key is not None]
        except Exception as e:
            logger.error(f"Error retrieving available AI models: {e}")
            return []
