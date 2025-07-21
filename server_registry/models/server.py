"""
Server model for server registry.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class ServerPermissions:
    """
    Represents the bot's permissions in a server.
    """

    is_admin: bool = False
    can_manage_channels: bool = False
    can_manage_roles: bool = False
    can_manage_messages: bool = False
    can_mention_everyone: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerPermissions":
        """
        Create a ServerPermissions instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing permission data.

        Returns:
            ServerPermissions: The created instance.
        """
        return cls(
            is_admin=data.get("is_admin", False),
            can_manage_channels=data.get("can_manage_channels", False),
            can_manage_roles=data.get("can_manage_roles", False),
            can_manage_messages=data.get("can_manage_messages", False),
            can_mention_everyone=data.get("can_mention_everyone", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ServerPermissions instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "is_admin": self.is_admin,
            "can_manage_channels": self.can_manage_channels,
            "can_manage_roles": self.can_manage_roles,
            "can_manage_messages": self.can_manage_messages,
            "can_mention_everyone": self.can_mention_everyone,
        }


@dataclass
class Server:
    """
    Represents a Discord server in the registry.
    """

    discord_id: str
    name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    id: Optional[int] = None
    aliases: List[str] = None
    bot_permissions: ServerPermissions = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.aliases is None:
            self.aliases = []
        if self.bot_permissions is None:
            self.bot_permissions = ServerPermissions()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Server":
        """
        Create a Server instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing server data.

        Returns:
            Server: The created instance.
        """
        permissions = (
            ServerPermissions.from_dict(data.get("bot_permissions", {}))
            if "bot_permissions" in data
            else None
        )

        return cls(
            id=data.get("id"),
            discord_id=data["discord_id"],
            name=data["name"],
            description=data.get("description"),
            icon_url=data.get("icon_url"),
            owner_id=data.get("owner_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            aliases=data.get("aliases", []),
            bot_permissions=permissions,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Server instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "id": self.id,
            "discord_id": self.discord_id,
            "name": self.name,
            "description": self.description,
            "icon_url": self.icon_url,
            "owner_id": self.owner_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "aliases": self.aliases,
            "bot_permissions": (
                self.bot_permissions.to_dict()
                if self.bot_permissions
                else None
            ),
        }
