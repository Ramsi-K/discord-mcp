"""
Bot management tools for Discord MCP server.
Provides tools for starting, stopping, and managing the Discord bot.
"""

import asyncio
import logging
import os
import dotenv
from typing import Dict, Any
from pydantic import Field
from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

# Global bot instance
_bot_instance = None
_bot_task = None

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


async def start_discord_bot(token: str = "") -> Dict[str, Any]:
    """Start the Discord bot with the provided token."""
    global _bot_instance, _bot_task

    # Get token from environment if not provided
    if not token:
        token = os.getenv("DISCORD_TOKEN", "")

    if not token:
        return {
            "error": "Discord token not provided and DISCORD_TOKEN environment variable not set"
        }

    # Check if bot is already running
    if _bot_instance and not _bot_instance.is_closed():
        # Make sure server module has the reference
        import mcp_server.server

        mcp_server.server.discord_bot = _bot_instance

        # Check if bot is connected by checking if user is available
        if _bot_instance.user:
            logger.info(f"Bot is already running as {_bot_instance.user}")
        else:
            # Wait a bit for the bot to connect
            logger.info(
                "Bot instance exists but not fully connected, waiting..."
            )
            max_wait = 5  # seconds
            for i in range(max_wait):
                if _bot_instance.user:
                    break
                await asyncio.sleep(1)
                logger.info(f"Waiting for existing bot to connect: {i+1}s")

        return {
            "success": True,
            "message": "Bot is already running",
            "bot_user": (
                str(_bot_instance.user)
                if _bot_instance.user
                else "Not logged in yet"
            ),
            "guild_count": (
                len(_bot_instance.guilds)
                if hasattr(_bot_instance, "guilds")
                else 0
            ),
        }

    try:
        # Import the bot class
        from bot.bot import DiscordMCPBot

        # Create new bot instance
        _bot_instance = DiscordMCPBot()

        # Start the bot in a background task
        _bot_task = asyncio.create_task(_bot_instance.start(token))

        # Wait for the bot to connect (user attribute becomes available)
        max_wait = 10  # seconds
        for i in range(max_wait):
            if _bot_instance.user:
                logger.info(f"Bot is connected after {i+1} seconds")
                break
            await asyncio.sleep(1)
            logger.info(f"Waiting for bot to connect: {i+1}s")

        # Update the server module's discord_bot reference
        import mcp_server.server

        mcp_server.server.discord_bot = _bot_instance

        return {
            "success": True,
            "message": "Discord bot started successfully",
            "bot_user": (
                str(_bot_instance.user)
                if _bot_instance.user
                else "Connecting..."
            ),
            "guild_count": (
                len(_bot_instance.guilds)
                if hasattr(_bot_instance, "guilds")
                else 0
            ),
        }

    except Exception as e:
        import traceback

        return {"error": f"Failed to start Discord bot: {str(e)}"}


async def get_bot_status() -> Dict[str, Any]:
    """Get the current status of the Discord bot."""
    global _bot_instance

    # Check global bot instance
    if not _bot_instance:
        return {
            "status": "not_started",
            "message": "Discord bot has not been started",
        }

    if _bot_instance.is_closed():
        return {
            "status": "closed",
            "message": "Discord bot is closed",
        }

    return {
        "status": "running",
        "bot_user": (
            str(_bot_instance.user) if _bot_instance.user else "Connecting..."
        ),
        "guild_count": len(_bot_instance.guilds),
        "guilds": [
            {"id": str(g.id), "name": g.name} for g in _bot_instance.guilds
        ],
    }


async def stop_discord_bot(*, ctx: Context) -> Dict[str, Any]:
    """Stop the Discord bot."""
    global _bot_instance, _bot_task

    await ctx.info("=== STOP_DISCORD_BOT ===")

    if not _bot_instance:
        return {"message": "Bot is not running"}

    try:
        await _bot_instance.close()
        if _bot_task and not _bot_task.done():
            _bot_task.cancel()

        _bot_instance = None
        _bot_task = None

        # Clear server module reference
        import mcp_server.server

        mcp_server.server.discord_bot = None

        return {"success": True, "message": "Discord bot stopped successfully"}

    except Exception as e:
        await ctx.info(f"Error stopping Discord bot: {e}")
        return {"error": f"Failed to stop Discord bot: {str(e)}"}
