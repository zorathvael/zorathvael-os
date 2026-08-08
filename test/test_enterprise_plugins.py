import pytest
from lib.plugin_sdk.enterprise_framework import PluginManager
from lib.plugin_sdk.plugin_manifest import PluginManifestValidator
from lib.plugin_sdk.plugin_permissions import PluginPermissionManager
from lib.plugin_sdk.plugin_sandbox import PluginSandbox
from lib.plugin_sdk.plugin_event_bus import PluginEventBus
from lib.marketplace.plugin_marketplace_backend import PluginMarketplaceBackend

def test_plugin_lifecycle_and_manager():
    manager = PluginManager()
    manifest = {
        "name": "Test Plugin",
        "id": "com.zorathvael.test",
        "version": "1.0.0",
        "author": "Tester",
        "description": "Test",
        "license": "MIT",
        "dependencies": [],
        "required_permissions": ["workflow"],
        "compatible_zorathvael_version": ">=1.0.0",
        "entry_point": "test.main",
        "configuration_schema": {},
        "default_settings": {}
    }
    manager.install("com.zorathvael.test", manifest)
    assert manager.health_monitor.check_health("com.zorathvael.test") == "healthy"
    manager.enable("com.zorathvael.test")
    manager.uninstall("com.zorathvael.test")

def test_manifest_validator():
    valid_manifest = {
        "name": "Test", "id": "test", "version": "1.0.0", "author": "A",
        "description": "D", "license": "MIT", "dependencies": [],
        "required_permissions": [], "compatible_zorathvael_version": ">=1.0",
        "entry_point": "e", "configuration_schema": {}, "default_settings": {}
    }
    assert PluginManifestValidator.validate(valid_manifest) is True

def test_permissions():
    assert PluginPermissionManager.validate_permissions(["workflow", "github"]) is True

def test_sandbox():
    def dummy_func():
        return "success"
    res = PluginSandbox.execute_safely(dummy_func)
    assert res["status"] == "success"
    assert res["result"] == "success"

def test_event_bus():
    bus = PluginEventBus()
    events_caught = []
    bus.subscribe("Task Completed", lambda data: events_caught.append(data))
    bus.publish("Task Completed", {"task_id": 123})
    assert len(events_caught) == 1
    assert events_caught[0]["task_id"] == 123

def test_marketplace_backend():
    backend = PluginMarketplaceBackend()
    backend.add_to_catalog({"id": "com.zorathvael.test", "name": "Test Plugin"})
    results = backend.search_catalog("Test")
    assert len(results) == 1
