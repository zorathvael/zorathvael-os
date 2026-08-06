import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MemoryEngine")

class MemoryEngine:
    def __init__(self) -> None:
        try:
            self.memory_store: Dict[str, Any] = {}
            logger.info("MemoryEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MemoryEngine: {e}")
            raise

    def store_memory(self, key: str, value: Any) -> None:
        """Stores a piece of information in memory with full exception handling."""
        try:
            if not key or not isinstance(key, str):
                raise ValueError("Memory key must be a valid non-empty string.")
            self.memory_store[key] = value
            logger.info(f"Memory stored successfully: {key}")
        except Exception as e:
            logger.error(f"Error storing memory for key '{key}': {e}")
            raise

    def retrieve_memory(self, key: str) -> Any:
        """Retrieves information from memory with full exception handling."""
        try:
            if not key or not isinstance(key, str):
                raise ValueError("Memory key must be a valid non-empty string.")
            if self.memory_store is None or key not in self.memory_store:
                logger.warning(f"Memory not found for key: {key}")
                return "Memory not found"
            return self.memory_store[key]
        except Exception as e:
            logger.error(f"Error retrieving memory for key '{key}': {e}")
            raise

    def list_memories(self) -> List[str]:
        """Lists all stored memory keys with error protection."""
        try:
            if self.memory_store is None:
                return []
            return list(self.memory_store.keys())
        except Exception as e:
            logger.error(f"Error listing memories: {e}")
            return []
