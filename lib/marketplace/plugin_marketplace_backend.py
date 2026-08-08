import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginMarketplaceBackend")

class PluginMarketplaceBackend:
    def __init__(self) -> None:
        self.catalog: List[Dict[str, Any]] = []
        self.ratings: Dict[str, float] = {}

    def add_to_catalog(self, plugin_meta: Dict[str, Any]) -> None:
        self.catalog.append(plugin_meta)
        self.ratings[plugin_meta["id"]] = 5.0
        logger.info(f"Added plugin to marketplace catalog: {plugin_meta['id']}")

    def search_catalog(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Searching marketplace catalog for query: {query}")
        return [p for p in self.catalog if query.lower() in p.get("name", "").lower()]
