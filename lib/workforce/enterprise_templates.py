import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnterpriseTemplates")

ORGANIZATION_TEMPLATES = [
    "Startup", "Agency", "Consulting Firm", "Software Company",
    "Marketing Agency", "Content Studio", "Research Lab", "Enterprise Company"
]

class EnterpriseOrganizationTemplates:
    @staticmethod
    def get_template(template_name: str) -> Dict[str, Any]:
        if template_name not in ORGANIZATION_TEMPLATES:
            raise ValueError(f"Organization template not found: {template_name}")
        
        logger.info(f"Loading organization template: {template_name}")
        return {
            "template_name": template_name,
            "structure": "Executive Board + Core Departments",
            "default_workers": ["CEO", "CTO", "CFO", "CMO", "Engineering Lead", "Marketing Lead"],
            "default_workflows": ["Product Launch", "Marketing Campaign", "Business Audit"]
        }
