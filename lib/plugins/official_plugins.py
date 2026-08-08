import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OfficialPluginsLibrary")

OFFICIAL_PLUGIN_NAMES = [
    "GitHub", "Notion", "Telegram", "Buffer", 
    "Google Drive", "Google Docs", "Gmail", "Google Calendar",
    "OpenAI", "Gemini", "Anthropic", "OpenRouter",
    "Slack", "Discord", "Webhook"
]

class OfficialPluginsLibrary:
    @staticmethod
    def get_plugin_manifest(name: str) -> Dict[str, Any]:
        if name not in OFFICIAL_PLUGIN_NAMES:
            raise ValueError(f"Official plugin not found: {name}")
        
        return {
            "name": name,
            "id": f"com.zorathvael.{name.lower().replace(' ', '_')}",
            "version": "1.0.0",
            "author": "Zorathvael OS Official Team",
            "description": f"Official production-ready plugin for {name}.",
            "license": "MIT",
            "dependencies": [],
            "required_permissions": [name.lower().replace(' ', '_')],
            "compatible_zorathvael_version": ">=1.0.0",
            "entry_point": f"lib.plugins.{name.lower().replace(' ', '_')}.plugin",
            "configuration_schema": {"type": "object"},
            "default_settings": {}
        }
