"""
Server Registry tools for Discord MCP server.
Provides tools for managing and querying Discord server information.
"""

import logging
from typing import Dict, List, Optional, Any
from pydantic import Field
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)


async def get_discord_bot(ctx: Context):
    """Helper function to get the Discord bot instance."""
    try:
        from mcp_server.server import discord_bot
        await ctx.info(f"Discord bot: {discord_bot}")
        return discord_bot
    except Exception as e:
        await ctx.info(f"Error getting Discord bot: {e}")
        return None


async def get_server_info(
    server_id: str,
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get detailed information about a Discord server."""
    await ctx.info(f"Getting server info for server_id: {server_id}")
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {
                "error": f"Server {server_id} not found or bot not in server"
            }

        # Get bot's permissions in the server
        bot_member = guild.get_member(discord_bot.user.id)
        bot_permissions = bot_member.guild_permissions if bot_member else None

        server_info = {
            "id": str(guild.id),
            "name": guild.name,
            "description": guild.description,
            "member_count": guild.member_count,
            "owner_id": str(guild.owner_id) if guild.owner_id else None,
            "created_at": (
                guild.created_at.isoformat() if guild.created_at else None
            ),
            "icon_url": str(guild.icon.url) if guild.icon else None,
            "banner_url": str(guild.banner.url) if guild.banner else None,
            "verification_level": str(guild.verification_level),
            "bot_permissions": {
                "administrator": (
                    bot_permissions.administrator if bot_permissions else False
                ),
                "manage_channels": (
                    bot_permissions.manage_channels
                    if bot_permissions
                    else False
                ),
                "manage_roles": (
                    bot_permissions.manage_roles if bot_permissions else False
                ),
                "manage_messages": (
                    bot_permissions.manage_messages
                    if bot_permissions
                    else False
                ),
                "send_messages": (
                    bot_permissions.send_messages if bot_permissions else False
                ),
                "embed_links": (
                    bot_permissions.embed_links if bot_permissions else False
                ),
                "mention_everyone": (
                    bot_permissions.mention_everyone
                    if bot_permissions
                    else False
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
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        servers = []
        for guild in discord_bot.guilds:
            servers.append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "owner_id": (
                        str(guild.owner_id) if guild.owner_id else None
                    ),
                }
            )

        return {"servers": servers, "total_count": len(servers)}

    except Exception as e:
        await ctx.info(f"Error listing servers: {e}")
        return {"error": f"Failed to list servers: {str(e)}"}


async def get_server_channels(
    server_id: str,
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get all channels in a Discord server."""
    await ctx.info(f"Getting channels for server {server_id}")
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {
                "error": f"Server {server_id} not found or bot not in server"
            }

        channels = []
        for channel in guild.channels:
            channel_info = {
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "position": channel.position,
                "category": (
                    channel.category.name if channel.category else None
                ),
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
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {
                "error": f"Server {server_id} not found or bot not in server"
            }

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
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        matches = []
        name_lower = name.lower()

        for guild in discord_bot.guilds:
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
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {
                "error": f"Server {server_id} not found or bot not in server"
            }

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
    
    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        guild = discord_bot.get_guild(int(server_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(server_id))

        if not guild:
            return {
                "error": f"Server {server_id} not found or bot not in server"
            }

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