"""
Test script for the Server Registry.
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the restructured package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def test_registry():
    """Test the server registry."""
    # Import the bot class
    from src.discord_mcp.discord_client.bot import DiscordMCPBot
    from src.discord_mcp.server_registry_wrapper import ServerRegistry

    # Get token
    token = os.getenv("DISCORD_TOKEN", "")
    if not token:
        logger.error("No Discord token available")
        return

    # Create bot instance
    bot = DiscordMCPBot()

    # Start the bot
    try:
        # Start the bot in a background task
        bot_task = asyncio.create_task(bot.start(token))

        # Wait for the bot to connect
        max_wait = 15  # seconds
        for i in range(max_wait):
            if bot.user:
                logger.info(f"Bot connected after {i+1} seconds as {bot.user}")
                break
            await asyncio.sleep(1)
            logger.info(f"Waiting for bot to connect: {i+1}s")

        if not bot.user:
            logger.error("Bot failed to connect within timeout period")
            return

        # Initialize server registry
        registry = ServerRegistry(bot)
        init_success = await registry.initialize()
        if not init_success:
            logger.error("Failed to initialize server registry")
            return

        # Update registry
        update_result = await registry.update_registry()
        logger.info(f"Registry update result: {update_result}")

        # Test finding a server
        if bot.guilds:
            guild = bot.guilds[0]
            logger.info(f"Testing find_server with {guild.name}")
            server = await registry.find_server(guild.name)
            if server:
                logger.info(f"Found server: {server.name} (ID: {server.discord_id})")
            else:
                logger.info("Server not found")

            # Test finding a channel
            if guild.channels:
                channel = guild.channels[0]
                logger.info(f"Testing find_channel with {channel.name}")
                found_channel = await registry.find_channel(channel.name, guild.name)
                if found_channel:
                    logger.info(
                        f"Found channel: {found_channel.name} (ID: {found_channel.discord_id})"
                    )
                else:
                    logger.info("Channel not found")

        # Wait a bit before shutting down
        await asyncio.sleep(2)

    finally:
        # Close the bot
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test_registry())
