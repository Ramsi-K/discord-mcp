"""
API for server registry.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from .models import Server, Channel, Role, ConversationContext
from .services import ServerRegistryService, ContextManagerService

logger = logging.getLogger(__name__)


class ServerRegistryAPI(ABC):
    """
    API for server registry.
    """

    @abstractmethod
    def get_server(
        self, reference: str, context: Optional[ConversationContext] = None
    ) -> Optional[Server]:
        """
        Get a server by reference (name, alias, or ID).

        Args:
            reference (str): The server reference.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_channel(
        self,
        reference: str,
        server_reference: Optional[str] = None,
        context: Optional[ConversationContext] = None,
    ) -> Optional[Channel]:
        """
        Get a channel by reference (name, alias, or ID).

        Args:
            reference (str): The channel reference.
            server_reference (Optional[str], optional): The server reference to limit the search to.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_role(
        self,
        reference: str,
        server_reference: Optional[str] = None,
        context: Optional[ConversationContext] = None,
    ) -> Optional[Role]:
        """
        Get a role by reference (name, alias, or ID).

        Args:
            reference (str): The role reference.
            server_reference (Optional[str], optional): The server reference to limit the search to.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        pass

    @abstractmethod
    def update_registry(self, server_reference: Optional[str] = None) -> bool:
        """
        Update the registry.

        Args:
            server_reference (Optional[str], optional): The server reference to update, or None to update all servers.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        pass

    @abstractmethod
    def check_permission(self, server_reference: str, permission: str) -> bool:
        """
        Check if the bot has a specific permission in a server.

        Args:
            server_reference (str): The server reference.
            permission (str): The permission to check.

        Returns:
            bool: True if the bot has the permission, False otherwise.
        """
        pass

    @abstractmethod
    def check_channel_permission(
        self, channel_reference: str, server_reference: str, permission: str
    ) -> bool:
        """
        Check if the bot has a specific permission in a channel.

        Args:
            channel_reference (str): The channel reference.
            server_reference (str): The server reference.
            permission (str): The permission to check.

        Returns:
            bool: True if the bot has the permission, False otherwise.
        """
        pass

    @abstractmethod
    def track_context(
        self, user_id: str, entity_type: str, reference: str
    ) -> bool:
        """
        Track an entity in the conversation context.

        Args:
            user_id (str): The user ID.
            entity_type (str): The entity type ('server', 'channel', or 'role').
            reference (str): The entity reference.

        Returns:
            bool: True if the entity was tracked, False otherwise.
        """
        pass

    @abstractmethod
    def set_current_user(self, user_id: str) -> None:
        """
        Set the current user ID for context tracking.

        Args:
            user_id (str): The user ID.
        """
        pass

    @abstractmethod
    def clear_current_user(self) -> None:
        """
        Clear the current user ID for context tracking.
        """
        pass


class ServerRegistryAPIImpl(ServerRegistryAPI):
    """
    Implementation of the Server Registry API.
    """

    def __init__(
        self,
        server_registry_service: ServerRegistryService = None,
        context_manager_service: ContextManagerService = None,
        discord_client: Any = None,
    ):
        """
        Initialize the ServerRegistryAPIImpl.

        Args:
            server_registry_service (ServerRegistryService, optional): The server registry service to use.
            context_manager_service (ContextManagerService, optional): The context manager service to use.
            discord_client (Any, optional): The Discord client to use for API calls.
        """
        self.server_registry_service = (
            server_registry_service or ServerRegistryService()
        )
        self.context_manager_service = (
            context_manager_service or ContextManagerService()
        )
        self.discord_client = discord_client
        self.current_user_id = None

    def get_server(
        self, reference: str, context: Optional[ConversationContext] = None
    ) -> Optional[Server]:
        """
        Get a server by reference (name, alias, or ID).

        Args:
            reference (str): The server reference.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Server]: The server if found, None otherwise.
        """
        # This is a stub implementation
        # In a real implementation, we would:
        # 1. Try to get the server by ID
        # 2. Try to get the server by name
        # 3. Try to get the server by alias
        # 4. If context is provided, try to get the server from context

        # For now, just create a dummy server
        if self.discord_client:
            for guild in self.discord_client.guilds:
                if reference.lower() in guild.name.lower() or reference == str(
                    guild.id
                ):
                    return Server(
                        discord_id=str(guild.id),
                        name=guild.name,
                    )

        return None

    def get_channel(
        self,
        reference: str,
        server_reference: Optional[str] = None,
        context: Optional[ConversationContext] = None,
    ) -> Optional[Channel]:
        """
        Get a channel by reference (name, alias, or ID).

        Args:
            reference (str): The channel reference.
            server_reference (Optional[str], optional): The server reference to limit the search to.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Channel]: The channel if found, None otherwise.
        """
        # This is a stub implementation
        # In a real implementation, we would:
        # 1. Try to get the channel by ID
        # 2. If server_reference is provided, get the server and then search its channels
        # 3. Try to get the channel by name
        # 4. Try to get the channel by alias
        # 5. If context is provided, try to get the channel from context

        # For now, just create a dummy channel
        if self.discord_client:
            # If server_reference is provided, limit search to that server
            if server_reference:
                server = self.get_server(server_reference, context)
                if server:
                    guild = self.discord_client.get_guild(
                        int(server.discord_id)
                    )
                    if guild:
                        for channel in guild.channels:
                            if (
                                reference.lower() in channel.name.lower()
                                or reference == str(channel.id)
                            ):
                                return Channel(
                                    discord_id=str(channel.id),
                                    server_id=int(server.id or 0),
                                    name=channel.name,
                                    type=str(channel.type),
                                )
            else:
                # Search all servers
                for guild in self.discord_client.guilds:
                    for channel in guild.channels:
                        if (
                            reference.lower() in channel.name.lower()
                            or reference == str(channel.id)
                        ):
                            return Channel(
                                discord_id=str(channel.id),
                                server_id=0,  # We don't have a server ID in this case
                                name=channel.name,
                                type=str(channel.type),
                            )

        return None

    def get_role(
        self,
        reference: str,
        server_reference: Optional[str] = None,
        context: Optional[ConversationContext] = None,
    ) -> Optional[Role]:
        """
        Get a role by reference (name, alias, or ID).

        Args:
            reference (str): The role reference.
            server_reference (Optional[str], optional): The server reference to limit the search to.
            context (Optional[ConversationContext], optional): The conversation context.

        Returns:
            Optional[Role]: The role if found, None otherwise.
        """
        # This is a stub implementation
        # In a real implementation, we would:
        # 1. Try to get the role by ID
        # 2. If server_reference is provided, get the server and then search its roles
        # 3. Try to get the role by name
        # 4. Try to get the role by alias
        # 5. If context is provided, try to get the role from context

        # For now, just create a dummy role
        if self.discord_client:
            # If server_reference is provided, limit search to that server
            if server_reference:
                server = self.get_server(server_reference, context)
                if server:
                    guild = self.discord_client.get_guild(
                        int(server.discord_id)
                    )
                    if guild:
                        for role in guild.roles:
                            if (
                                reference.lower() in role.name.lower()
                                or reference == str(role.id)
                            ):
                                return Role(
                                    discord_id=str(role.id),
                                    server_id=int(server.id or 0),
                                    name=role.name,
                                    color=role.color.value,
                                    position=role.position,
                                    mentionable=role.mentionable,
                                )
            else:
                # Search all servers
                for guild in self.discord_client.guilds:
                    for role in guild.roles:
                        if (
                            reference.lower() in role.name.lower()
                            or reference == str(role.id)
                        ):
                            return Role(
                                discord_id=str(role.id),
                                server_id=0,  # We don't have a server ID in this case
                                name=role.name,
                                color=role.color.value,
                                position=role.position,
                                mentionable=role.mentionable,
                            )

        return None

    def update_registry(self, server_reference: Optional[str] = None) -> bool:
        """
        Update the registry.

        Args:
            server_reference (Optional[str]): The server reference to update, or None to update all servers.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        # If we don't have a Discord client, we can't update the registry
        if not self.discord_client:
            return False

        try:
            if server_reference:
                # Resolve the server reference
                server = self.get_server(server_reference)
                if not server:
                    return False

                # Get the Discord guild data
                discord_guild = self.discord_client.get_guild(
                    int(server.discord_id)
                )
                if not discord_guild:
                    return False

                # Update the registry for this server
                return self.server_registry_service.update_server_registry(
                    server.id, discord_guild
                )
            else:
                # Get all Discord guilds
                # Note: discord.py's Client doesn't have get_guilds(), it has guilds property
                discord_guilds = self.discord_client.guilds

                # Update the registry for all servers
                return (
                    self.server_registry_service.update_all_server_registries(
                        discord_guilds
                    )
                )
        except Exception as e:
            print(f"Error updating registry: {e}")
            return False

    def check_permission(self, server_reference: str, permission: str) -> bool:
        """
        Check if the bot has a specific permission in a server.

        Args:
            server_reference (str): The server reference.
            permission (str): The permission to check.

        Returns:
            bool: True if the bot has the permission, False otherwise.
        """
        # This is a stub implementation
        return True

    def check_channel_permission(
        self, channel_reference: str, server_reference: str, permission: str
    ) -> bool:
        """
        Check if the bot has a specific permission in a channel.

        Args:
            channel_reference (str): The channel reference.
            server_reference (str): The server reference.
            permission (str): The permission to check.

        Returns:
            bool: True if the bot has the permission, False otherwise.
        """
        # This is a stub implementation
        return True

    def track_context(
        self, user_id: str, entity_type: str, entity_id: int
    ) -> bool:
        """
        Track an entity in the conversation context.

        Args:
            user_id (str): The user ID.
            entity_type (str): The entity type ('server', 'channel', or 'role').
            entity_id (int): The entity ID.

        Returns:
            bool: True if the entity was tracked, False otherwise.
        """
        return self.context_manager_service.track_entity(
            user_id, entity_type, entity_id
        )

    def set_current_user(self, user_id: str) -> None:
        """
        Set the current user ID for context tracking.

        Args:
            user_id (str): The user ID.
        """
        self.current_user_id = user_id

    def clear_current_user(self) -> None:
        """
        Clear the current user ID for context tracking.
        """
        self.current_user_id = None
