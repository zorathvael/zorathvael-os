import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginPermissions")

class PluginPermissionManager:
    ALLOWED_PERMISSIONS = [
        "filesystem.read", "filesystem.write", "network",
        "github", "notion", "telegram", "gmail", "calendar", "buffer",
        "ai.openai", "ai.gemini", "ai.anthropic", "ai.openrouter",
        "memory", "workflow", "automation"
    ]

    @classmethod
    def validate_permissions(cls, permissions: List[str]) -> bool:
        for perm in permissions:
            if perm not in cls.ALLOWED_PERMISSIONS:
                logger.error(f"Unauthorized or invalid permission requested: {perm}")
                raise PermissionError(f"Invalid permission: {perm}")
        logger.info("All plugin permissions validated successfully.")
        return True
