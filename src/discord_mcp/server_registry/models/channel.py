"""
Channel model for server registry.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class ChannelType(Enum):
    """
    Enum representing the different types of Discord channels.
    """

    TEXT = "text"
    VOICE = "voice"
    CATEGORY = "category"
    ANNOUNCEMENT = "announcement"
    FORUM = "forum"
    STAGE = "stage"
    THREAD = "thread"

    @classmethod
    def from_string(cls, value: str) -> "ChannelType":
        """
        Create a ChannelType from a string.

        Args:
            value (str): The string value.

        Returns:
            ChannelType: The corresponding enum value.
        """
        try:
            return cls(value.lower())
        except ValueError:
            return cls.TEXT


@dataclass
class ChannelPermissions:
    """
    Represents the bot's permissions in a channel.
    """

    can_view: bool = True
    can_send: bool = True
    can_embed: bool = True
    can_attach: bool = True
    can_mention_everyone: bool = False
    can_manage: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChannelPermissions":
        """
        Create a ChannelPermissions instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing permission data.

        Returns:
            ChannelPermissions: The created instance.
        """
        return cls(
            can_view=data.get("can_view", True),
            can_send=data.get("can_send", True),
            can_embed=data.get("can_embed", True),
            can_attach=data.get("can_attach", True),
            can_mention_everyone=data.get("can_mention_everyone", False),
            can_manage=data.get("can_manage", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ChannelPermissions instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "can_view": self.can_view,
            "can_send": self.can_send,
            "can_embed": self.can_embed,
            "can_attach": self.can_attach,
            "can_mention_everyone": self.can_mention_everyone,
            "can_manage": self.can_manage,
        }


@dataclass
class Channel:
    """
    Represents a Discord channel in the registry.
    """

    discord_id: str
    server_id: int
    name: str
    type: ChannelType = ChannelType.TEXT
    topic: Optional[str] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    id: Optional[int] = None
    aliases: List[str] = None
    permissions: ChannelPermissions = None

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = ChannelType.from_string(self.type)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.aliases is None:
            self.aliases = []
        if self.permissions is None:
            self.permissions = ChannelPermissions()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Channel":
        """
        Create a Channel instance from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary containing channel data.

        Returns:
            Channel: The created instance.
        """
        channel_type = (
            ChannelType.from_string(data["type"])
            if "type" in data
            else ChannelType.TEXT
        )
        permissions = (
            ChannelPermissions.from_dict(data.get("permissions", {}))
            if "permissions" in data
            else None
        )

        return cls(
            id=data.get("id"),
            discord_id=data["discord_id"],
            server_id=data["server_id"],
            name=data["name"],
            type=channel_type,
            topic=data.get("topic"),
            position=data.get("position"),
            parent_id=data.get("parent_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            aliases=data.get("aliases", []),
            permissions=permissions,
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Channel instance to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation.
        """
        return {
            "id": self.id,
            "discord_id": self.discord_id,
            "server_id": self.server_id,
            "name": self.name,
            "type": self.type.value,
            "topic": self.topic,
            "position": self.position,
            "parent_id": self.parent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "aliases": self.aliases,
            "permissions": (
                self.permissions.to_dict() if self.permissions else None
            ),
        }
