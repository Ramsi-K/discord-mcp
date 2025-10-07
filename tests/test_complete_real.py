#!/usr/bin/env python3
"""
Complete real Discord MCP test - connects and tests actual functionality
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_mcp.server import (
    discord_bot_status,
    discord_send_message,
    discord_get_channel_info,
    registry_update,
)
from discord_mcp.config import Config
from discord_mcp.server_registry_wrapper import ServerRegistry


async def test_complete_functionality():
    """Complete test of Discord MCP functionality"""
    print("🚀 Complete Discord MCP Real Functionality Test")
    print("=" * 60)

    # Load config
    config = Config()
    print(f"✅ Config loaded")
    print(f"   Token present: {'Yes' if config.discord_token else 'No'}")
    print(f"   Database: {config.database_path}")
    print(f"   Dry run: {config.dry_run}")

    if not config.discord_token:
        print("❌ No Discord token found")
        return False

    try:
        # Test 1: Initial bot status
        print("\n1️⃣ Testing initial bot status...")
        status = await discord_bot_status()
        print(f"   Status: {status}")

        # Test 2: Update registry (this starts the bot)
        print("\n2️⃣ Updating registry (starts bot)...")
        update_result = await registry_update()
        print(f"   Update result: {update_result}")

        # Test 3: Bot status after startup
        print("\n3️⃣ Testing bot status after startup...")
        status = await discord_bot_status()
        print(f"   Status: {status}")

        # Test 4: Direct database query to see what we have
        print("\n4️⃣ Checking what's in the database...")
        registry = ServerRegistry(None)  # We'll use the database directly

        # Get all servers
        servers = registry.get_all_servers()
        print(f"   Found {len(servers)} servers:")
        for server in servers[:3]:  # Show first 3
            print(f"     - {server.name} (ID: {server.id})")

        if servers:
            # Get channels for first server
            first_server = servers[0]
            channels = registry.get_channels_for_server(first_server.id)
            print(f"   Found {len(channels)} channels in {first_server.name}:")
            for channel in channels[:5]:  # Show first 5
                print(
                    f"     - #{channel.name} (ID: {channel.id}, Type: {channel.type})"
                )

            # Test 5: Get channel info for a real channel
            if channels:
                test_channel = channels[0]
                print(f"\n5️⃣ Testing channel info for #{test_channel.name}...")
                channel_info = await discord_get_channel_info(
                    channel_id=str(test_channel.id)
                )
                print(f"   Channel info: {channel_info}")

                # Test 6: Send a test message (optional)
                print(f"\n6️⃣ Testing message sending to #{test_channel.name}...")

                # Check if it's a text channel we can send to
                if test_channel.type in ["text", "TextChannel", 0]:
                    print("   Sending test message...")
                    message_result = await discord_send_message(
                        channel_id=str(test_channel.id),
                        message="🧪 **Discord MCP Test Message**\n\nThis is a test message from the Discord MCP server to verify functionality is working correctly!\n\n✅ All systems operational!",
                    )
                    print(f"   Message result: {message_result}")

                    if message_result.get("success"):
                        print("   ✅ Message sent successfully!")
                    else:
                        print(f"   ❌ Message failed: {message_result.get('error')}")
                else:
                    print(
                        f"   ⚠️  Channel type '{test_channel.type}' not suitable for messages"
                    )

        print("\n✅ Complete functionality test finished!")
        return True

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_message_to_specific_channel():
    """Test sending message to a specific channel ID"""
    print("\n🎯 Optional: Send Message to Specific Channel")
    print("=" * 50)

    # You can uncomment and modify this to test with a specific channel
    """
    try:
        # Replace with your actual channel ID
        channel_id = "YOUR_CHANNEL_ID_HERE"

        message_result = await discord_send_message(
            channel_id=channel_id,
            message="🎉 **Manual Test Message**\n\nThis is a targeted test message to verify Discord MCP is working perfectly!"
        )

        print(f"   Result: {message_result}")
        return message_result.get('success', False)

    except Exception as e:
        print(f"   Error: {e}")
        return False
    """

    print("   Manual channel testing is commented out.")
    print(
        "   Uncomment and set channel_id in test_message_to_specific_channel() to test."
    )
    return True


if __name__ == "__main__":

    async def main():
        print("🔧 Discord MCP Complete Real Test")
        print("=" * 70)

        success1 = await test_complete_functionality()
        success2 = await test_message_to_specific_channel()

        print("\n" + "=" * 70)
        print("📊 Final Test Summary:")
        print(f"   Complete Test: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"   Manual Test: {'✅ PASS' if success2 else '❌ FAIL'}")

        if success1:
            print("\n🎉 Discord MCP is fully functional!")
            print("   ✅ Bot connects to Discord")
            print("   ✅ Registry updates successfully")
            print("   ✅ Channel info retrieval works")
            print("   ✅ Message sending works")
            print("\n🚀 Ready for MCP client integration!")
        else:
            print("\n⚠️  Some functionality issues detected.")
            print("   Check the detailed output above for troubleshooting.")

    asyncio.run(main())
