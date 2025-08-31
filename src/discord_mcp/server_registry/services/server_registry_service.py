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
            server_id (int): The server ID (not used, we use discord_guild.id).
            discord_guild (Any): The Discord guild object.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            # Create/update server
            server = self._create_server_from_guild(discord_guild)
            server = self.server_repo.upsert_server(server)

            # Update channels
            self._update_channels_for_server(server, discord_guild)

            # Update roles
            self._update_roles_for_server(server, discord_guild)

            logger.info(
                f"Successfully updated registry for server {discord_guild.name}"
            )
            return True
        except Exception as e:
            logger.error(
                f"Error updating server registry for {discord_guild.name}: {e}"
            )
            return False

    def update_all_server_registries(self, discord_guilds: List[Any]) -> bool:
        """
        Update the server registry for all servers.

        Args:
            discord_guilds (List[Any]): The Discord guild objects.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            success_count = 0
            for guild in discord_guilds:
                if self.update_server_registry(0, guild):  # server_id not used
                    success_count += 1

            logger.info(
                f"Updated registry for {success_count}/{len(discord_guilds)} servers"
            )
            return success_count > 0
        except Exception as e:
            logger.error(f"Error updating all server registries: {e}")
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

    def _create_server_from_guild(self, discord_guild: Any) -> Server:
        """
        Create a Server object from a Discord guild.

        Args:
            discord_guild (Any): The Discord guild object.

        Returns:
            Server: The created server object.
        """
        server = Server(
            discord_id=str(discord_guild.id),
            name=discord_guild.name,
            description=discord_guild.description,
            icon_url=(
                str(discord_guild.icon.url) if discord_guild.icon else None
            ),
            owner_id=(
                str(discord_guild.owner_id) if discord_guild.owner_id else None
            ),
        )

        # Generate aliases
        server.aliases = self.generate_server_aliases(server)

        return server

    def _update_channels_for_server(
        self, server: Server, discord_guild: Any
    ) -> None:
        """
        Update channels for a server.

        Args:
            server (Server): The server object.
            discord_guild (Any): The Discord guild object.
        """
        try:
            for discord_channel in discord_guild.channels:
                channel = self._create_channel_from_discord(
                    discord_channel, server.id
                )
                self.channel_repo.upsert_channel(channel)
        except Exception as e:
            logger.error(
                f"Error updating channels for server {server.name}: {e}"
            )

    def _update_roles_for_server(
        self, server: Server, discord_guild: Any
    ) -> None:
        """
        Update roles for a server.

        Args:
            server (Server): The server object.
            discord_guild (Any): The Discord guild object.
        """
        try:
            for discord_role in discord_guild.roles:
                role = self._create_role_from_discord(discord_role, server.id)
                self.role_repo.upsert_role(role)
        except Exception as e:
            logger.error(f"Error updating roles for server {server.name}: {e}")

    def _create_channel_from_discord(
        self, discord_channel: Any, server_id: int
    ) -> Channel:
        """
        Create a Channel object from a Discord channel.

        Args:
            discord_channel (Any): The Discord channel object.
            server_id (int): The server ID.

        Returns:
            Channel: The created channel object.
        """
        from ..models import ChannelType

        channel = Channel(
            discord_id=str(discord_channel.id),
            server_id=server_id,
            name=discord_channel.name,
            type=ChannelType.from_string(str(discord_channel.type)),
            topic=getattr(discord_channel, "topic", None),
            position=getattr(discord_channel, "position", 0),
            parent_id=(
                str(discord_channel.category.id)
                if getattr(discord_channel, "category", None)
                else None
            ),
        )

        # Generate aliases
        channel.aliases = self.generate_channel_aliases(channel)

        return channel

    def _create_role_from_discord(
        self, discord_role: Any, server_id: int
    ) -> Role:
        """
        Create a Role object from a Discord role.

        Args:
            discord_role (Any): The Discord role object.
            server_id (int): The server ID.

        Returns:
            Role: The created role object.
        """
        role = Role(
            discord_id=str(discord_role.id),
            server_id=server_id,
            name=discord_role.name,
            color=discord_role.color.value,
            position=discord_role.position,
            mentionable=discord_role.mentionable,
        )

        # Generate aliases
        role.aliases = self.generate_role_aliases(role)

        return role
