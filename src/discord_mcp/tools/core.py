"""
Core Discord MCP tools for server and channel operations.
Implements the essential Discord functionality for MCP integration.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from functools import wraps
from pydantic import Field
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)


def require_bot(func):
    """Decorator to ensure Discord bot is running before executing tool."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get ctx from kwargs
        ctx = kwargs.get('ctx')
        if not ctx:
            return {"error": "Context not available"}

        # Check if bot is available
        discord_bot = await get_discord_bot(ctx)
        if not discord_bot:
            # Try to start bot
            import os
            from ..server import ensure_bot_running

            token = os.getenv("DISCORD_TOKEN", "")
            if not token:
                return {
                    "error": "Discord bot not started and DISCORD_TOKEN not set. Please start the bot first."
                }

            # Start the bot
            start_result = await ensure_bot_running(token)
            if not start_result.get("success"):
                return {
                    "error": f"Could not start Discord bot: {start_result.get('error', 'Unknown error')}"
                }

        return await func(*args, **kwargs)

    return wrapper


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


# Server and Channel Listing Tools (Task 2.1)


@require_bot
async def discord_list_servers(*, ctx: Context) -> Dict[str, Any]:
    """List all servers (guilds) the bot is a member of.

    Returns information about all Discord servers the bot has access to,
    including server ID, name, member count, and owner information.
    """
    await ctx.info("Listing Discord servers")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock server data")
        return {
            "servers": [
                {
                    "id": "123456789012345678",
                    "name": "Mock Server 1",
                    "member_count": 150,
                    "owner_id": "987654321098765432",
                    "description": "A mock server for testing",
                    "icon_url": None,
                    "verification_level": "medium",
                },
                {
                    "id": "234567890123456789",
                    "name": "Mock Server 2",
                    "member_count": 75,
                    "owner_id": "876543210987654321",
                    "description": "Another mock server",
                    "icon_url": None,
                    "verification_level": "low",
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

            server_info = {
                "id": str(guild.id),
                "name": guild.name,
                "member_count": guild.member_count,
                "owner_id": str(guild.owner_id) if guild.owner_id else None,
                "description": guild.description,
                "icon_url": str(guild.icon.url) if guild.icon else None,
                "verification_level": str(guild.verification_level),
            }
            servers.append(server_info)

        return {"servers": servers, "total_count": len(servers)}

    except Exception as e:
        await ctx.info(f"Error listing servers: {e}")
        return {"error": f"Failed to list servers: {str(e)}"}


@require_bot
async def discord_list_channels(
    guild_id: str = Field(description="Discord server (guild) ID"),
    channel_type: Optional[str] = Field(
        default=None,
        description="Optional channel type filter (text, voice, category, etc.)",
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """List channels in a Discord server with optional type filtering.

    Args:
        guild_id: The Discord server ID to list channels from
        channel_type: Optional filter by channel type (text, voice, category, etc.)

    Returns:
        Dictionary containing list of channels and server information
    """
    await ctx.info(
        f"Listing channels for server {guild_id}, type filter: {channel_type}"
    )

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock channel data")
        mock_channels = [
            {
                "id": "345678901234567890",
                "name": "general",
                "type": "text",
                "position": 0,
                "category": None,
                "topic": "General discussion channel",
                "nsfw": False,
            },
            {
                "id": "456789012345678901",
                "name": "announcements",
                "type": "text",
                "position": 1,
                "category": None,
                "topic": "Server announcements",
                "nsfw": False,
            },
            {
                "id": "567890123456789012",
                "name": "Voice Channel 1",
                "type": "voice",
                "position": 2,
                "category": None,
                "user_limit": 10,
            },
        ]

        # Apply type filter if specified
        if channel_type:
            mock_channels = [
                ch for ch in mock_channels if ch["type"] == channel_type
            ]

        return {
            "channels": mock_channels,
            "server_name": "Mock Server",
            "server_id": guild_id,
            "filtered_by_type": channel_type,
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        # Check guild allowlist
        if not config.is_guild_allowed(guild_id):
            return {"error": f"Guild {guild_id} is not in the allowlist"}

        guild = discord_bot.get_guild(int(guild_id))
        if not guild:
            guild = await discord_bot.fetch_guild(int(guild_id))

        if not guild:
            return {
                "error": f"Server {guild_id} not found or bot not in server"
            }

        channels = []
        for channel in guild.channels:
            # Apply type filter if specified
            if channel_type and str(channel.type) != channel_type:
                continue

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
            if hasattr(channel, "nsfw"):
                channel_info["nsfw"] = channel.nsfw

            # Add voice channel specific info
            if hasattr(channel, "user_limit"):
                channel_info["user_limit"] = channel.user_limit
            if hasattr(channel, "bitrate"):
                channel_info["bitrate"] = channel.bitrate

            channels.append(channel_info)

        return {
            "channels": channels,
            "server_name": guild.name,
            "server_id": str(guild.id),
            "filtered_by_type": channel_type,
            "total_count": len(channels),
        }

    except Exception as e:
        await ctx.info(f"Error listing channels: {e}")
        return {"error": f"Failed to list channels: {str(e)}"}


# Channel Information and Status Tools (Task 2.2)


@require_bot
async def discord_get_channel_info(
    channel_id: str = Field(description="Discord channel ID"), *, ctx: Context
) -> Dict[str, Any]:
    """Get detailed information about a Discord channel.

    Args:
        channel_id: The Discord channel ID to get information about

    Returns:
        Dictionary containing detailed channel information
    """
    await ctx.info(f"Getting channel info for {channel_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock channel info")
        return {
            "id": channel_id,
            "name": "mock-channel",
            "type": "text",
            "topic": "Mock channel for dry run testing",
            "nsfw": False,
            "position": 5,
            "category": "Mock Category",
            "created_at": "2024-01-01T00:00:00.000000+00:00",
            "server_id": "123456789012345678",
            "server_name": "Mock Server",
            "permissions": {
                "send_messages": True,
                "read_messages": True,
                "manage_messages": False,
                "embed_links": True,
            },
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        channel = discord_bot.get_channel(int(channel_id))
        if not channel:
            channel = await discord_bot.fetch_channel(int(channel_id))

        if not channel:
            return {"error": f"Channel {channel_id} not found"}

        # Check guild allowlist if channel is in a guild
        if channel.guild and not config.is_guild_allowed(
            str(channel.guild.id)
        ):
            return {
                "error": f"Guild {channel.guild.id} is not in the allowlist"
            }

        # Get bot's permissions in this channel
        bot_permissions = None
        if channel.guild:
            bot_member = channel.guild.get_member(discord_bot.user.id)
            if bot_member:
                bot_permissions = channel.permissions_for(bot_member)

        channel_info = {
            "id": str(channel.id),
            "name": channel.name,
            "type": str(channel.type),
            "position": getattr(channel, "position", None),
            "category": (
                channel.category.name
                if getattr(channel, "category", None)
                else None
            ),
            "created_at": channel.created_at.isoformat(),
            "server_id": str(channel.guild.id) if channel.guild else None,
            "server_name": channel.guild.name if channel.guild else None,
        }

        # Add text channel specific info
        if hasattr(channel, "topic"):
            channel_info["topic"] = channel.topic
        if hasattr(channel, "nsfw"):
            channel_info["nsfw"] = channel.nsfw
        if hasattr(channel, "slowmode_delay"):
            channel_info["slowmode_delay"] = channel.slowmode_delay

        # Add voice channel specific info
        if hasattr(channel, "user_limit"):
            channel_info["user_limit"] = channel.user_limit
        if hasattr(channel, "bitrate"):
            channel_info["bitrate"] = channel.bitrate

        # Add bot permissions if available
        if bot_permissions:
            channel_info["permissions"] = {
                "send_messages": bot_permissions.send_messages,
                "read_messages": bot_permissions.read_messages,
                "manage_messages": bot_permissions.manage_messages,
                "embed_links": bot_permissions.embed_links,
                "attach_files": bot_permissions.attach_files,
                "read_message_history": bot_permissions.read_message_history,
                "mention_everyone": bot_permissions.mention_everyone,
                "add_reactions": bot_permissions.add_reactions,
            }

        return channel_info

    except Exception as e:
        await ctx.info(f"Error getting channel info: {e}")
        return {"error": f"Failed to get channel info: {str(e)}"}


@require_bot
async def discord_bot_status(*, ctx: Context) -> Dict[str, Any]:
    """Get the current status and health information of the Discord bot.

    Returns:
        Dictionary containing bot status, connection info, and guild information
    """
    await ctx.info("Getting Discord bot status")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock bot status")
        return {
            "status": "connected",
            "bot_user": "MockBot#1234",
            "bot_id": "123456789012345678",
            "guild_count": 2,
            "latency": 45.2,
            "uptime": "2h 15m 30s",
            "guilds": [
                {"id": "123456789012345678", "name": "Mock Server 1"},
                {"id": "234567890123456789", "name": "Mock Server 2"},
            ],
            "dry_run": True,
            "config": {
                "guild_allowlist": config.guild_allowlist,
                "log_level": config.log_level,
            },
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {
            "status": "not_connected",
            "message": "Discord bot is not available or not started",
            "config": {
                "guild_allowlist": config.guild_allowlist,
                "log_level": config.log_level,
                "dry_run": config.dry_run,
            },
        }

    try:
        if discord_bot.is_closed():
            return {
                "status": "closed",
                "message": "Discord bot connection is closed",
                "config": {
                    "guild_allowlist": config.guild_allowlist,
                    "log_level": config.log_level,
                    "dry_run": config.dry_run,
                },
            }

        # Filter guilds by allowlist if configured
        allowed_guilds = []
        if discord_bot.guilds:
            for guild in discord_bot.guilds:
                if config.is_guild_allowed(str(guild.id)):
                    allowed_guilds.append(
                        {
                            "id": str(guild.id),
                            "name": guild.name,
                            "member_count": guild.member_count,
                        }
                    )

        return {
            "status": "connected",
            "bot_user": (
                str(discord_bot.user) if discord_bot.user else "Unknown"
            ),
            "bot_id": str(discord_bot.user.id) if discord_bot.user else None,
            "guild_count": len(allowed_guilds),
            "total_guild_count": (
                len(discord_bot.guilds) if discord_bot.guilds else 0
            ),
            "latency": round(discord_bot.latency * 1000, 1),  # Convert to ms
            "guilds": allowed_guilds,
            "config": {
                "guild_allowlist": config.guild_allowlist,
                "log_level": config.log_level,
                "dry_run": config.dry_run,
            },
        }

    except Exception as e:
        await ctx.info(f"Error getting bot status: {e}")
        return {"error": f"Failed to get bot status: {str(e)}"}


@require_bot
async def discord_ping(
    server_id: Optional[str] = Field(
        default=None, description="Optional server ID to check connection to specific server"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Ping Discord to check connection health and optionally verify access to a specific server.

    This is a lightweight health check that verifies:
    - Bot is connected to Discord
    - Bot is responsive (latency check)
    - Optionally: Bot has access to a specific server

    Args:
        server_id: Optional Discord server/guild ID to verify access to

    Returns:
        Dictionary with connection status, latency, and server access info
    """
    await ctx.info(f"Pinging Discord{f' and checking server {server_id}' if server_id else ''}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock ping data")
        return {
            "status": "connected",
            "latency_ms": 42.5,
            "bot_user": "MockBot#1234",
            "server_access": True if server_id else None,
            "server_name": "Mock Server" if server_id else None,
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {
            "status": "disconnected",
            "error": "Discord bot is not connected",
        }

    try:
        if discord_bot.is_closed():
            return {
                "status": "closed",
                "error": "Discord bot connection is closed",
            }

        # Basic ping response
        response = {
            "status": "connected",
            "latency_ms": round(discord_bot.latency * 1000, 2),
            "bot_user": str(discord_bot.user) if discord_bot.user else "Unknown",
            "bot_id": str(discord_bot.user.id) if discord_bot.user else None,
        }

        # If server_id provided, check access
        if server_id:
            guild = discord_bot.get_guild(int(server_id))

            if not guild:
                # Try fetching it
                try:
                    guild = await discord_bot.fetch_guild(int(server_id))
                except:
                    guild = None

            if guild:
                # Check if allowed by allowlist
                if not config.is_guild_allowed(server_id):
                    response["server_access"] = False
                    response["server_error"] = f"Server {server_id} not in allowlist"
                else:
                    response["server_access"] = True
                    response["server_id"] = str(guild.id)
                    response["server_name"] = guild.name
                    response["member_count"] = guild.member_count
            else:
                response["server_access"] = False
                response["server_error"] = f"Bot does not have access to server {server_id}"

        return response

    except Exception as e:
        await ctx.info(f"Error pinging Discord: {e}")
        return {
            "status": "error",
            "error": f"Failed to ping Discord: {str(e)}"
        }


# Message Management Tools (Task 2.3)


@require_bot
async def discord_get_recent_messages(
    channel_id: str = Field(description="Discord channel ID"),
    limit: int = Field(
        default=50, description="Number of messages to retrieve (max 100)"
    ),
    before: Optional[str] = Field(
        default=None, description="Message ID to get messages before"
    ),
    after: Optional[str] = Field(
        default=None, description="Message ID to get messages after"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get recent messages from a Discord channel with pagination support.

    Args:
        channel_id: The Discord channel ID to get messages from
        limit: Number of messages to retrieve (1-100, default 50)
        before: Message ID to get messages before (for pagination)
        after: Message ID to get messages after (for pagination)

    Returns:
        Dictionary containing list of messages and pagination info
    """
    await ctx.info(
        f"Getting recent messages from channel {channel_id}, limit: {limit}"
    )

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Validate limit
    if limit < 1 or limit > 100:
        return {"error": "Limit must be between 1 and 100"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock message data")
        mock_messages = []
        for i in range(min(limit, 5)):  # Return up to 5 mock messages
            mock_messages.append(
                {
                    "id": f"67890123456789012{i}",
                    "content": f"Mock message {i + 1} content",
                    "author": {
                        "id": f"11111111111111111{i}",
                        "username": f"MockUser{i + 1}",
                        "display_name": f"Mock User {i + 1}",
                        "bot": False,
                    },
                    "timestamp": f"2024-01-0{i + 1}T12:00:00.000000+00:00",
                    "edited_timestamp": None,
                    "attachments": [],
                    "embeds": [],
                    "reactions": [],
                    "reply_to": None,
                    "type": "default",
                }
            )

        return {
            "messages": mock_messages,
            "channel_id": channel_id,
            "count": len(mock_messages),
            "has_more": False,
            "pagination": {"before": before, "after": after, "limit": limit},
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        channel = discord_bot.get_channel(int(channel_id))
        if not channel:
            channel = await discord_bot.fetch_channel(int(channel_id))

        if not channel:
            return {"error": f"Channel {channel_id} not found"}

        # Check guild allowlist if channel is in a guild
        if channel.guild and not config.is_guild_allowed(
            str(channel.guild.id)
        ):
            return {
                "error": f"Guild {channel.guild.id} is not in the allowlist"
            }

        # Check bot permissions
        if channel.guild:
            bot_member = channel.guild.get_member(discord_bot.user.id)
            if bot_member:
                permissions = channel.permissions_for(bot_member)
                if not permissions.read_message_history:
                    return {
                        "error": "Bot does not have permission to read message history in this channel"
                    }

        # Set up pagination parameters
        kwargs = {"limit": limit}
        if before:
            try:
                before_msg = await channel.fetch_message(int(before))
                kwargs["before"] = before_msg
            except:
                return {"error": f"Invalid before message ID: {before}"}

        if after:
            try:
                after_msg = await channel.fetch_message(int(after))
                kwargs["after"] = after_msg
            except:
                return {"error": f"Invalid after message ID: {after}"}

        # Fetch messages
        messages = []
        async for message in channel.history(**kwargs):
            message_data = {
                "id": str(message.id),
                "content": message.content,
                "author": {
                    "id": str(message.author.id),
                    "username": message.author.name,
                    "display_name": message.author.display_name,
                    "bot": message.author.bot,
                },
                "timestamp": message.created_at.isoformat(),
                "edited_timestamp": (
                    message.edited_at.isoformat()
                    if message.edited_at
                    else None
                ),
                "attachments": [
                    {
                        "id": str(att.id),
                        "filename": att.filename,
                        "size": att.size,
                        "url": att.url,
                        "content_type": att.content_type,
                    }
                    for att in message.attachments
                ],
                "embeds": [
                    {
                        "title": embed.title,
                        "description": embed.description,
                        "url": embed.url,
                        "color": embed.color.value if embed.color else None,
                    }
                    for embed in message.embeds
                ],
                "reactions": [
                    {"emoji": str(reaction.emoji), "count": reaction.count}
                    for reaction in message.reactions
                ],
                "reply_to": (
                    str(message.reference.message_id)
                    if message.reference
                    else None
                ),
                "type": str(message.type),
            }
            messages.append(message_data)

        return {
            "messages": messages,
            "channel_id": channel_id,
            "channel_name": channel.name,
            "count": len(messages),
            "has_more": len(messages)
            == limit,  # Assume more if we got exactly the limit
            "pagination": {"before": before, "after": after, "limit": limit},
        }

    except Exception as e:
        await ctx.info(f"Error getting recent messages: {e}")
        return {"error": f"Failed to get recent messages: {str(e)}"}


@require_bot
async def discord_get_message(
    channel_id: str = Field(description="Discord channel ID"),
    message_id: str = Field(description="Discord message ID"),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Get a specific message by ID from a Discord channel.

    Args:
        channel_id: The Discord channel ID containing the message
        message_id: The Discord message ID to retrieve

    Returns:
        Dictionary containing the message information
    """
    await ctx.info(f"Getting message {message_id} from channel {channel_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Returning mock message data")
        return {
            "id": message_id,
            "content": "Mock message content for testing",
            "author": {
                "id": "123456789012345678",
                "username": "MockUser",
                "display_name": "Mock User",
                "bot": False,
            },
            "timestamp": "2024-01-01T12:00:00.000000+00:00",
            "edited_timestamp": None,
            "attachments": [],
            "embeds": [],
            "reactions": [],
            "reply_to": None,
            "type": "default",
            "channel_id": channel_id,
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        channel = discord_bot.get_channel(int(channel_id))
        if not channel:
            channel = await discord_bot.fetch_channel(int(channel_id))

        if not channel:
            return {"error": f"Channel {channel_id} not found"}

        # Check guild allowlist if channel is in a guild
        if channel.guild and not config.is_guild_allowed(
            str(channel.guild.id)
        ):
            return {
                "error": f"Guild {channel.guild.id} is not in the allowlist"
            }

        # Check bot permissions
        if channel.guild:
            bot_member = channel.guild.get_member(discord_bot.user.id)
            if bot_member:
                permissions = channel.permissions_for(bot_member)
                if not permissions.read_message_history:
                    return {
                        "error": "Bot does not have permission to read message history in this channel"
                    }

        # Fetch the specific message
        message = await channel.fetch_message(int(message_id))

        message_data = {
            "id": str(message.id),
            "content": message.content,
            "author": {
                "id": str(message.author.id),
                "username": message.author.name,
                "display_name": message.author.display_name,
                "bot": message.author.bot,
                "avatar_url": (
                    str(message.author.avatar.url)
                    if message.author.avatar
                    else None
                ),
            },
            "timestamp": message.created_at.isoformat(),
            "edited_timestamp": (
                message.edited_at.isoformat() if message.edited_at else None
            ),
            "attachments": [
                {
                    "id": str(att.id),
                    "filename": att.filename,
                    "size": att.size,
                    "url": att.url,
                    "content_type": att.content_type,
                }
                for att in message.attachments
            ],
            "embeds": [
                {
                    "title": embed.title,
                    "description": embed.description,
                    "url": embed.url,
                    "color": embed.color.value if embed.color else None,
                    "footer": embed.footer.text if embed.footer else None,
                    "timestamp": (
                        embed.timestamp.isoformat()
                        if embed.timestamp
                        else None
                    ),
                }
                for embed in message.embeds
            ],
            "reactions": [
                {
                    "emoji": str(reaction.emoji),
                    "count": reaction.count,
                    "me": reaction.me,
                }
                for reaction in message.reactions
            ],
            "reply_to": (
                str(message.reference.message_id)
                if message.reference
                else None
            ),
            "type": str(message.type),
            "channel_id": channel_id,
            "channel_name": channel.name,
        }

        return message_data

    except Exception as e:
        await ctx.info(f"Error getting message: {e}")
        return {"error": f"Failed to get message: {str(e)}"}


@require_bot
async def discord_send_message(
    channel_id: str = Field(description="Discord channel ID"),
    content: str = Field(description="Message content to send"),
    reply_to_id: Optional[str] = Field(
        default=None, description="Message ID to reply to"
    ),
    mention_everyone: bool = Field(
        default=False, description="Allow @everyone and @here mentions (requires permission)"
    ),
    *,
    ctx: Context,
) -> Dict[str, Any]:
    """Send a message to a Discord channel with optional reply support and mention controls.

    Args:
        channel_id: The Discord channel ID to send the message to
        content: The message content to send
        reply_to_id: Optional message ID to reply to
        mention_everyone: Allow @everyone and @here mentions (default: False, requires bot permission)

    Returns:
        Dictionary containing the sent message information
    """
    await ctx.info(f"Sending message to channel {channel_id}")

    config = await get_config()
    if not config:
        return {"error": "Configuration not available"}

    # Validate message content
    if not content or len(content.strip()) == 0:
        return {"error": "Message content cannot be empty"}

    if len(content) > 2000:
        return {"error": "Message content cannot exceed 2000 characters"}

    # Handle DRY_RUN mode
    if config.dry_run:
        await ctx.info("DRY_RUN mode: Message not actually sent")
        return {
            "success": True,
            "message_id": "dry_run_message_id_123456789",
            "channel_id": channel_id,
            "content": content,
            "timestamp": "2024-01-01T12:00:00.000000+00:00",
            "reply_to_id": reply_to_id,
            "dry_run": True,
        }

    discord_bot = await get_discord_bot(ctx)
    if not discord_bot:
        return {"error": "Discord bot not available"}

    try:
        channel = discord_bot.get_channel(int(channel_id))
        if not channel:
            channel = await discord_bot.fetch_channel(int(channel_id))

        if not channel:
            return {"error": f"Channel {channel_id} not found"}

        # Check guild allowlist if channel is in a guild
        if channel.guild and not config.is_guild_allowed(
            str(channel.guild.id)
        ):
            return {
                "error": f"Guild {channel.guild.id} is not in the allowlist"
            }

        # Check bot permissions
        if channel.guild:
            bot_member = channel.guild.get_member(discord_bot.user.id)
            if bot_member:
                permissions = channel.permissions_for(bot_member)
                if not permissions.send_messages:
                    return {
                        "error": "Bot does not have permission to send messages in this channel"
                    }

        # Set up message reference for reply
        message_reference = None
        if reply_to_id:
            try:
                reply_message = await channel.fetch_message(int(reply_to_id))
                message_reference = reply_message
            except:
                return {"error": f"Invalid reply message ID: {reply_to_id}"}

        # Set up allowed mentions
        import discord
        allowed_mentions = discord.AllowedMentions(everyone=mention_everyone)

        # Send the message
        sent_message = await channel.send(
            content=content,
            reference=message_reference,
            allowed_mentions=allowed_mentions
        )

        return {
            "success": True,
            "message_id": str(sent_message.id),
            "channel_id": str(sent_message.channel.id),
            "channel_name": sent_message.channel.name,
            "content": sent_message.content,
            "timestamp": sent_message.created_at.isoformat(),
            "reply_to_id": reply_to_id,
            "author": {
                "id": str(sent_message.author.id),
                "username": sent_message.author.name,
                "display_name": sent_message.author.display_name,
            },
        }

    except Exception as e:
        await ctx.info(f"Error sending message: {e}")
        return {"error": f"Failed to send message: {str(e)}"}
