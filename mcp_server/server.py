"""
Main MCP server implementation for Discord.
"""

import logging
import asyncio
import os
from functools import wraps
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variable to hold the bot instance
discord_bot = None
bot_task = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="Discord MCP",
    description="MCP server for Discord integration",
    log_level="INFO",
)


# Helper function to ensure Discord bot is ready
def require_discord_bot(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global discord_bot
        if not discord_bot or discord_bot.is_closed() or not discord_bot.user:
            # Try to start the bot if it's not running
            token = kwargs.get("token", "") or os.getenv("DISCORD_TOKEN", "")
            if not token:
                return {
                    "error": "Discord token not provided and DISCORD_TOKEN environment variable not set"
                }

            start_result = await ensure_bot_running(token)
            if not start_result.get("success"):
                return {
                    "error": f"Could not start Discord bot: {start_result.get('error', 'Unknown error')}"
                }

        return await func(*args, **kwargs)

    return wrapper


async def ensure_bot_running(token: str = "") -> dict:
    """Ensure the Discord bot is running and connected."""
    global discord_bot, bot_task

    if not token:
        token = os.getenv("DISCORD_TOKEN", "")

    if not token:
        return {"error": "No Discord token available"}

    # Check if bot is already running and connected
    if discord_bot and not discord_bot.is_closed() and discord_bot.user:
        logger.info(f"Bot is already running as {discord_bot.user}")
        return {
            "success": True,
            "message": "Bot is already running",
            "bot_user": str(discord_bot.user),
            "guild_count": (
                len(discord_bot.guilds) if discord_bot.guilds else 0
            ),
        }

    try:
        # Import the bot class
        from bot.bot import DiscordMCPBot

        # Create new bot instance
        discord_bot = DiscordMCPBot()

        # Start the bot in a background task
        bot_task = asyncio.create_task(discord_bot.start(token))

        # Wait for the bot to connect
        max_wait = 15  # seconds
        for i in range(max_wait):
            if discord_bot.user:
                logger.info(
                    f"Bot connected after {i+1} seconds as {discord_bot.user}"
                )
                break
            await asyncio.sleep(1)
            logger.info(f"Waiting for bot to connect: {i+1}s")

        if not discord_bot.user:
            return {"error": "Bot failed to connect within timeout period"}

        return {
            "success": True,
            "message": "Discord bot started successfully",
            "bot_user": str(discord_bot.user),
            "guild_count": (
                len(discord_bot.guilds) if discord_bot.guilds else 0
            ),
        }

    except Exception as e:
        logger.error(f"Failed to start Discord bot: {str(e)}")
        return {"error": f"Failed to start Discord bot: {str(e)}"}


@mcp.tool(
    name="discord_start_bot",
    description="Start the Discord bot",
)
async def discord_start_bot(token: str = ""):
    """Start the Discord bot."""
    return await ensure_bot_running(token)


@mcp.tool(
    name="discord_send_message",
    description="Send a message to a Discord channel",
)
@require_discord_bot
async def discord_send_message(
    channel_id: str,
    message: str,
    mention_everyone: bool = False,
    token: str = "",
):
    """Send a message to a Discord channel, starting bot if needed."""
    global discord_bot

    try:
        logger.info(f"Sending message to channel {channel_id}")
        return await discord_bot.send_direct_message(
            channel_id, message, mention_everyone
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return {"error": f"Error sending message: {str(e)}"}


@mcp.tool(
    name="discord_get_channel_info",
    description="Get information about a Discord channel",
)
@require_discord_bot
async def discord_get_channel_info(channel_id: str, token: str = ""):
    """Get information about a Discord channel, starting bot if needed."""
    global discord_bot

    try:
        logger.info(f"Getting info for channel {channel_id}")
        return await discord_bot.get_channel_info(channel_id)
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        return {"error": f"Error getting channel info: {str(e)}"}


@mcp.tool(
    name="discord_list_servers",
    description="List all servers the bot is in",
)
@require_discord_bot
async def discord_list_servers(token: str = ""):
    """List all servers the bot is in, starting bot if needed."""
    global discord_bot

    try:
        logger.info("Listing servers")
        servers = []
        for guild in discord_bot.guilds:
            servers.append(
                {
                    "id": str(guild.id),
                    "name": guild.name,
                    "member_count": guild.member_count,
                }
            )
        return {"servers": servers, "total_count": len(servers)}
    except Exception as e:
        logger.error(f"Error listing servers: {str(e)}")
        return {"error": f"Error listing servers: {str(e)}"}


@mcp.tool(
    name="discord_bot_status",
    description="Get the current status of the Discord bot",
)
async def discord_bot_status():
    """Get the current status of the Discord bot."""
    global discord_bot

    if not discord_bot:
        return {
            "status": "not_started",
            "message": "Discord bot has not been started",
        }

    if discord_bot.is_closed():
        return {
            "status": "closed",
            "message": "Discord bot is closed",
        }

    return {
        "status": "running",
        "bot_user": (
            str(discord_bot.user) if discord_bot.user else "Connecting..."
        ),
        "guild_count": len(discord_bot.guilds) if discord_bot.guilds else 0,
        "guilds": (
            [{"id": str(g.id), "name": g.name} for g in discord_bot.guilds]
            if discord_bot.guilds
            else []
        ),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
