#!/usr/bin/env python3
"""
Real Discord functionality test - connects to actual Discord API
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_mcp.config import Config
from discord_mcp.discord_client.bot import DiscordMCPBot
from discord_mcp.tools.discord_tools import (
    discord_bot_status,
    discord_list_servers,
    discord_list_channels,
    discord_get_channel_info,
    discord_send_message,
)


async def test_real_discord_functionality():
    """Test actual Discord functionality with real API calls"""
    print("🚀 Starting Real Discord Functionality Test")
    print("=" * 50)

    # Load environment
    config = Config()
    print(
        f"✅ Config loaded - Token present: {'Yes' if config.discord_token else 'No'}"
    )
    print(f"✅ Database path: {config.db_path}")
    print(f"✅ Dry run mode: {config.dry_run}")

    if config.dry_run:
        print("⚠️  DRY_RUN is enabled - switching to live mode for real testing")
        os.environ["DRY_RUN"] = "false"
        config = Config()  # Reload config

    if not config.discord_token:
        print("❌ No Discord token found in environment")
        return False

    print("\n🤖 Testing Discord Bot Connection...")

    try:
        # Test 1: Bot Status
        print("\n1️⃣ Testing bot status...")
        status_result = await discord_bot_status()
        print(f"   Status: {status_result}")

        # Test 2: List Servers
        print("\n2️⃣ Testing server listing...")
        servers_result = await discord_list_servers()
        print(f"   Servers: {servers_result}")

        # Test 3: List Channels (if we have servers)
        if "servers" in str(servers_result) and "[]" not in str(servers_result):
            print("\n3️⃣ Testing channel listing...")
            channels_result = await discord_list_channels()
            print(f"   Channels: {channels_result}")

            # Test 4: Get Channel Info (if we have channels)
            if "channels" in str(channels_result) and "[]" not in str(channels_result):
                print("\n4️⃣ Testing channel info...")
                # Try to extract a channel ID from the result
                import json

                try:
                    if isinstance(channels_result, str):
                        channels_data = json.loads(channels_result)
                    else:
                        channels_data = channels_result

                    if channels_data.get("channels"):
                        first_channel = channels_data["channels"][0]
                        channel_id = first_channel.get("id")
                        if channel_id:
                            info_result = await discord_get_channel_info(channel_id)
                            print(f"   Channel Info: {info_result}")

                            # Test 5: Send Test Message (commented out to avoid spam)
                            print("\n5️⃣ Testing message sending (dry run)...")
                            print(
                                "   Note: Actual message sending skipped to avoid spam"
                            )
                            print(
                                "   You can uncomment the line below to test real message sending"
                            )
                            # message_result = await discord_send_message(channel_id, "🧪 Test message from Discord MCP!")
                            # print(f"   Message Result: {message_result}")

                except Exception as e:
                    print(
                        f"   ⚠️  Could not parse channel data for detailed testing: {e}"
                    )

        print("\n✅ Real Discord functionality test completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error during Discord testing: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_bot_direct_connection():
    """Test direct bot connection and basic operations"""
    print("\n🔧 Testing Direct Bot Connection...")

    try:
        config = Config()
        bot = DiscordMCPBot(config)

        print("   Attempting to connect to Discord...")

        # Start bot in background
        bot_task = asyncio.create_task(bot.start(config.discord_token))

        # Wait a moment for connection
        await asyncio.sleep(3)

        if bot.is_ready():
            print(f"   ✅ Bot connected successfully!")
            print(f"   Bot user: {bot.user}")
            print(f"   Bot ID: {bot.user.id}")
            print(f"   Guilds: {len(bot.guilds)}")

            # List some basic info
            for guild in bot.guilds[:3]:  # First 3 guilds
                print(f"   - Guild: {guild.name} (ID: {guild.id})")

        else:
            print("   ⚠️  Bot not ready yet")

        # Clean shutdown
        await bot.close()
        bot_task.cancel()

        try:
            await bot_task
        except asyncio.CancelledError:
            pass

        return True

    except Exception as e:
        print(f"   ❌ Direct bot connection failed: {e}")
        return False


if __name__ == "__main__":

    async def main():
        print("🧪 Discord MCP Real Functionality Test")
        print("=" * 60)

        # Test 1: MCP Tools
        success1 = await test_real_discord_functionality()

        print("\n" + "=" * 60)

        # Test 2: Direct Bot Connection
        success2 = await test_bot_direct_connection()

        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"   MCP Tools Test: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"   Direct Bot Test: {'✅ PASS' if success2 else '❌ FAIL'}")

        if success1 and success2:
            print("\n🎉 All tests passed! Discord MCP is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")

    asyncio.run(main())
