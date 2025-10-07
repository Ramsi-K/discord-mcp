"""
Server Registry tools for Discord MCP server.
Provides tools for managing and querying Discord server information.
"""

import logging
from typing import Dict, Any
from pydantic import Field
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)


async def get_discord_bot(ctx: Context):
    """Helper function to get the Discord bot instance."""
    try:
        # Import from the server module
        import sys
        import importlib

        # Get the server module
        server_module = sys.modules.get("discord_mcp.server")
        if server_module and hasattr(server_module, "discord_bot"):
            discord_bot = server_module.discord_bot
            if discord_bot:
                await ctx.info(f"Discord bot available: {discord_bot.user}")
                return discord_bot

        await ctx.info("Discord bot not available")
        return None
    except Exception as e:
        await ctx.info(f"Error getting Discord bot: {e}")
        return None


async def get_config():
    """Helper function to get the configuration."""
    try:
        from ..config import Config

        return Config()
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return None


async def get_server_info(
    server_id: str = Field(description="Discord server (guild) ID"),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get detailed information about a Discord server."""
    await ctx.info(f"Getting server info for server_id: {server_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock server info")
        return {
            "id": server_id,
            "name": "Mock Server",
            "description": "A mock server for testing",
            "member_count": 150,
            "owner_id": "987654321098765432",
            "created_at": "2024-01-01T00:00:00.000000+00:00",
            "icon_url": None,
            "banner_url": None,
            "verification_level": "medium",
            "bot_permissions": {
                "administrator": False,
                "manage_channels": True,
                "manage_roles": False,
                "manage_messages": True,
                "send_messages": True,
                "embed_links": True,
                "mention_everyone": False,
            },
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(server_id):
            return {"error": f"Guild {server_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {"error": f"Server {server_id} not found or bot not in server"}

        # Get bot's permissions in the server
        bot_member = guild.get_member(discord_bot.user.id)
        bot_permissions = bot_member.guild_permissions if bot_member else None

        server_info = {
            "id": str(guild.id),
            "name": guild.name,
            "description": guild.description,
            "member_count": guild.member_count,
            "owner_id": str(guild.owner_id) if guild.owner_id else None,
            "created_at": (guild.created_at.isoformat() if guild.created_at else None),
            "icon_url": str(guild.icon.url) if guild.icon else None,
            "banner_url": str(guild.banner.url) if guild.banner else None,
            "verification_level": str(guild.verification_level),
            "bot_permissions": {
                "administrator": (
                    bot_permissions.administrator if bot_permissions else False
                ),
                "manage_channels": (
                    bot_permissions.manage_channels if bot_permissions else False
                ),
                "manage_roles": (
                    bot_permissions.manage_roles if bot_permissions else False
                ),
                "manage_messages": (
                    bot_permissions.manage_messages if bot_permissions else False
                ),
                "send_messages": (
                    bot_permissions.send_messages if bot_permissions else False
                ),
                "embed_links": (
                    bot_permissions.embed_links if bot_permissions else False
                ),
                "mention_everyone": (
                    bot_permissions.mention_everyone if bot_permissions else False
                ),
            },
        }

        return server_info

    except Exception as e:
        await ctx.info(f"Error getting server info: {e}")
        return {"error": f"Failed to get server info: {str(e)}"}


async def list_servers(*, ctx: Context) -> Dict[str, Any]:
    """List all servers the bot is in."""
    await ctx.info("Listing servers")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock server list")
        return {
            "servers": [
                {
                    "id": "123456789012345678",
                    "name": "Mock Server 1",
                    "member_count": 150,
                    "owner_id": "987654321098765432",
                },
                {
                    "id": "234567890123456789",
                    "name": "Mock Server 2",
                    "member_count": 75,
                    "owner_id": "876543210987654321",
                },
            ],
            "total_count": 2,
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        servers = []
        for guild in discord_bot.guilds:
            # Check guild allowlist if configured
            if not config.is_guild_allowed(str(guild.id)):
                continue

            servers.append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "owner_id": (str(guild.owner_id) if guild.owner_id else None),
                }
            )

        return {"servers": servers, "total_count": len(servers)}

    except Exception as e:
        await ctx.info(f"Error listing servers: {e}")
        return {"error": f"Failed to list servers: {str(e)}"}


async def get_server_channels(
    server_id: str = Field(description="Discord server (guild) ID"),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get all channels in a Discord server."""
    await ctx.info(f"Getting channels for server {server_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock channel data")
        return {
            "channels": [
                {
                    "id": "345678901234567890",
                    "name": "general",
                    "type": "text",
                    "position": 0,
                    "category": None,
                    "topic": "General discussion channel",
                },
                {
                    "id": "456789012345678901",
                    "name": "announcements",
                    "type": "text",
                    "position": 1,
                    "category": None,
                    "topic": "Server announcements",
                },
                {
                    "id": "567890123456789012",
                    "name": "Voice Channel 1",
                    "type": "voice",
                    "position": 2,
                    "category": None,
                    "user_limit": 10,
                },
            ],
            "server_name": "Mock Server",
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(server_id):
            return {"error": f"Guild {server_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {"error": f"Server {server_id} not found or bot not in server"}

        channels = []
        for channel in guild.channels:
            channel_info = {
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "category": (channel.category.name if channel.category else None),
            }

            # Add text channel specific info
            if hasattr(channel, "topic"):
                channel_info["topic"] = channel.topic

            # Add voice channel specific info
            if hasattr(channel, "user_limit"):
                channel_info["user_limit"] = channel.user_limit

            channels.append(channel_info)

        return {"channels": channels, "server_name": guild.name}

    except Exception as e:
        await ctx.info(f"Error getting server channels: {e}")
        return {"error": f"Failed to get server channels: {str(e)}"}


async def get_server_roles(
    server_id: str = Field(description="Discord server (guild) ID"),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get all roles in a Discord server."""
    await ctx.info(f"Getting roles for server {server_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock role data")
        return {
            "roles": [
                {
                    "id": "123456789012345678",
                    "name": "@everyone",
                    "color": 0,
                    "position": 0,
                    "mentionable": False,
                    "managed": False,
                    "member_count": 150,
                    "permissions": {
                        "administrator": False,
                        "manage_channels": False,
                        "manage_roles": False,
                        "manage_messages": False,
                    },
                },
                {
                    "id": "234567890123456789",
                    "name": "Moderator",
                    "color": 3447003,
                    "position": 5,
                    "mentionable": True,
                    "managed": False,
                    "member_count": 5,
                    "permissions": {
                        "administrator": False,
                        "manage_channels": True,
                        "manage_roles": True,
                        "manage_messages": True,
                    },
                },
            ],
            "server_name": "Mock Server",
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(server_id):
            return {"error": f"Guild {server_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {"error": f"Server {server_id} not found or bot not in server"}

        roles = []
        for role in guild.roles:
            roles.append(
                {
                    "id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "position": role.position,
                    "mentionable": role.mentionable,
                    "managed": role.managed,
                    "member_count": len(role.members),
                    "permissions": {
                        "administrator": role.permissions.administrator,
                        "manage_channels": role.permissions.manage_channels,
                        "manage_roles": role.permissions.manage_roles,
                        "manage_messages": role.permissions.manage_messages,
                    },
                }
            )

        return {"roles": roles, "server_name": guild.name}

    except Exception as e:
        await ctx.info(f"Error getting server roles: {e}")
        return {"error": f"Failed to get server roles: {str(e)}"}


async def find_server_by_name(
    name: str = Field(
        description="Server name to search for (supports partial matching)"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Find a server by name (supports partial matching)."""
    await ctx.info(f"Finding server by name: {name}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock server search results")
        name_lower = name.lower()
        mock_servers = [
            {
                "id": "123456789012345678",
                "name": "Mock Server 1",
                "member_count": 150,
            },
            {
                "id": "234567890123456789",
                "name": "Mock Server 2",
                "member_count": 75,
            },
            {
                "id": "345678901234567890",
                "name": "Test Server",
                "member_count": 25,
            },
        ]

        matches = []
        for server in mock_servers:
            if name_lower in server["name"].lower():
                matches.append(
                    {
                        **server,
                        "exact_match": server["name"].lower() == name_lower,
                    }
                )

        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))
        return {"matches": matches, "query": name, "dry_run": True}

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        matches = []
        name_lower = name.lower()

        for guild in discord_bot.guilds:
            # Check guild allowlist if configured
            if not config.is_guild_allowed(str(guild.id)):
                continue

            if name_lower in guild.name.lower():
                matches.append(
                    {
                        "id": str(guild.id),
                        "name": guild.name,
                        "member_count": guild.member_count,
                        "exact_match": guild.name.lower() == name_lower,
                    }
                )

        # Sort by exact match first, then by name
        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))

        return {"matches": matches, "query": name}

    except Exception as e:
        await ctx.info(f"Error finding server by name: {e}")
        return {"error": f"Failed to find server: {str(e)}"}


