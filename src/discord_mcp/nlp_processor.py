"""Entity resolution for MCP Discord tools.

This module handles entity resolution (converting names/aliases to IDs) for Discord entities.
While the MCP client (LLM) handles intent detection, the server still needs to resolve
entity references like "general channel" to actual Discord IDs.
"""

import logging
from typing import Optional
from .server_registry.api import ServerRegistryAPI

logger = logging.getLogger(__name__)


class EntityResolver:
    """Resolves entity references to Discord IDs.
    
    This class provides a simplified interface for resolving entity references
    to Discord IDs using the ServerRegistryAPI.
    """
    
    def __init__(self, registry_api: ServerRegistryAPI):
        """Initialize with a server registry API.
        
        Args:
            registry_api: The server registry API to use for entity resolution
        """
        self.registry = registry_api
    
    async def resolve_server(self, server_reference: str) -> str:
        """Resolve a server reference to a server ID.
        
        Args:
            server_reference: Name, alias, or ID of a server
            
        Returns:
            Server ID if found, otherwise the original reference
        """
        try:
            server = self.registry.get_server(server_reference)
            if server and server.discord_id:
                logger.debug(f"Resolved server '{server_reference}' to ID '{server.discord_id}'")
                return server.discord_id
            logger.debug(f"Could not resolve server '{server_reference}'")
            return server_reference
        except Exception as e:
            logger.error(f"Error resolving server '{server_reference}': {e}")
            return server_reference
    
    async def resolve_channel(self, channel_reference: str, server_id: Optional[str] = None) -> str:
        """Resolve a channel reference to a channel ID.
        
        Args:
            channel_reference: Name, alias, or ID of a channel
            server_id: Optional server ID to scope the search
            
        Returns:
            Channel ID if found, otherwise the original reference
        """
        try:
            channel = self.registry.get_channel(channel_reference, server_id)
            if channel and channel.discord_id:
                logger.debug(f"Resolved channel '{channel_reference}' to ID '{channel.discord_id}'")
                return channel.discord_id
            logger.debug(f"Could not resolve channel '{channel_reference}'")
            return channel_reference
        except Exception as e:
            logger.error(f"Error resolving channel '{channel_reference}': {e}")
            return channel_reference
    
    async def resolve_role(self, role_reference: str, server_id: Optional[str] = None) -> str:
        """Resolve a role reference to a role ID.
        
        Args:
            role_reference: Name, alias, or ID of a role
            server_id: Optional server ID to scope the search
            
        Returns:
            Role ID if found, otherwise the original reference
        """
        try:
            role = self.registry.get_role(role_reference, server_id)
            if role and role.discord_id:
                logger.debug(f"Resolved role '{role_reference}' to ID '{role.discord_id}'")
                return role.discord_id
            logger.debug(f"Could not resolve role '{role_reference}'")
            return role_reference
        except Exception as e:
            logger.error(f"Error resolving role '{role_reference}': {e}")
            return role_reference