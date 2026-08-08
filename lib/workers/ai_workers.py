import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIWorkersLibrary")

class AIWorker:
    def __init__(self, role: str, goals: List[str], responsibilities: List[str], prompt_template: str) -> None:
        self.role = role
        self.goals = goals
        self.responsibilities = responsibilities
        self.prompt_template = prompt_template

class AIWorkersLibrary:
    ROLES = [
        "CEO", "COO", "CTO", "CFO", "CMO", 
        "Sales Manager", "Marketing Manager", "Research Analyst", 
        "Project Manager", "Product Manager", "Software Architect", 
        "Software Engineer", "QA Engineer", "DevOps Engineer", 
        "Security Engineer", "Data Analyst", "Copywriter", 
        "Technical Writer", "Customer Success", "Business Consultant"
    ]

    def get_worker(self, role: str) -> AIWorker:
        if role not in self.ROLES:
            raise ValueError(f"Worker role not found: {role}")
        
        return AIWorker(
            role=role,
            goals=[f"Excellence in {role} operations"],
            responsibilities=[f"Execute {role} core duties"],
            prompt_template=f"You are the {role} of Zorathvael OS. Execute tasks with precision."
        )
