"""
Test script for the Natural Language Command Processor.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def test_nlp():
    """Test the NLP processor."""
    # Import the bot class
    from bot.bot import DiscordMCPBot
    from mcp_server.server_registry_wrapper import ServerRegistry
    from mcp_server.nlp_processor import NLPProcessor

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

        # Create NLP processor
        processor = NLPProcessor(registry)

        # Test commands
        test_commands = [
            "Send a message in the general channel saying Hello from NLP test!",
            "List all channels in the server",
            "Show me the roles in the server",
            "What channels are available?",
        ]

        for command in test_commands:
            logger.info(f"\nProcessing command: {command}")
            result = await processor.process_command("test_user", command)
            logger.info(f"Intent: {result['intent']}")
            logger.info(f"Entities: {result['entities']}")
            logger.info(f"Resolved: {result['resolved']}")
            logger.info(f"Ambiguous: {result['ambiguous']}")

        # Wait a bit before shutting down
        await asyncio.sleep(2)

    finally:
        # Close the bot
        await bot.close()


if __name__ == "__main__":
    asyncio.run(test_nlp())
