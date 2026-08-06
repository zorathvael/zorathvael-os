import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntegrationEngine")

class IntegrationEngine:
    def __init__(self) -> None:
        try:
            self.integrations: Dict[str, Dict[str, Any]] = {}
            logger.info("IntegrationEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize IntegrationEngine: {e}")
            raise

    def register_integration(self, name: str, config: Dict[str, Any]) -> None:
        """Registers an external integration service configuration with validation."""
        try:
            if not name or not isinstance(name, str):
                raise ValueError("Integration name must be a valid non-empty string.")
            if not isinstance(config, dict):
                raise TypeError("Integration configuration must be a dictionary.")
            
            self.integrations[name] = config
            logger.info(f"Integration registered: {name}")
        except Exception as e:
            logger.error(f"Error registering integration '{name}': {e}")
            raise

    def get_integration(self, name: str) -> Dict[str, Any]:
        """Retrieves integration configuration securely with error protection."""
        try:
            if name not in self.integrations:
                logger.error(f"Integration not found: {name}")
                raise KeyError(f"Integration '{name}' is not registered.")
            return self.integrations[name]
        except Exception as e:
            logger.error(f"Error retrieving integration '{name}': {e}")
            raise
