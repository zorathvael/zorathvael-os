import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginManifest")

class PluginManifestValidator:
    REQUIRED_FIELDS = [
        "name", "id", "version", "author", "description", 
        "license", "dependencies", "required_permissions", 
        "compatible_zorathvael_version", "entry_point", 
        "configuration_schema", "default_settings"
    ]

    @classmethod
    def validate(cls, manifest: Dict[str, Any]) -> bool:
        for field in cls.REQUIRED_FIELDS:
            if field not in manifest:
                logger.error(f"Manifest validation failed: missing required field '{field}'")
                raise ValueError(f"Missing required manifest field: {field}")
        
        logger.info(f"Plugin manifest for '{manifest.get('id')}' validated successfully.")
        return True
