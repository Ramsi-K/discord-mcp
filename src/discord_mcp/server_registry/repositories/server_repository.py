"""
Server repository.
"""

import logging
from typing import Dict, List, Optional, Any

from ..db import DatabaseConnection
from ..models import Server, ServerPermissions

logger = logging.getLogger(__name__)


class ServerRepository:
    """
    Repository for server data.
    """

    def __init__(self, db: DatabaseConnection = None):
        """
        Initialize the ServerRepository.

        Args:
            db (DatabaseConnection, optional): The database connection.
        """
        self.db = db or DatabaseConnection()

    def get_server_by_id(self, server_id: int) -> Optional[Server]:
        """
        Get a server by ID.

        Args:
            server_id (int): The server ID.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM servers WHERE id = ?", (server_id,)
            )
            if results:
                return self._row_to_server(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting server by ID {server_id}: {e}")
            return None

    def get_server_by_discord_id(self, discord_id: str) -> Optional[Server]:
        """
        Get a server by Discord ID.

        Args:
            discord_id (str): The Discord ID.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM servers WHERE discord_id = ?", (discord_id,)
            )
            if results:
                return self._row_to_server(results[0])
            return None
        except Exception as e:
            logger.error(
                f"Error getting server by Discord ID {discord_id}: {e}"
            )
            return None

    def get_server_by_name(self, name: str) -> Optional[Server]:
        """
        Get a server by name.

        Args:
            name (str): The server name.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM servers WHERE LOWER(name) = LOWER(?)", (name,)
            )
            if results:
                return self._row_to_server(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting server by name {name}: {e}")
            return None

    def get_server_by_alias(self, alias: str) -> Optional[Server]:
        """
        Get a server by alias.

        Args:
            alias (str): The server alias.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                """
                SELECT s.* FROM servers s
                JOIN server_aliases sa ON s.id = sa.server_id
                WHERE LOWER(sa.alias) = LOWER(?)
                """,
                (alias,),
            )
            if results:
                return self._row_to_server(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting server by alias {alias}: {e}")
            return None

    def get_all_servers(self) -> List[Server]:
        """
        Get all servers.

        Returns:
            List[Server]: The servers.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM servers ORDER BY name"
            )
            return [self._row_to_server(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting all servers: {e}")
            return []

    def create_server(self, server: Server) -> Server:
        """
        Create a new server.

        Args:
            server (Server): The server to create.

        Returns:
            Server: The created server with ID.
        """
        try:
            server_id = self.db.execute_insert(
                """
                INSERT INTO servers (discord_id, name, description, icon_url, owner_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    server.discord_id,
                    server.name,
                    server.description,
                    server.icon_url,
                    server.owner_id,
                ),
            )
            server.id = server_id

            # Add aliases if any
            if hasattr(server, "aliases") and server.aliases:
                for alias in server.aliases:
                    self._add_server_alias(server_id, alias)

            return server
        except Exception as e:
            logger.error(f"Error creating server {server.name}: {e}")
            return server

    def update_server(self, server: Server) -> Server:
        """
        Update a server.

        Args:
            server (Server): The server to update.

        Returns:
            Server: The updated server.
        """
        try:
            self.db.execute_update(
                """
                UPDATE servers 
                SET name = ?, description = ?, icon_url = ?, owner_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    server.name,
                    server.description,
                    server.icon_url,
                    server.owner_id,
                    server.id,
                ),
            )
            return server
        except Exception as e:
            logger.error(f"Error updating server {server.id}: {e}")
            return server

    def delete_server(self, server_id: int) -> bool:
        """
        Delete a server.

        Args:
            server_id (int): The server ID.

        Returns:
            bool: True if the server was deleted, False otherwise.
        """
        try:
            affected_rows = self.db.execute_update(
                "DELETE FROM servers WHERE id = ?", (server_id,)
            )
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Error deleting server {server_id}: {e}")
            return False

    def _add_server_alias(self, server_id: int, alias: str) -> bool:
        """
        Add an alias to a server.

        Args:
            server_id (int): The server ID.
            alias (str): The alias.

        Returns:
            bool: True if the alias was added, False otherwise.
        """
        # This is a stub implementation
        return True

    def _update_bot_permissions(
        self, server_id: int, permissions: ServerPermissions
    ) -> bool:
        """
        Update bot permissions for a server.

        Args:
            server_id (int): The server ID.
            permissions (ServerPermissions): The permissions.

        Returns:
            bool: True if the permissions were updated, False otherwise.
        """
        try:
            # Delete existing permissions
            self.db.execute_update(
                "DELETE FROM bot_permissions WHERE server_id = ?", (server_id,)
            )

            # Insert new permissions
            permission_attrs = [
                "administrator",
                "manage_channels",
                "manage_roles",
                "manage_messages",
                "send_messages",
                "embed_links",
                "mention_everyone",
            ]

            for perm_name in permission_attrs:
                if hasattr(permissions, perm_name):
                    perm_value = getattr(permissions, perm_name)
                    self.db.execute_insert(
                        """
                        INSERT INTO bot_permissions (server_id, permission_name, permission_value)
                        VALUES (?, ?, ?)
                        """,
                        (server_id, perm_name, perm_value),
                    )

            return True
        except Exception as e:
            logger.error(
                f"Error updating bot permissions for server {server_id}: {e}"
            )
            return False

    def _row_to_server(self, row: Dict[str, Any]) -> Server:
        """
        Convert a database row to a Server object.

        Args:
            row (Dict[str, Any]): The database row.

        Returns:
            Server: The Server object.
        """
        server = Server(
            discord_id=row["discord_id"],
            name=row["name"],
            description=row.get("description"),
            icon_url=row.get("icon_url"),
            owner_id=row.get("owner_id"),
        )
        server.id = row["id"]
        return server

    def upsert_server(self, server: Server) -> Server:
        """
        Insert or update a server (upsert operation).

        Args:
            server (Server): The server to upsert.

        Returns:
            Server: The upserted server with ID.
        """
        # Check if server exists by discord_id
        existing = self.get_server_by_discord_id(server.discord_id)
        if existing:
            # Update existing server
            server.id = existing.id
            return self.update_server(server)
        else:
            # Create new server
            return self.create_server(server)
