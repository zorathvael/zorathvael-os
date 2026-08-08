import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ApprovalSystem")

class HumanApprovalSystem:
    def __init__(self) -> None:
        self.requests: Dict[str, Dict[str, Any]] = {}

    def create_request(self, req_id: str, worker_id: str, action: str) -> None:
        self.requests[req_id] = {
            "worker_id": worker_id,
            "action": action,
            "status": "pending"
        }
        logger.info(f"Approval request created ({req_id}) for worker {worker_id}: {action}")

    def handle_approval(self, req_id: str, decision: str) -> None:
        if req_id not in self.requests:
            raise KeyError(f"Approval request not found: {req_id}")
        
        self.requests[req_id]["status"] = decision
        logger.info(f"Approval request {req_id} updated with decision: {decision}")
