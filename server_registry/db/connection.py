"""
Database connection for server registry.
"""

import os
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Singleton class for managing SQLite database connections.
    Provides methods for executing SQL queries and managing transactions.
    """

    _instance = None
    _connection = None

    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
            
            # Check environment variable first, then parameter, then default
            if not db_path:
                db_path = os.getenv("MCP_DISCORD_DB_PATH")
            
            if not db_path:
                # Default to a file in the user's home directory
                home_dir = os.path.expanduser("~")
                db_dir = os.path.join(home_dir, ".mcp_discord")
                os.makedirs(db_dir, exist_ok=True)
                db_path = os.path.join(db_dir, "server_registry.db")
            
            cls._instance._db_path = db_path
            logger.info(f"Using database at: {db_path}")
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a connection to the SQLite database.

        Returns:
            sqlite3.Connection: The database connection.
        """
        if self._connection is None:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)

            # Connect to the database
            self._connection = sqlite3.connect(self._db_path)

            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")

            # Configure connection
            self._connection.row_factory = sqlite3.Row

        return self._connection

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.

        Args:
            query (str): The SQL query.
            params (Tuple, optional): The query parameters. Defaults to ().

        Returns:
            List[Dict[str, Any]]: The query results.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return results

    def execute_insert(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an insert query and return the last inserted row ID.

        Args:
            query (str): The SQL query.
            params (Tuple, optional): The query parameters. Defaults to ().

        Returns:
            int: The last inserted row ID.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id

    def execute_update(self, query: str, params: Tuple = ()) -> int:
        """
        Execute an update query and return the number of affected rows.

        Args:
            query (str): The SQL query.
            params (Tuple, optional): The query parameters. Defaults to ().

        Returns:
            int: The number of affected rows.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows

    def execute_script(self, script: str) -> None:
        """
        Execute a SQL script.

        Args:
            script (str): The SQL script.
        """
        conn = self.get_connection()
        conn.executescript(script)
        conn.commit()