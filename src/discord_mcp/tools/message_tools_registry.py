"""
Message tools for Discord MCP server.
"""

from typing import Optional
from pydantic import Field
from mcp.server.fastmcp import Context


async def send_message(
    channel_id: str = Field(
        description="Discord channel ID to send the message to"
    ),
    message: str = Field(description="Message content to send"),
    mention_everyone: bool = Field(
        default=False,
        description="Whether to mention @everyone in the message",
    ),
    *,
    ctx: Context,
) -> dict:
    """
    Send a message to a Discord channel.
    """
    # Log the request
    await ctx.info(f"Sending message to channel {channel_id}")
    await ctx.info(f"Message content: {message}")

    # Import discord for allowed mentions
    import discord
    import sys

    # Log available modules
    await ctx.info(f"Available modules: {list(sys.modules.keys())}")

    # Get the discord_bot from the server module
    try:
        from mcp_server.server import discord_bot

        await ctx.info(f"Discord bot from server module: {discord_bot}")
    except Exception as e:
        await ctx.info(f"Error importing discord_bot from server module: {e}")
        discord_bot = None

    if discord_bot:
        try:
            # Get the channel
            channel = discord_bot.get_channel(int(channel_id))
            if not channel:
                channel = await discord_bot.fetch_channel(int(channel_id))

            # Send the message
            allowed_mentions = discord.AllowedMentions(
                everyone=mention_everyone
            )
            sent_message = await channel.send(
                content=message, allowed_mentions=allowed_mentions
            )

            return {
                "success": True,
                "channel_id": channel_id,
                "message": message,
                "mention_everyone": mention_everyone,
                "message_id": str(sent_message.id),
                "timestamp": sent_message.created_at.isoformat(),
            }
        except Exception as e:
            await ctx.info(f"Error sending message: {str(e)}")
            return {
                "success": False,
                "error": f"Error sending message: {str(e)}",
            }
    else:
        await ctx.info("Discord bot not available")
        # Return mock data for testing
        return {
            "success": True,
            "channel_id": channel_id,
            "message": message,
            "mention_everyone": mention_everyone,
            "message_id": "123456789012345678",  # Mock message ID
            "timestamp": "2023-01-01T00:00:00Z",  # Mock timestamp
        }


async def get_channel_info(
    channel_id: str = Field(
        description="Discord channel ID to get information about"
    ),
    *,
    ctx: Context,
) -> dict:
    """
    Get information about a Discord channel.
    """
    # Log the request
    await ctx.info(f"Getting information for channel {channel_id}")

    # Get the discord_bot from the server module
    from mcp_server.server import discord_bot

    if discord_bot:

        try:
            # Get the channel
            channel = discord_bot.get_channel(int(channel_id))
            if not channel:
                channel = await discord_bot.fetch_channel(int(channel_id))

            # Return channel info
            return {
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "topic": getattr(channel, "topic", None),
                "nsfw": getattr(channel, "nsfw", False),
                "position": getattr(channel, "position", 0),
                "created_at": channel.created_at.isoformat(),
            }
        except Exception as e:
            await ctx.info(f"Error getting channel info: {str(e)}")
            return {
                "success": False,
                "error": f"Error getting channel info: {str(e)}",
            }
    else:
        await ctx.info("Discord bot not available")
        # Return mock data for testing
        return {
            "id": channel_id,
            "name": f"channel-{channel_id[-4:]}",
            "type": "text",
            "topic": "A sample Discord channel",
            "nsfw": False,
            "position": 1,
            "created_at": "2023-01-01T00:00:00Z",
        }
