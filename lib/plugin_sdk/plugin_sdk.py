import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginSDK")

class BasePlugin(ABC):
    def __init__(self, name: str, version: str) -> None:
        self.name = name
        self.version = version
        self.config: Dict[str, Any] = {}
        self.permissions: List[str] = []

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass

class PluginRegistry:
    def __init__(self) -> None:
        self.plugins: Dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        self.plugins[plugin.name] = plugin
        logger.info(f"Plugin registered: {plugin.name} (v{plugin.version})")

    def get_plugin(self, name: str) -> BasePlugin:
        if name not in self.plugins:
            raise KeyError(f"Plugin not found: {name}")
        return self.plugins[name]

class PluginLoader:
    @staticmethod
    def load_plugin(plugin_class: type, config: Dict[str, Any]) -> BasePlugin:
        plugin = plugin_class()
        plugin.initialize(config)
        logger.info(f"Plugin loaded and initialized successfully: {plugin.name}")
        return plugin
