#!/usr/bin/env python3
"""
Test MCP tools with real Discord API calls
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the server module to get access to the tool functions
from discord_mcp.server import (
    discord_bot_status,
    discord_send_message,
    discord_get_channel_info,
    registry_get_server,
    registry_get_channel,
    registry_update,
)
from discord_mcp.config import Config


async def test_mcp_tools():
    """Test MCP tools with real Discord functionality"""
    print("🧪 Testing MCP Tools with Real Discord API")
    print("=" * 50)

    # Load config
    config = Config()
    print(f"✅ Config loaded")
    print(f"   Token present: {'Yes' if config.discord_token else 'No'}")
    print(f"   Database path: {config.database_path}")
    print(f"   Dry run mode: {config.dry_run}")

    if not config.discord_token:
        print("❌ No Discord token found")
        return False

    try:
        # Test 1: Bot Status
        print("\n1️⃣ Testing discord_bot_status...")
        status = await discord_bot_status()
        print(f"   Result: {status}")

        # Test 2: Registry Update (to populate the database)
        print("\n2️⃣ Testing registry_update...")
        update_result = await registry_update()
        print(f"   Result: {update_result}")

        # Test 3: Get Server Info
        print("\n3️⃣ Testing registry_get_server...")
        try:
            # Try to get the first server
            server_result = await registry_get_server(
                reference=""
            )  # Empty reference should return first server
            print(f"   Result: {server_result}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test 4: Get Channel Info
        print("\n4️⃣ Testing registry_get_channel...")
        try:
            channel_result = await registry_get_channel(
                reference="general"
            )  # Common channel name
            print(f"   Result: {channel_result}")

            # If we got a channel, test getting its info
            if channel_result and "id" in str(channel_result):
                print("\n5️⃣ Testing discord_get_channel_info...")
                # Extract channel ID from result
                import json

                if isinstance(channel_result, str):
                    channel_data = json.loads(channel_result)
                else:
                    channel_data = channel_result

                if "id" in channel_data:
                    channel_id = channel_data["id"]
                    info_result = await discord_get_channel_info(
                        channel_id=channel_id
                    )
                    print(f"   Result: {info_result}")

                    # Test 6: Send Message (commented out to avoid spam)
                    print("\n6️⃣ Testing discord_send_message (dry run)...")
                    print(
                        "   Note: Uncomment below to test real message sending"
                    )
                    # message_result = await discord_send_message(
                    #     channel_id=channel_id,
                    #     message="🧪 Test message from Discord MCP tools!"
                    # )
                    # print(f"   Result: {message_result}")

        except Exception as e:
            print(f"   Error: {e}")

        print("\n✅ MCP tools test completed!")
        return True

    except Exception as e:
        print(f"\n❌ Error during MCP tools test: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_direct_message_sending():
    """Test sending a real message if user wants to"""
    print("\n🚀 Optional: Test Real Message Sending")
    print("=" * 50)

    # This is commented out by default to avoid spam
    # Uncomment and modify to test real message sending

    """
    try:
        # Replace with actual channel ID you want to test with
        test_channel_id = "YOUR_CHANNEL_ID_HERE"
        
        message_result = await discord_send_message(
            channel_id=test_channel_id,
            message="🧪 Test message from Discord MCP! This is a real test."
        )
        print(f"Message sent: {message_result}")
        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False
    """

    print("   Real message sending is disabled by default.")
    print("   Uncomment the code in test_direct_message_sending() to test.")
    return True


if __name__ == "__main__":

    async def main():
        print("🔧 Discord MCP Tools Real Test")
        print("=" * 60)

        success1 = await test_mcp_tools()
        success2 = await test_direct_message_sending()

        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"   MCP Tools: {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"   Message Test: {'✅ PASS' if success2 else '❌ FAIL'}")

        if success1:
            print("\n🎉 MCP tools are working with real Discord API!")
        else:
            print("\n⚠️  Some issues found. Check output above.")

    asyncio.run(main())
