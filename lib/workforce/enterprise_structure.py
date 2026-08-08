import logging
from lib.workforce.organization_engine import OrganizationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnterpriseStructure")

def setup_enterprise_organization() -> OrganizationManager:
    org = OrganizationManager()

    # Executive Board
    org.register_department("Executive Board", lead="CEO")
    org.register_worker("exec_ceo", "CEO", "Executive Board")
    org.register_worker("exec_coo", "COO", "Executive Board")
    org.register_worker("exec_cto", "CTO", "Executive Board")
    org.register_worker("exec_cfo", "CFO", "Executive Board")
    org.register_worker("exec_cmo", "CMO", "Executive Board")

    # Departments
    departments = [
        "Engineering", "Marketing", "Sales", "Finance", 
        "Research", "Operations", "Customer Success", 
        "Legal", "Security", "Human Resources"
    ]

    for dept in departments:
        org.register_department(dept, lead=f"{dept} Manager")
        org.register_worker(f"worker_{dept.lower().replace(' ', '_')}", f"{dept} Specialist", dept)

    logger.info("Enterprise organizational structure initialized successfully.")
    return org
