"""
Server registry service.
"""

import logging
from typing import Dict, List, Optional, Any

from ..models import Server, Channel, Role, ChannelType
from ..repositories import ServerRepository, ChannelRepository, RoleRepository

logger = logging.getLogger(__name__)


class ServerRegistryService:
    """
    Service for managing the server registry.
    """

    def __init__(
        self,
        server_repo: ServerRepository = None,
        channel_repo: ChannelRepository = None,
        role_repo: RoleRepository = None,
    ):
        """
        Initialize the ServerRegistryService.

        Args:
            server_repo (ServerRepository, optional): The server repository.
            channel_repo (ChannelRepository, optional): The channel repository.
            role_repo (RoleRepository, optional): The role repository.
        """
        self.server_repo = server_repo or ServerRepository()
        self.channel_repo = channel_repo or ChannelRepository()
        self.role_repo = role_repo or RoleRepository()

    def register_server(self, discord_guild: Any) -> Server:
        """
        Register a Discord server in the registry.

        Args:
            discord_guild (Any): The Discord guild object.

        Returns:
            Server: The registered server.
        """
        try:
            # For now, just create a simple server object
            server = Server(
                discord_id=str(discord_guild.id),
                name=discord_guild.name,
            )

            # Generate some basic aliases
            server.aliases = [
                server.name.lower(),
                server.name.lower().replace(" ", ""),
            ]

            return server
        except Exception as e:
            print(f"Error registering server: {e}")
            # Return a dummy server in case of error
            return Server(
                discord_id="0",
                name="Unknown Server",
            )

    def update_server_registry(
        self, server_id: int, discord_guild: Any
    ) -> bool:
        """
        Update the server registry for a specific server.

        Args:
            server_id (int): The server ID.
            discord_guild (Any): The Discord guild object.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        # This is a stub implementation
        return True

    def update_all_server_registries(self, discord_guilds: List[Any]) -> bool:
        """
        Update the server registry for all servers.

        Args:
            discord_guilds (List[Any]): The Discord guild objects.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            for guild in discord_guilds:
                # Register or update the server
                self.register_server(guild)
            return True
        except Exception as e:
            print(f"Error updating all server registries: {e}")
            return False

    def generate_server_aliases(self, server: Server) -> List[str]:
        """
        Generate aliases for a server.

        Args:
            server (Server): The server.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Add the server name
        aliases.append(server.name.lower())

        # Add the server name without spaces
        aliases.append(server.name.lower().replace(" ", ""))

        # Add the server name with "server" suffix if not already present
        if "server" not in server.name.lower():
            aliases.append(f"{server.name.lower()} server")

        return aliases

    def generate_channel_aliases(self, channel: Channel) -> List[str]:
        """
        Generate aliases for a channel.

        Args:
            channel (Channel): The channel.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Add the channel name
        aliases.append(channel.name.lower())

        # Add the channel name without spaces
        aliases.append(channel.name.lower().replace(" ", ""))

        # Add the channel name with "channel" suffix if not already present
        if "channel" not in channel.name.lower():
            aliases.append(f"{channel.name.lower()} channel")

        # Add special aliases based on channel type
        if channel.type == ChannelType.ANNOUNCEMENT:
            aliases.append("announcements")
            aliases.append("announcement")
        elif channel.type == ChannelType.VOICE:
            aliases.append("voice")

        return aliases

    def generate_role_aliases(self, role: Role) -> List[str]:
        """
        Generate aliases for a role.

        Args:
            role (Role): The role.

        Returns:
            List[str]: The generated aliases.
        """
        aliases = []

        # Add the role name
        aliases.append(role.name.lower())

        # Add the role name without spaces
        aliases.append(role.name.lower().replace(" ", ""))

        # Add the role name with "role" suffix if not already present
        if "role" not in role.name.lower():
            aliases.append(f"{role.name.lower()} role")

        # Add plural form for common role names
        if role.name.lower().endswith("r"):
            aliases.append(f"{role.name.lower()}s")
        elif not role.name.lower().endswith("s"):
            aliases.append(f"{role.name.lower()}s")

        return aliases

    def _extract_bot_permissions(self, discord_guild: Dict[str, Any]) -> Any:
        """
        Extract bot permissions from Discord guild data.

        Args:
            discord_guild (Dict[str, Any]): The Discord guild data.

        Returns:
            Any: The bot permissions.
        """
        # This is a stub implementation
        from ..models import ServerPermissions

        return ServerPermissions()

    def _extract_channel_permissions(
        self, discord_channel: Dict[str, Any]
    ) -> Any:
        """
        Extract channel permissions from Discord channel data.

        Args:
            discord_channel (Dict[str, Any]): The Discord channel data.

        Returns:
            Any: The channel permissions.
        """
        # This is a stub implementation
        from ..models import ChannelPermissions

        return ChannelPermissions()
