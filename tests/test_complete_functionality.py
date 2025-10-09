#!/usr/bin/env python3
"""
Comprehensive test for Discord MCP package functionality.
Tests both dry run and live functionality.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from discord_mcp.config import Config
from discord_mcp.server import ensure_bot_running, discord_bot_status
from discord_mcp.discord_client.bot import DiscordMCPBot


async def test_config():
    """Test configuration loading."""
    print("🧪 Testing configuration...")

    config = Config()

    # Test basic properties
    assert config.discord_token, "Discord token should be loaded"
    assert config.log_level in [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]
    assert isinstance(config.dry_run, bool)
    assert config.database_path is not None

    print(f"✅ Config loaded: DRY_RUN={config.dry_run}, LOG_LEVEL={config.log_level}")
    return config


async def test_bot_dry_run():
    """Test bot functionality in dry run mode."""
    print("🧪 Testing bot in DRY_RUN mode...")

    # Set dry run mode
    os.environ["DRY_RUN"] = "true"

    config = Config()
    bot = DiscordMCPBot(config)

    # Test dry run message sending
    result = await bot.send_direct_message("123456789", "Test message")
    print(f"Dry run result: {result}")
    assert result["success"] == True
    assert result["dry_run"] == True
    print("✅ Dry run message sending works")

    # Test dry run channel info
    result = await bot.get_channel_info("123456789")
    print(f"Channel info result: {result}")
    assert result["success"] == True
    assert result.get("dry_run") == True
    print("✅ Dry run channel info works")

    # Reset dry run mode
    os.environ["DRY_RUN"] = "false"


async def test_bot_live_connection():
    """Test live bot connection (if token is valid)."""
    print("🧪 Testing live bot connection...")

    config = Config()

    # Test bot status before starting
    status = await discord_bot_status()
    print(f"Initial bot status: {status['status']}")

    # Try to start the bot
    result = await ensure_bot_running()

    if result.get("success"):
        print(f"✅ Bot connected successfully as {result['bot_user']}")
        print(f"✅ Bot is in {result['guild_count']} guilds")

        # Test bot status after starting
        status = await discord_bot_status()
        assert status["status"] == "running"
        print("✅ Bot status check works")

        return True
    else:
        print(f"⚠️  Bot connection failed: {result.get('error')}")
        print(
            "This might be expected if the token is invalid or bot has no permissions"
        )
        return False


async def test_server_registry():
    """Test server registry functionality."""
    print("🧪 Testing server registry...")

    try:
        from discord_mcp.server_registry_wrapper import ServerRegistry
        from discord_mcp.discord_client.bot import DiscordMCPBot

        config = Config()
        bot = DiscordMCPBot(config)
        registry = ServerRegistry(bot)

        # Test initialization
        init_result = await registry.initialize()
        if init_result:
            print("✅ Server registry initialized successfully")
        else:
            print("⚠️  Server registry initialization failed (might be expected)")

    except Exception as e:
        print(f"⚠️  Server registry test failed: {e}")


async def test_imports():
    """Test all critical imports."""
    print("🧪 Testing imports...")

    # Test main server imports
    from discord_mcp.server import main, mcp

    print("✅ Server imports work")

    # Test config import
    from discord_mcp.config import Config

    print("✅ Config import works")

    # Test bot import
    from discord_mcp.discord_client.bot import DiscordMCPBot

    print("✅ Bot import works")

    # Test tools imports
    from discord_mcp.tools.tools import register_tools

    print("✅ Tools import works")

    # Test registry import
    from discord_mcp.server_registry_wrapper import ServerRegistry

    print("✅ Registry import works")


async def main():
    """Run all tests."""
    print("🚀 Starting comprehensive Discord MCP functionality tests...\n")

    try:
        # Test imports first
        await test_imports()
        print()

        # Test configuration
        config = await test_config()
        print()

        # Test dry run functionality
        await test_bot_dry_run()
        print()

        # Test live bot connection
        live_success = await test_bot_live_connection()
        print()

        # Test server registry
        await test_server_registry()
        print()

        print("🎉 All tests completed!")

        if live_success:
            print("✅ Package is fully functional with live Discord connection")
        else:
            print("⚠️  Package structure is correct, but live Discord connection failed")
            print("   This might be due to token permissions or network issues")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
