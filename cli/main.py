import asyncio
import sys
import os
from dotenv import load_dotenv
from contextlib import AsyncExitStack

# Add parent directory to path for imports
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from .mcp_client import MCPClient
from cli.claude import Claude
from cli.cli_chat import CliChat
from cli.cli import CliApp
from src.discord_mcp.discord_client.bot import DiscordMCPBot

load_dotenv()

# Anthropic Config
claude_model = os.getenv("CLAUDE_MODEL", "")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

# Discord Config
discord_token = os.getenv("DISCORD_TOKEN", "")

assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert (
    anthropic_api_key
), "Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
assert discord_token, "Error: DISCORD_TOKEN cannot be empty. Update .env"

# Global Discord bot instance
discord_bot = None


async def main():
    claude_service = Claude(model=claude_model)

    server_scripts = sys.argv[1:]
    clients = {}

    # Set environment variable to pass the Discord bot to the MCP server
    os.environ["DISCORD_BOT_AVAILABLE"] = "1"

    command, args = (
        ("uv", ["run", "src/discord_mcp/server.py"])
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["src/discord_mcp/server.py"])
    )

    # Initialize Discord bot
    global discord_bot
    discord_bot = DiscordMCPBot()
    # Start the bot in the background
    print("Starting Discord bot...")
    try:
        # Make sure the bot is available globally
        sys.modules["__main__"].discord_bot = discord_bot

        bot_task = asyncio.create_task(discord_bot.start(discord_token))
        print("Discord bot task created successfully")
    except Exception as e:
        print(f"Error starting Discord bot: {e}")
        print(f"Token length: {len(discord_token)}")
        print(f"First few characters of token: {discord_token[:5]}...")
        bot_task = None

    async with AsyncExitStack() as stack:
        discord_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["discord_client"] = discord_client

        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client

        # Store Discord bot reference for tool access
        clients["discord_bot"] = discord_bot

        # Pass the Discord bot to the MCP server via environment variable
        os.environ["DISCORD_BOT_MODULE"] = "__main__"

        chat = CliChat(
            discord_client=discord_client,
            clients=clients,
            claude_service=claude_service,
        )

        cli = CliApp(chat)
        await cli.initialize()

        try:
            await cli.run()
        finally:
            # Ensure bot is closed properly when CLI exits
            if not bot_task.done():
                await discord_bot.close()  # Await the close coroutine
                await bot_task


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
