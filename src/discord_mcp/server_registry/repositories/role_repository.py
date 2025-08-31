"""
Role repository.
"""

import logging
from typing import Dict, List, Optional, Any

from ..db import DatabaseConnection
from ..models import Role

logger = logging.getLogger(__name__)


class RoleRepository:
    """
    Repository for role data.
    """

    def __init__(self, db: DatabaseConnection = None):
        """
        Initialize the RoleRepository.

        Args:
            db (DatabaseConnection, optional): The database connection.
        """
        self.db = db or DatabaseConnection()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get a role by ID.

        Args:
            role_id (int): The role ID.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM roles WHERE id = ?", (role_id,)
            )
            if results:
                return self._row_to_role(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting role by ID {role_id}: {e}")
            return None

    def get_role_by_discord_id(self, discord_id: str) -> Optional[Role]:
        """
        Get a role by Discord ID.

        Args:
            discord_id (str): The Discord ID.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM roles WHERE discord_id = ?", (discord_id,)
            )
            if results:
                return self._row_to_role(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting role by Discord ID {discord_id}: {e}")
            return None

    def get_role_by_name(
        self, name: str, server_id: Optional[int] = None
    ) -> Optional[Role]:
        """
        Get a role by name.

        Args:
            name (str): The role name.
            server_id (Optional[int], optional): The server ID to filter by.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        try:
            if server_id:
                results = self.db.execute_query(
                    "SELECT * FROM roles WHERE LOWER(name) = LOWER(?) AND server_id = ?",
                    (name, server_id),
                )
            else:
                results = self.db.execute_query(
                    "SELECT * FROM roles WHERE LOWER(name) = LOWER(?)", (name,)
                )

            if results:
                return self._row_to_role(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting role by name {name}: {e}")
            return None

    def get_role_by_alias(
        self, alias: str, server_id: Optional[int] = None
    ) -> Optional[Role]:
        """
        Get a role by alias.

        Args:
            alias (str): The role alias.
            server_id (Optional[int], optional): The server ID to filter by.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        try:
            if server_id:
                results = self.db.execute_query(
                    """
                    SELECT r.* FROM roles r
                    JOIN role_aliases ra ON r.id = ra.role_id
                    WHERE LOWER(ra.alias) = LOWER(?) AND r.server_id = ?
                    """,
                    (alias, server_id),
                )
            else:
                results = self.db.execute_query(
                    """
                    SELECT r.* FROM roles r
                    JOIN role_aliases ra ON r.id = ra.role_id
                    WHERE LOWER(ra.alias) = LOWER(?)
                    """,
                    (alias,),
                )

            if results:
                return self._row_to_role(results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting role by alias {alias}: {e}")
            return None

    def get_roles_by_server_id(self, server_id: int) -> List[Role]:
        """
        Get all roles for a server.

        Args:
            server_id (int): The server ID.

        Returns:
            List[Role]: The roles.
        """
        try:
            results = self.db.execute_query(
                "SELECT * FROM roles WHERE server_id = ? ORDER BY position DESC, name",
                (server_id,),
            )
            return [self._row_to_role(row) for row in results]
        except Exception as e:
            logger.error(f"Error getting roles for server {server_id}: {e}")
            return []

    def create_role(self, role: Role) -> Role:
        """
        Create a new role.

        Args:
            role (Role): The role to create.

        Returns:
            Role: The created role with ID.
        """
        try:
            role_id = self.db.execute_insert(
                """
                INSERT INTO roles (discord_id, server_id, name, color, position, mentionable)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    role.discord_id,
                    role.server_id,
                    role.name,
                    role.color,
                    role.position,
                    role.mentionable,
                ),
            )
            role.id = role_id

            # Add aliases if any
            if hasattr(role, "aliases") and role.aliases:
                for alias in role.aliases:
                    self._add_role_alias(role_id, alias)

            return role
        except Exception as e:
            logger.error(f"Error creating role {role.name}: {e}")
            return role

    def update_role(self, role: Role) -> Role:
        """
        Update a role.

        Args:
            role (Role): The role to update.

        Returns:
            Role: The updated role.
        """
        try:
            self.db.execute_update(
                """
                UPDATE roles 
                SET name = ?, color = ?, position = ?, mentionable = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    role.name,
                    role.color,
                    role.position,
                    role.mentionable,
                    role.id,
                ),
            )
            return role
        except Exception as e:
            logger.error(f"Error updating role {role.id}: {e}")
            return role

    def delete_role(self, role_id: int) -> bool:
        """
        Delete a role.

        Args:
            role_id (int): The role ID.

        Returns:
            bool: True if the role was deleted, False otherwise.
        """
        try:
            affected_rows = self.db.execute_update(
                "DELETE FROM roles WHERE id = ?", (role_id,)
            )
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Error deleting role {role_id}: {e}")
            return False

    def _add_role_alias(self, role_id: int, alias: str) -> bool:
        """
        Add an alias to a role.

        Args:
            role_id (int): The role ID.
            alias (str): The alias.

        Returns:
            bool: True if the alias was added, False otherwise.
        """
        try:
            self.db.execute_insert(
                "INSERT OR IGNORE INTO role_aliases (role_id, alias) VALUES (?, ?)",
                (role_id, alias),
            )
            return True
        except Exception as e:
            logger.error(
                f"Error adding role alias {alias} for role {role_id}: {e}"
            )
            return False

    def _row_to_role(self, row: Dict[str, Any]) -> Role:
        """
        Convert a database row to a Role object.

        Args:
            row (Dict[str, Any]): The database row.

        Returns:
            Role: The Role object.
        """
        role = Role(
            discord_id=row["discord_id"],
            server_id=row["server_id"],
            name=row["name"],
            color=row.get("color", 0),
            position=row.get("position", 0),
            mentionable=bool(row.get("mentionable", False)),
        )
        role.id = row["id"]
        return role

    def upsert_role(self, role: Role) -> Role:
        """
        Insert or update a role (upsert operation).

        Args:
            role (Role): The role to upsert.

        Returns:
            Role: The upserted role with ID.
        """
        # Check if role exists by discord_id
        existing = self.get_role_by_discord_id(role.discord_id)
        if existing:
            # Update existing role
            role.id = existing.id
            return self.update_role(role)
        else:
            # Create new role
            return self.create_role(role)
