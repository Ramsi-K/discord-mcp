#!/usr/bin/env python3
"""
Debug guild connectivity issues
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_mcp.config import Config
from discord_mcp.discord_client.bot import DiscordMCPBot


async def debug_guild_connection():
    """Debug why guilds aren't showing up"""
    print("🔍 Debugging Guild Connection Issues")
    print("=" * 50)

    config = Config()
    print(f"✅ Config loaded")
    print(f"   Token: {'Present' if config.discord_token else 'Missing'}")
    print(f"   Guild allowlist: {config.guild_allowlist}")

    # Create bot instance
    bot = DiscordMCPBot(config)

    # Add some debug logging
    @bot.event
    async def on_ready():
        print(f"\n🤖 Bot Ready Event Triggered!")
        print(f"   Bot user: {bot.user}")
        print(f"   Bot ID: {bot.user.id}")
        print(f"   Total guilds: {len(bot.guilds)}")

        if bot.guilds:
            print(f"\n📋 Guild Details:")
            for i, guild in enumerate(bot.guilds, 1):
                print(f"   {i}. {guild.name} (ID: {guild.id})")
                print(f"      Members: {guild.member_count}")
                print(f"      Channels: {len(guild.channels)}")

                # Check if guild is allowed
                if config.guild_allowlist:
                    allowed = config.is_guild_allowed(str(guild.id))
                    print(f"      Allowed: {allowed}")
                else:
                    print(f"      Allowed: Yes (no allowlist)")
        else:
            print(f"\n❌ No guilds found!")
            print(f"   This could mean:")
            print(f"   1. Bot token is invalid")
            print(f"   2. Bot hasn't been added to any servers")
            print(f"   3. Bot lacks necessary permissions")
            print(f"   4. Network/API issues")

        # Test guild access after ready
        await asyncio.sleep(1)
        print(f"\n🔄 Re-checking guilds after 1 second...")
        print(f"   Guilds now: {len(bot.guilds)}")

        # Stop the bot after debugging
        await bot.close()

    try:
        print(f"\n🚀 Starting bot for debugging...")
        await bot.start(config.discord_token)
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_guild_connection())
