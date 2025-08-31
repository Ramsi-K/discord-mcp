#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from discord_mcp.server_registry_wrapper import ServerRegistry
from discord_mcp.discord_client.bot import DiscordMCPBot
from discord_mcp.config import Config


async def test():
    bot = DiscordMCPBot(Config())
    registry = ServerRegistry(bot)
    result = await registry.initialize()
    print(f"Registry init: {result}")


asyncio.run(test())
