import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReportEngine")

class ReportEngine:
    def __init__(self) -> None:
        try:
            self.reports: List[Dict[str, Any]] = []
            logger.info("ReportEngine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ReportEngine: {e}")
            raise

    def generate_report(self, title: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a structured system report with validation."""
        try:
            if not title or not isinstance(title, str):
                raise ValueError("Report title must be a valid non-empty string.")
            if not isinstance(data, dict):
                raise TypeError("Report data must be a dictionary.")

            report = {
                "title": title,
                "data": data,
                "status": "Generated"
            }
            self.reports.append(report)
            logger.info(f"Report generated successfully: {title}")
            return report
        except Exception as e:
            logger.error(f"Error generating report '{title}': {e}")
            raise

    def list_reports(self) -> List[Dict[str, Any]]:
        """Lists all generated reports with error protection."""
        try:
            return self.reports
        except Exception as e:
            logger.error(f"Error listing reports: {e}")
            return []
