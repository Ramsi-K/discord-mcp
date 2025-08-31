"""
Test the core Discord MCP tools implementation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


# Mock the Context class since we can't import it directly in tests
class MockContext:
    def __init__(self):
        self.info = AsyncMock()


# Import the tools to test
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from discord_mcp.tools.core import (
    discord_list_servers,
    discord_list_channels,
    discord_get_channel_info,
    discord_bot_status,
    discord_get_recent_messages,
    discord_get_message,
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


class TestCoreTools:
    """Test cases for core Discord MCP tools."""

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
    async def test_discord_list_channels_dry_run(self, mock_ctx, mock_config):
        """Test discord_list_channels in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_list_channels(
                guild_id="123456789012345678", channel_type=None, ctx=mock_ctx
            )

            assert result is not None
            assert "channels" in result
            assert "server_name" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert len(result["channels"]) == 3

    @pytest.mark.asyncio
    async def test_discord_list_channels_with_type_filter_dry_run(
        self, mock_ctx, mock_config
    ):
        """Test discord_list_channels with type filter in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_list_channels(
                guild_id="123456789012345678",
                channel_type="text",
                ctx=mock_ctx,
            )

            assert result is not None
            assert "channels" in result
            assert "filtered_by_type" in result
            assert result["filtered_by_type"] == "text"
            assert result["dry_run"] is True
            # Should only return text channels
            for channel in result["channels"]:
                assert channel["type"] == "text"

    @pytest.mark.asyncio
    async def test_discord_get_channel_info_dry_run(
        self, mock_ctx, mock_config
    ):
        """Test discord_get_channel_info in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_get_channel_info(
                channel_id="345678901234567890", ctx=mock_ctx
            )

            assert result is not None
            assert "id" in result
            assert "name" in result
            assert "type" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["id"] == "345678901234567890"

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
    async def test_discord_get_recent_messages_dry_run(
        self, mock_ctx, mock_config
    ):
        """Test discord_get_recent_messages in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_get_recent_messages(
                channel_id="345678901234567890", limit=10, ctx=mock_ctx
            )

            assert result is not None
            assert "messages" in result
            assert "channel_id" in result
            assert "count" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["channel_id"] == "345678901234567890"
            assert len(result["messages"]) <= 10

    @pytest.mark.asyncio
    async def test_discord_get_message_dry_run(self, mock_ctx, mock_config):
        """Test discord_get_message in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_get_message(
                channel_id="345678901234567890",
                message_id="678901234567890123",
                ctx=mock_ctx,
            )

            assert result is not None
            assert "id" in result
            assert "content" in result
            assert "author" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["id"] == "678901234567890123"

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
    async def test_discord_send_message_with_reply_dry_run(
        self, mock_ctx, mock_config
    ):
        """Test discord_send_message with reply in DRY_RUN mode."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            result = await discord_send_message(
                channel_id="345678901234567890",
                content="Reply message",
                reply_to_id="678901234567890123",
                ctx=mock_ctx,
            )

            assert result is not None
            assert "success" in result
            assert "reply_to_id" in result
            assert "dry_run" in result
            assert result["dry_run"] is True
            assert result["success"] is True
            assert result["reply_to_id"] == "678901234567890123"

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

            # Test content too long
            long_content = "x" * 2001
            result = await discord_send_message(
                channel_id="345678901234567890",
                content=long_content,
                ctx=mock_ctx,
            )
            assert "error" in result
            assert "2000" in result["error"]

    @pytest.mark.asyncio
    async def test_discord_get_recent_messages_validation(
        self, mock_ctx, mock_config
    ):
        """Test discord_get_recent_messages input validation."""
        with patch(
            "discord_mcp.tools.core.get_config", return_value=mock_config
        ):
            # Test invalid limit
            result = await discord_get_recent_messages(
                channel_id="345678901234567890", limit=0, ctx=mock_ctx
            )
            assert "error" in result
            assert "between 1 and 100" in result["error"]

            result = await discord_get_recent_messages(
                channel_id="345678901234567890", limit=101, ctx=mock_ctx
            )
            assert "error" in result
            assert "between 1 and 100" in result["error"]

    @pytest.mark.asyncio
    async def test_config_not_available(self, mock_ctx):
        """Test behavior when config is not available."""
        with patch("discord_mcp.tools.core.get_config", return_value=None):
            result = await discord_list_servers(ctx=mock_ctx)
            assert "error" in result
            assert "Configuration not available" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__])