async def find_channel_by_name(
    server_id: str = Field(description="Discord server (guild) ID"),
    name: str = Field(
        description="Channel name to search for (supports partial matching)"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Find a channel by name in a specific server."""
    await ctx.info(f"Finding channel '{name}' in server {server_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock channel search results")
        name_lower = name.lower()
        mock_channels = [
            {
                "id": "345678901234567890",
                "name": "general",
                "type": "text",
                "category": None,
            },
            {
                "id": "456789012345678901",
                "name": "announcements",
                "type": "text",
                "category": None,
            },
            {
                "id": "567890123456789012",
                "name": "general-chat",
                "type": "text",
                "category": "Community",
            },
        ]

        matches = []
        for channel in mock_channels:
            if name_lower in channel["name"].lower():
                matches.append(
                    {
                        **channel,
                        "exact_match": channel["name"].lower() == name_lower,
                    }
                )

        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))
        return {
            "matches": matches,
            "query": name,
            "server_name": "Mock Server",
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(server_id):
            return {"error": f"Guild {server_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {"error": f"Server {server_id} not found or bot not in server"}

        matches = []
        name_lower = name.lower()

        for channel in guild.channels:
            if name_lower in channel.name.lower():
                matches.append(
                    {
                        "id": str(channel.id),
                        "name": channel.name,
                        "type": str(channel.type),
                        "category": (
                            channel.category.name if channel.category else None
                        ),
                        "exact_match": channel.name.lower() == name_lower,
                    }
                )

        # Sort by exact match first, then by name
        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))

        return {"matches": matches, "query": name, "server_name": guild.name}

    except Exception as e:
        await ctx.info(f"Error finding channel by name: {e}")
        return {"error": f"Failed to find channel: {str(e)}"}


async def find_role_by_name(
    server_id: str = Field(description="Discord server (guild) ID"),
    name: str = Field(
        description="Role name to search for (supports partial matching)"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Find a role by name in a specific server."""
    await ctx.info(f"Finding role '{name}' in server {server_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock role search results")
        name_lower = name.lower()
        mock_roles = [
            {
                "id": "123456789012345678",
                "name": "@everyone",
                "color": 0,
                "member_count": 150,
            },
            {
                "id": "234567890123456789",
                "name": "Moderator",
                "color": 3447003,
                "member_count": 5,
            },
            {
                "id": "345678901234567890",
                "name": "Member",
                "color": 7506394,
                "member_count": 100,
            },
        ]

        matches = []
        for role in mock_roles:
            if name_lower in role["name"].lower():
                matches.append(
                    {
                        **role,
                        "exact_match": role["name"].lower() == name_lower,
                    }
                )

        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))
        return {
            "matches": matches,
            "query": name,
            "server_name": "Mock Server",
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(server_id):
            return {"error": f"Guild {server_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {"error": f"Server {server_id} not found or bot not in server"}

        matches = []
        name_lower = name.lower()

        for role in guild.roles:
            if name_lower in role.name.lower():
                matches.append(
                    {
                        "id": str(role.id),
                        "name": role.name,
                        "color": role.color.value,
                        "member_count": len(role.members),
                        "exact_match": role.name.lower() == name_lower,
                    }
                )

        # Sort by exact match first, then by name
        matches.sort(key=lambda x: (not x["exact_match"], x["name"]))

        return {"matches": matches, "query": name, "server_name": guild.name}

    except Exception as e:
        await ctx.info(f"Error finding role by name: {e}")
        return {"error": f"Failed to find role: {str(e)}"}
