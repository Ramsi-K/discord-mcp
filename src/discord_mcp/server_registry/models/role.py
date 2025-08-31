"""
Role model for server registry.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class Role:
    """
    Represents a Discord role in the registry.
    """

    discord_id: str
    server_id: int
    name: str
    color: Optional[int] = None
    position: Optional[int] = None
    mentionable: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    id: Optional[int] = None
    aliases: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.aliases is None:
            self.aliases = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """
        Create a Role instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing role data.

        Returns:
            Role: The created instance.
        """
        return cls(
            id=data.get("id"),
            discord_id=data["discord_id"],
            server_id=data["server_id"],
            name=data["name"],
            color=data.get("color"),
            position=data.get("position"),
            mentionable=data.get("mentionable", False),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            aliases=data.get("aliases", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Role instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "id": self.id,
            "discord_id": self.discord_id,
            "server_id": self.server_id,
            "name": self.name,
            "color": self.color,
            "position": self.position,
            "mentionable": self.mentionable,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "aliases": self.aliases,
        }
