import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MissionCenter")

class MissionCenter:
    def __init__(self) -> None:
        try:
            self.missions: List[Dict[str, Any]] = []
            logger.info("MissionCenter initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MissionCenter: {e}")
            raise

    def create_mission(self, mission_name: str, objectives: List[str]) -> Dict[str, Any]:
        """Creates a new operational mission for AI agents with validation."""
        try:
            if not mission_name or not isinstance(mission_name, str):
                raise ValueError("Mission name must be a valid non-empty string.")
            if not isinstance(objectives, list) or not objectives:
                raise ValueError("Mission objectives must be a non-empty list of strings.")

            mission = {
                "mission_name": mission_name,
                "objectives": objectives,
                "status": "Pending"
            }
            self.missions.append(mission)
            logger.info(f"Mission created successfully: {mission_name}")
            return mission
        except Exception as e:
            logger.error(f"Error creating mission '{mission_name}': {e}")
            raise

    def get_missions(self) -> List[Dict[str, Any]]:
        """Returns all registered missions with error protection."""
        try:
            return self.missions
        except Exception as e:
            logger.error(f"Error retrieving missions: {e}")
            return []
