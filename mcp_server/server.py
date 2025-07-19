"""
Main MCP server implementation for Discord.
"""

import logging
import os
import sys
from mcp.server.fastmcp import FastMCP

from mcp_server.tools.message_tools import send_message, get_channel_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="Discord MCP",
    description="MCP server for Discord integration",
    log_level="INFO",
)

# Try to access the Discord bot from the main module
try:
    # Get the module name from environment variable
    bot_module_name = os.environ.get("DISCORD_BOT_MODULE", "__main__")
    logger.info(f"Looking for Discord bot in module: {bot_module_name}")

    # Log all available modules
    logger.info(f"Available modules: {list(sys.modules.keys())}")

    bot_module = sys.modules.get(bot_module_name)
    logger.info(f"Bot module found: {bot_module}")

    if bot_module:
        logger.info(f"Bot module attributes: {dir(bot_module)}")

    if bot_module and hasattr(bot_module, "discord_bot"):
        discord_bot = bot_module.discord_bot
        logger.info(
            f"Successfully accessed Discord bot from main module: {discord_bot}"
        )
        logger.info(f"Discord bot type: {type(discord_bot)}")
        logger.info(f"Discord bot attributes: {dir(discord_bot)}")
    else:
        discord_bot = None
        logger.warning("Discord bot not found in main module")

        # Try to access it directly from __main__
        main_module = sys.modules.get("__main__")
        if main_module and hasattr(main_module, "discord_bot"):
            discord_bot = main_module.discord_bot
            logger.info(
                f"Found Discord bot directly in __main__: {discord_bot}"
            )
except Exception as e:
    discord_bot = None
    logger.error(f"Error accessing Discord bot: {e}")
    import traceback

    logger.error(f"Traceback: {traceback.format_exc()}")


# Register tools
@mcp.tool(
    name="discord_send_message",
    description="Send a message to a Discord channel",
)
async def discord_send_message(
    channel_id, message, mention_everyone=False, *, ctx
):
    return await send_message(channel_id, message, mention_everyone, ctx=ctx)


@mcp.tool(
    name="discord_get_channel_info",
    description="Get information about a Discord channel",
)
async def discord_get_channel_info(channel_id, *, ctx):
    return await get_channel_info(channel_id, ctx=ctx)


if __name__ == "__main__":
    # Run the MCP server
    logger.info("Starting Discord MCP server...")
    mcp.run(transport="stdio")
