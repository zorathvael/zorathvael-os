import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnterpriseFramework")

class PluginHealthMonitor:
    def __init__(self) -> None:
        self.health_status: Dict[str, str] = {}

    def check_health(self, plugin_id: str) -> str:
        status = self.health_status.get(plugin_id, "healthy")
        logger.info(f"Health check for plugin '{plugin_id}': {status}")
        return status

    def set_status(self, plugin_id: str, status: str) -> None:
        self.health_status[plugin_id] = status

class PluginLifecycleManager:
    def __init__(self) -> None:
        self.states: Dict[str, str] = {}

    def transition(self, plugin_id: str, new_state: str) -> None:
        old_state = self.states.get(plugin_id, "unloaded")
        self.states[plugin_id] = new_state
        logger.info(f"Plugin '{plugin_id}' transitioned from {old_state} to {new_state}")

class PluginManager:
    def __init__(self) -> None:
        self.installed_plugins: Dict[str, Dict[str, Any]] = {}
        self.lifecycle = PluginLifecycleManager()
        self.health_monitor = PluginHealthMonitor()

    def install(self, plugin_id: str, manifest: Dict[str, Any]) -> None:
        self.installed_plugins[plugin_id] = manifest
        self.lifecycle.transition(plugin_id, "installed")
        self.health_monitor.set_status(plugin_id, "healthy")
        logger.info(f"Successfully installed plugin: {plugin_id}")

    def uninstall(self, plugin_id: str) -> None:
        if plugin_id in self.installed_plugins:
            del self.installed_plugins[plugin_id]
            self.lifecycle.transition(plugin_id, "uninstalled")
            logger.info(f"Successfully uninstalled plugin: {plugin_id}")

    def enable(self, plugin_id: str) -> None:
        self.lifecycle.transition(plugin_id, "enabled")

    def disable(self, plugin_id: str) -> None:
        self.lifecycle.transition(plugin_id, "disabled")

    def update(self, plugin_id: str, new_manifest: Dict[str, Any]) -> None:
        self.installed_plugins[plugin_id] = new_manifest
        self.lifecycle.transition(plugin_id, "updated")
        logger.info(f"Successfully updated plugin: {plugin_id}")

    def reload(self, plugin_id: str) -> None:
        self.lifecycle.transition(plugin_id, "reloaded")

    def restart(self, plugin_id: str) -> None:
        self.lifecycle.transition(plugin_id, "restarted")
