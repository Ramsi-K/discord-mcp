"""
Simple Discord bot implementation that can be connected to the MCP server.
"""

import os
import asyncio
import logging
import discord
from discord.ext import commands

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DiscordMCPBot(commands.Bot):
    """Discord bot that can be connected to an MCP server."""

    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        # Initialize the bot
        super().__init__(
            command_prefix="!", intents=intents, help_command=None
        )

    async def send_direct_message(
        self, channel_id, message, mention_everyone=False
    ):
        """Send a message directly to a channel."""
        logger.info(
            f"Sending direct message to channel {channel_id}: {message}"
        )
        try:
            # Get the channel
            channel = self.get_channel(int(channel_id))
            if not channel:
                channel = await self.fetch_channel(int(channel_id))

            # Send the message
            allowed_mentions = discord.AllowedMentions(
                everyone=mention_everyone
            )
            sent_message = await channel.send(
                content=message, allowed_mentions=allowed_mentions
            )

            logger.info(f"Message sent successfully: {sent_message.id}")
            return {
                "success": True,
                "channel_id": str(channel.id),
                "message": message,
                "message_id": str(sent_message.id),
                "timestamp": sent_message.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"success": False, "error": str(e)}

    async def get_channel_info(self, channel_id):
        """Get information about a channel directly."""
        logger.info(f"Getting channel info for channel {channel_id}")
        try:
            # Get the channel
            channel = self.get_channel(int(channel_id))
            if not channel:
                channel = await self.fetch_channel(int(channel_id))

            # Return channel info
            return {
                "success": True,
                "id": str(channel.id),
                "name": channel.name,
                "type": str(channel.type),
                "topic": getattr(channel, "topic", None),
                "nsfw": getattr(channel, "nsfw", False),
                "position": getattr(channel, "position", 0),
                "created_at": channel.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return {"success": False, "error": str(e)}

    async def setup_hook(self):
        """Set up the bot when it's starting."""
        logger.info("Setting up Discord bot...")

        # Register commands
        await self.add_cog(BasicCommands(self))

        logger.info("Discord bot setup complete!")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="MCP commands"
            )
        )


class BasicCommands(commands.Cog):
    """Basic commands for the Discord bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Simple ping command to check if the bot is alive."""
        await ctx.send(
            f"Pong! Bot latency: {round(self.bot.latency * 1000)}ms"
        )

    @commands.command(name="send")
    async def send_message(self, ctx, channel_id: str, *, message: str):
        """Send a message to a specific channel."""
        try:
            # Get the channel
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                channel = await self.bot.fetch_channel(int(channel_id))

            # Send the message
            await channel.send(message)
            await ctx.send(f"Message sent to channel {channel.name}!")
        except Exception as e:
            await ctx.send(f"Error sending message: {str(e)}")


async def run_bot():
    """Run the Discord bot."""
    # Load environment variables from .env file
    from dotenv import load_dotenv

    load_dotenv()

    # Get the token from environment variable
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.error(
            "No Discord token found. Please set the DISCORD_TOKEN environment variable."
        )
        return

    # Create and run the bot
    bot = DiscordMCPBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    # Run the bot
    asyncio.run(run_bot())
