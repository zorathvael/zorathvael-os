import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkforceCommunication")

class WorkforceCommunicationBus:
    def __init__(self) -> None:
        self.messages: List[Dict[str, Any]] = []

    def send_message(self, sender: str, recipient: str, msg_type: str, content: Dict[str, Any]) -> None:
        message = {
            "sender": sender,
            "recipient": recipient,
            "type": msg_type,
            "content": content
        }
        self.messages.append(message)
        logger.info(f"Message sent from {sender} to {recipient} [Type: {msg_type}]")

    def get_messages_for(self, recipient: str) -> List[Dict[str, Any]]:
        return [m for m in self.messages if m["recipient"] == recipient or m["recipient"] == "broadcast"]
