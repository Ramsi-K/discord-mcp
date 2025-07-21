"""
Server Registry Wrapper for Discord MCP server.
Provides a clean interface between the MCP server and the server registry.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)


class ServerRegistry:
    """
    Wrapper for the server registry API.
    Provides a clean interface for the MCP server to interact with the server registry.
    """

    def __init__(self, discord_bot):
        """
        Initialize the ServerRegistry.

        Args:
            discord_bot: The Discord bot instance.
        """
        self.discord_bot = discord_bot
        self.api = None
        self.current_user_id = "system"

    async def initialize(self) -> bool:
        """
        Initialize the server registry.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        try:
            # Get database path from environment variable
            db_path = os.getenv("MCP_DISCORD_DB_PATH")
            
            # Import the initialization module
            from server_registry.init import init_server_registry
            
            # Initialize the registry
            result = init_server_registry(discord_client=self.discord_bot, db_path=db_path)
            
            if result["success"]:
                self.api = result["api"]
                logger.info(f"Server registry initialized successfully using database at {result.get('db_path')}")
                return True
            else:
                logger.error(f"Failed to initialize server registry: {result.get('message')}")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize server registry: {str(e)}")
            return False

    def set_current_user(self, user_id: str) -> None:
        """
        Set the current user ID for context tracking.

        Args:
            user_id (str): The user ID.
        """
        self.current_user_id = user_id
        if self.api:
            self.api.set_current_user(user_id)

    def clear_current_user(self) -> None:
        """
        Clear the current user ID for context tracking.
        """
        self.current_user_id = "system"
        if self.api:
            self.api.clear_current_user()

    async def update_registry(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the server registry.

        Args:
            server_id (Optional[str], optional): The server ID to update, or None to update all servers.

        Returns:
            Dict[str, Any]: The result of the update operation.
        """
        if not self.api:
            return {"error": "Server registry API not initialized"}

        try:
            success = self.api.update_registry(server_id)
            if success:
                return {
                    "success": True,
                    "message": f"Registry updated successfully for {'all servers' if server_id is None else f'server {server_id}'}",
                }
            else:
                return {
                    "error": f"Failed to update registry for {'all servers' if server_id is None else f'server {server_id}'}",
                }
        except Exception as e:
            logger.error(f"Error updating registry: {str(e)}")
            return {"error": f"Error updating registry: {str(e)}"}

    def track_context(self, entity_type: str, entity_id: Union[int, str]) -> bool:
        """
        Track an entity in the conversation context.

        Args:
            entity_type (str): The entity type ('server', 'channel', or 'role').
            entity_id (Union[int, str]): The entity ID.

        Returns:
            bool: True if the entity was tracked, False otherwise.
        """
        if not self.api:
            return False

        try:
            # Convert string ID to int if needed
            if isinstance(entity_id, str):
                entity_id = int(entity_id)

            return self.api.track_context(self.current_user_id, entity_type, entity_id)
        except Exception as e:
            logger.error(f"Error tracking context: {str(e)}")
            return False