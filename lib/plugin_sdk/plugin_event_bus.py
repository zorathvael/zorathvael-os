import logging
from typing import Dict, List, Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PluginEventBus")

class PluginEventBus:
    def __init__(self) -> None:
        self.listeners: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        logger.info(f"Subscribed to event type: {event_type}")

    def publish(self, event_type: str, data: Any) -> None:
        logger.info(f"Publishing event: {event_type}")
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {str(e)}")
