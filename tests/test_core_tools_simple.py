"""
Simple test for core Discord MCP tools to verify basic functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# Mock the Context class
class MockContext:
    def __init__(self):
        self.info = AsyncMock()


# Import the tools to test
from discord_mcp.tools.core import (
    discord_list_servers,
    discord_bot_status,
    discord_send_message,
)


@pytest.fixture
def mock_ctx():
    """Create a mock MCP context."""
    return MockContext()


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock()
    config.dry_run = True
    config.guild_allowlist = None
    config.log_level = "INFO"
    config.is_guild_allowed = MagicMock(return_value=True)
    return config


class TestCoreToolsBasic:
    """Basic test cases for core Discord MCP tools."""

    @pytest.mark.asyncio
    async def test_discord_list_servers_dry_run(self, mock_ctx, mock_config):
        """Test discord_list_servers in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_list_servers(ctx=mock_ctx)

            assert result is not None
            assert "servers" in result
            assert "total_count" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert len(result["servers"]) == 2
            assert result["total_count"] == 2

    @pytest.mark.asyncio
    async def test_discord_bot_status_dry_run(self, mock_ctx, mock_config):
        """Test discord_bot_status in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_bot_status(ctx=mock_ctx)

            assert result is not None
            assert "status" in result
            assert "bot_user" in result
            assert "guild_count" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["status"] == "connected"

    @pytest.mark.asyncio
    async def test_discord_send_message_dry_run(self, mock_ctx, mock_config):
        """Test discord_send_message in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_send_message(
                channel_id="345678901234567890",
                content="Test message",
                ctx=mock_ctx,
            )

            assert result is not None
            assert "success" in result
            assert "message_id" in result
            assert "content" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["success"] is True
            assert result["content"] == "Test message"

    @pytest.mark.asyncio
    async def test_discord_send_message_validation(
        self, mock_ctx, mock_config
    ):
        """Test discord_send_message input validation."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            # Test empty content
            result = await discord_send_message(
                channel_id="345678901234567890", content="", ctx=mock_ctx
            )
            assert "error" in result
            assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_config_not_available(self, mock_ctx):
        """Test behavior when config is not available."""
        with patch("discord_mcp.tools.core.get_config", return_value=None):
            result = await discord_list_servers(ctx=mock_ctx)
            assert "error" in result
            assert "Configuration not available" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__])
