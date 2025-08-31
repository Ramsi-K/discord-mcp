#!/usr/bin/env python3
"""Test script to verify the restructured package works correctly."""

import os
import sys
import asyncio

# Set test environment variables
os.environ["DISCORD_TOKEN"] = "test_token_123"
os.environ["DRY_RUN"] = "true"


def test_imports():
    """Test that all the key imports work with the new structure."""
    try:
        # Test config import
        from src.discord_mcp.config import Config

        config = Config()
        print("✅ Config import and initialization works")

        # Test bot import
        from src.discord_mcp.discord_client.bot import DiscordMCPBot

        bot = DiscordMCPBot(config)
        print("✅ Discord bot import and initialization works")

        # Test server registry wrapper import
        from src.discord_mcp.server_registry_wrapper import ServerRegistry

        print("✅ Server registry wrapper import works")

        # Test server import
        from src.discord_mcp.server import main

        print("✅ Server main function import works")

        # Test that server registry can be initialized (without Discord bot)
        # registry = ServerRegistry(None)  # This should work for basic testing

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_config_functionality():
    """Test that config functionality works as expected."""
    try:
        from src.discord_mcp.config import Config

        config = Config()

        # Test required environment variables
        assert config.discord_token == "test_token_123"
        print("✅ Discord token reading works")

        # Test optional environment variables
        assert config.dry_run == True
        print("✅ DRY_RUN flag reading works")

        assert config.log_level == "INFO"  # Default value
        print("✅ Log level default works")

        assert config.guild_allowlist is None  # Not set
        print("✅ Guild allowlist default works")

        # Test guild allowlist functionality
        assert (
            config.is_guild_allowed("123456789") == True
        )  # Should allow all when None
        print("✅ Guild allowlist checking works")

        return True

    except Exception as e:
        print(f"❌ Config functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_bot_dry_run():
    """Test that the bot works in dry run mode."""
    try:
        from src.discord_mcp.config import Config
        from src.discord_mcp.discord_client.bot import DiscordMCPBot

        config = Config()
        bot = DiscordMCPBot(config)

        # Test dry run message sending
        result = await bot.send_direct_message(
            "123456789", "Test message", False
        )
        assert result["success"] == True
        assert result["dry_run"] == True
        print("✅ Bot dry run message sending works")

        # Test dry run channel info
        result = await bot.get_channel_info("123456789")
        assert result["success"] == True
        assert result["dry_run"] == True
        print("✅ Bot dry run channel info works")

        return True

    except Exception as e:
        print(f"❌ Bot dry run test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Testing restructured Discord MCP package...\n")

    tests_passed = 0
    total_tests = 3

    # Test imports
    if test_imports():
        tests_passed += 1

    # Test config functionality
    if test_config_functionality():
        tests_passed += 1

    # Test bot dry run functionality
    if asyncio.run(test_bot_dry_run()):
        tests_passed += 1

    print(f"\n{tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print(
            "✅ All tests passed! The restructure appears to be working correctly."
        )
        return True
    else:
        print(
            "❌ Some tests failed. The restructure may have broken functionality."
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
