"""
Channel repository.
"""

import logging
from typing import Dict, List, Optional, Any

from ..db import DatabaseConnection
from ..models import Channel, ChannelPermissions

logger = logging.getLogger(__name__)


class ChannelRepository:
    """
    Repository for channel data.
    """

    def __init__(self, db: DatabaseConnection = None):
        """
        Initialize the ChannelRepository.

        Args:
            db (DatabaseConnection, optional): The database connection.
        """
        self.db = db or DatabaseConnection()

    def get_channel_by_id(self, channel_id: int) -> Optional[Channel]:
        """
        Get a channel by ID.

        Args:
            channel_id (int): The channel ID.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM channels WHERE id = ?", (channel_id,)
            )
            if results:
                return self._row_to_channel(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting channel by ID {channel_id}: {e}")
            return None

    def get_channel_by_discord_id(self, discord_id: str) -> Optional[Channel]:
        """
        Get a channel by Discord ID.

        Args:
            discord_id (str): The Discord ID.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM channels WHERE discord_id = ?", (discord_id,)
            )
            if results:
                return self._row_to_channel(results[0])
            return None
        except Exception as e:
            logger.error(
                f"Error getting channel by Discord ID {discord_id}: {e}"
            )
            return None

    def get_channel_by_name(
        self, name: str, server_id: Optional[int] = None
    ) -> Optional[Channel]:
        """
        Get a channel by name.

        Args:
            name (str): The channel name.
            server_id (Optional[int], optional): The server ID to filter by.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        try:
            if server_id:
                results = self.db.execute_query(
                    "SELECT * FROM channels WHERE LOWER(name) = LOWER(?) AND server_id = ?",
                    (name, server_id),
                )
            else:
                results = self.db.execute_query(
                    "SELECT * FROM channels WHERE LOWER(name) = LOWER(?)",
                    (name,),
                )

            if results:
                return self._row_to_channel(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting channel by name {name}: {e}")
            return None

    def get_channel_by_alias(
        self, alias: str, server_id: Optional[int] = None
    ) -> Optional[Channel]:
        """
        Get a channel by alias.

        Args:
            alias (str): The channel alias.
            server_id (Optional[int], optional): The server ID to filter by.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        try:
            if server_id:
                results = self.db.execute_query(
                    """
                    SELECT c.* FROM channels c
                    JOIN channel_aliases ca ON c.id = ca.channel_id
                    WHERE LOWER(ca.alias) = LOWER(?) AND c.server_id = ?
                    """,
                    (alias, server_id),
                )
            else:
                results = self.db.execute_query(
                    """
                    SELECT c.* FROM channels c
                    JOIN channel_aliases ca ON c.id = ca.channel_id
                    WHERE LOWER(ca.alias) = LOWER(?)
                    """,
                    (alias,),
                )

            if results:
                return self._row_to_channel(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting channel by alias {alias}: {e}")
            return None

    def get_channels_by_server_id(self, server_id: int) -> List[Channel]:
        """
        Get all channels for a server.

        Args:
            server_id (int): The server ID.

        Returns:
            List[Channel]: The channels.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM channels WHERE server_id = ? ORDER BY position, name",
                (server_id,),
            )
            return [self._row_to_channel(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting channels for server {server_id}: {e}")
            return []

    def create_channel(self, channel: Channel) -> Channel:
        """
        Create a new channel.

        Args:
            channel (Channel): The channel to create.

        Returns:
            Channel: The created channel with ID.
        """
        try:
            channel_id = self.db.execute_insert(
                """
                INSERT INTO channels (discord_id, server_id, name, type, topic, position, parent_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    channel.discord_id,
                    channel.server_id,
                    channel.name,
                    (
                        channel.type.value
                        if hasattr(channel.type, "value")
                        else str(channel.type)
                    ),
                    channel.topic,
                    channel.position,
                    channel.parent_id,
                ),
            )
            channel.id = channel_id

            # Add aliases if any
            if hasattr(channel, "aliases") and channel.aliases:
                for alias in channel.aliases:
                    self._add_channel_alias(channel_id, alias)

            return channel
        except Exception as e:
            logger.error(f"Error creating channel {channel.name}: {e}")
            return channel

    def update_channel(self, channel: Channel) -> Channel:
        """
        Update a channel.

        Args:
            channel (Channel): The channel to update.

        Returns:
            Channel: The updated channel.
        """
        try:
            self.db.execute_update(
                """
                UPDATE channels 
                SET name = ?, type = ?, topic = ?, position = ?, parent_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    channel.name,
                    (
                        channel.type.value
                        if hasattr(channel.type, "value")
                        else str(channel.type)
                    ),
                    channel.topic,
                    channel.position,
                    channel.parent_id,
                    channel.id,
                ),
            )
            return channel
        except Exception as e:
            logger.error(f"Error updating channel {channel.id}: {e}")
            return channel

    def delete_channel(self, channel_id: int) -> bool:
        """
        Delete a channel.

        Args:
            channel_id (int): The channel ID.

        Returns:
            bool: True if the channel was deleted, False otherwise.
        """
        try:
            affected_rows = self.db.execute_update(
                "DELETE FROM channels WHERE id = ?", (channel_id,)
            )
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Error deleting channel {channel_id}: {e}")
            return False

    def _add_channel_alias(self, channel_id: int, alias: str) -> bool:
        """
        Add an alias to a channel.

        Args:
            channel_id (int): The channel ID.
            alias (str): The alias.

        Returns:
            bool: True if the alias was added, False otherwise.
        """
        try:
            self.db.execute_insert(
                "INSERT OR IGNORE INTO channel_aliases (channel_id, alias) VALUES (?, ?)",
                (channel_id, alias),
            )
            return True
        except Exception as e:
            logger.error(
                f"Error adding channel alias {alias} for channel {channel_id}: {e}"
            )
            return False

    def _update_channel_permissions(
        self, channel_id: int, permissions: ChannelPermissions
    ) -> bool:
        """
        Update channel permissions.

        Args:
            channel_id (int): The channel ID.
            permissions (ChannelPermissions): The permissions.

        Returns:
            bool: True if the permissions were updated, False otherwise.
        """
        try:
            # Delete existing permissions
            self.db.execute_update(
                "DELETE FROM channel_permissions WHERE channel_id = ?",
                (channel_id,),
            )

            # Insert new permissions
            permission_attrs = [
                "send_messages",
                "read_messages",
                "manage_messages",
                "embed_links",
                "attach_files",
                "mention_everyone",
                "use_external_emojis",
            ]

            for perm_name in permission_attrs:
                if hasattr(permissions, perm_name):
                    perm_value = getattr(permissions, perm_name)
                    self.db.execute_insert(
                        """
                        INSERT INTO channel_permissions (channel_id, permission_name, permission_value)
                        VALUES (?, ?, ?)
                        """,
                        (channel_id, perm_name, perm_value),
                    )

            return True
        except Exception as e:
            logger.error(
                f"Error updating channel permissions for channel {channel_id}: {e}"
            )
            return False

    def _row_to_channel(self, row: Dict[str, Any]) -> Channel:
        """
        Convert a database row to a Channel object.

        Args:
            row (Dict[str, Any]): The database row.

        Returns:
            Channel: The Channel object.
        """
        from ..models import ChannelType

        channel = Channel(
            discord_id=row["discord_id"],
            server_id=row["server_id"],
            name=row["name"],
            type=ChannelType.from_string(row["type"]),
            topic=row.get("topic"),
            position=row.get("position"),
            parent_id=row.get("parent_id"),
        )
        channel.id = row["id"]
        return channel

    def upsert_channel(self, channel: Channel) -> Channel:
        """
        Insert or update a channel (upsert operation).

        Args:
            channel (Channel): The channel to upsert.

        Returns:
            Channel: The upserted channel with ID.
        """
        # Check if channel exists by discord_id
        existing = self.get_channel_by_discord_id(channel.discord_id)
        if existing:
            # Update existing channel
            channel.id = existing.id
            return self.update_channel(channel)
        else:
            # Create new channel
            return self.create_channel(channel)
