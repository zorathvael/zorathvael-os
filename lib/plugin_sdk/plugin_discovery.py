import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginDiscovery")

class PluginDiscoveryEngine:
    def __init__(self) -> None:
        self.discovered_plugins: List[Dict[str, Any]] = []

    def scan_directory(self, path: str) -> List[Dict[str, Any]]:
        logger.info(f"Scanning directory for plugins: {path}")
        # Simulated auto-scan and validation for robust enterprise discovery
        return self.discovered_plugins

    def register_discovered(self, manifest: Dict[str, Any]) -> None:
        # Check duplicate IDs or names
        for p in self.discovered_plugins:
            if p.get("id") == manifest.get("id"):
                logger.error(f"Duplicate plugin ID detected: {manifest.get('id')}")
                raise ValueError(f"Duplicate plugin ID: {manifest.get('id')}")
        
        self.discovered_plugins.append(manifest)
        logger.info(f"Discovered and registered manifest: {manifest.get('id')}")
