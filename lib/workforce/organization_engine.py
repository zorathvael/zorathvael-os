import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrganizationEngine")

class OrganizationManager:
    def __init__(self) -> None:
        self.departments: Dict[str, Any] = {}
        self.workers: Dict[str, Any] = {}
        self.escalations: List[Dict[str, Any]] = []
        self.approvals: List[Dict[str, Any]] = []

    def register_department(self, name: str, lead: str) -> None:
        self.departments[name] = {"lead": lead, "teams": []}
        logger.info(f"Registered department '{name}' led by '{lead}'")

    def register_worker(self, worker_id: str, role: str, department: str) -> None:
        self.workers[worker_id] = {"role": role, "department": department, "status": "available"}
        logger.info(f"Registered AI worker '{worker_id}' (Role: {role}, Dept: {department})")

    def delegate_task(self, from_worker: str, to_worker: str, task: Dict[str, Any]) -> None:
        logger.info(f"Delegating task from {from_worker} to {to_worker}: {task.get('title')}")

    def escalate_issue(self, worker_id: str, issue: str) -> None:
        self.escalations.append({"worker": worker_id, "issue": issue, "status": "pending"})
        logger.warning(f"Escalation raised by {worker_id}: {issue}")

    def request_approval(self, worker_id: str, action: str) -> str:
        approval_id = f"app_{len(self.approvals) + 1}"
        self.approvals.append({"id": approval_id, "worker": worker_id, "action": action, "status": "pending"})
        logger.info(f"Approval requested ({approval_id}) by {worker_id} for: {action}")
        return approval_id
