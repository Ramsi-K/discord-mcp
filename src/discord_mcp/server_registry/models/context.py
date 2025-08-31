"""
Context model for server registry.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class ConversationContext:
    """
    Represents a conversation context in the registry.
    """

    user_id: str
    server_id: Optional[int] = None
    channel_id: Optional[int] = None
    role_id: Optional[int] = None
    created_at: datetime = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """
        Create a ConversationContext instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing context data.

        Returns:
            ConversationContext: The created instance.
        """
        return cls(
            id=data.get("id"),
            user_id=data["user_id"],
            server_id=data.get("server_id"),
            channel_id=data.get("channel_id"),
            role_id=data.get("role_id"),
            created_at=data.get("created_at"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ConversationContext instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "server_id": self.server_id,
            "channel_id": self.channel_id,
            "role_id": self.role_id,
            "created_at": self.created_at,
        }
