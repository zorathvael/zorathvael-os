import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SharedMemorySystem")

class SharedMemorySystem:
    def __init__(self) -> None:
        self.personal_memory: Dict[str, Dict[str, Any]] = {}
        self.department_memory: Dict[str, Dict[str, Any]] = {}
        self.project_memory: Dict[str, Dict[str, Any]] = {}
        self.organization_memory: Dict[str, Any] = {}

    def set_personal(self, worker_id: str, key: str, value: Any) -> None:
        if worker_id not in self.personal_memory:
            self.personal_memory[worker_id] = {}
        self.personal_memory[worker_id][key] = value
        logger.info(f"Personal memory updated for {worker_id}: {key}")

    def get_personal(self, worker_id: str, key: str) -> Optional[Any]:
        return self.personal_memory.get(worker_id, {}).get(key)

    def set_department(self, dept: str, key: str, value: Any) -> None:
        if dept not in self.department_memory:
            self.department_memory[dept] = {}
        self.department_memory[dept][key] = value
        logger.info(f"Department memory updated for {dept}: {key}")

    def set_org(self, key: str, value: Any) -> None:
        self.organization_memory[key] = value
        logger.info(f"Organization memory updated: {key}")
