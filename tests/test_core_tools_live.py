"""Live integration tests for core Discord tools.

These tests exercise the tools against a real Discord guild/channel.
Enable by setting:
  DISCORD_LIVE_TESTS=1
  DISCORD_TEST_GUILD_ID=<guild_id>
  DISCORD_TEST_CHANNEL_ID=<text_channel_id>
Optional:
  DISCORD_TEST_ROLE_ID=<role_id to mention>
"""

import asyncio
import os
import time
from contextlib import suppress
from unittest.mock import AsyncMock

import pytest

from discord_mcp.tools.core import (
    discord_get_channel_info,
    discord_get_message,
    discord_get_recent_messages,
    discord_list_channels,
    discord_ping,
    discord_send_message,
)


LIVE_TESTS_ENABLED = os.getenv("DISCORD_LIVE_TESTS", "0").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
TEST_GUILD_ID = os.getenv("DISCORD_TEST_GUILD_ID")
TEST_CHANNEL_ID = os.getenv("DISCORD_TEST_CHANNEL_ID")
TEST_ROLE_ID = os.getenv("DISCORD_TEST_ROLE_ID")

pytestmark = pytest.mark.skipif(
    not LIVE_TESTS_ENABLED or not TEST_GUILD_ID or not TEST_CHANNEL_ID,
    reason=(
        "Live Discord test environment not configured. "
        "Set DISCORD_LIVE_TESTS=1 and provide DISCORD_TEST_GUILD_ID / DISCORD_TEST_CHANNEL_ID."
    ),
)


class LiveContext:
    """Minimal MCP context for logging calls within tests."""

    def __init__(self):
        self.info = AsyncMock()


@pytest.fixture(scope="session")
async def live_bot():
    """Ensure the Discord bot is running for the duration of the test session."""
    try:
        import discord_mcp.server as server
    except TypeError as exc:
        pytest.skip(f"Unable to import discord_mcp.server: {exc}")
    except Exception as exc:
        pytest.skip(f"discord_mcp.server import failed: {exc}")

    start_result = await server.ensure_bot_running()
    if not start_result.get("success"):
        pytest.skip(
            f"Unable to start Discord bot for live tests: {start_result.get('error')}"
        )

    yield server.discord_bot

    if server.discord_bot and not server.discord_bot.is_closed():
        await server.discord_bot.close()

    if server.bot_task:
        server.bot_task.cancel()
        with suppress(asyncio.CancelledError):
            await server.bot_task


@pytest.fixture
def live_ctx():
    return LiveContext()


@pytest.mark.asyncio
async def test_discord_ping_live(live_ctx, live_bot):
    result = await discord_ping(server_id=TEST_GUILD_ID, ctx=live_ctx)
    assert result["status"] == "connected"
    assert result.get("server_access") is True
    assert result.get("server_id") == TEST_GUILD_ID


@pytest.mark.asyncio
async def test_discord_list_channels_live(live_ctx, live_bot):
    result = await discord_list_channels(guild_id=TEST_GUILD_ID, ctx=live_ctx)
    assert "channels" in result
    channel_ids = {channel["id"] for channel in result["channels"]}
    assert TEST_CHANNEL_ID in channel_ids


@pytest.mark.asyncio
async def test_send_and_fetch_message_live(live_ctx, live_bot):
    unique_suffix = str(int(time.time()))
    base_content = f"Live integration test {unique_suffix}"

    mention_user_ids = str(live_bot.user.id)
    mention_role_ids = str(TEST_ROLE_ID) if TEST_ROLE_ID else None

    send_result = await discord_send_message(
        channel_id=TEST_CHANNEL_ID,
        content=base_content,
        mention_user_ids=mention_user_ids,
        mention_role_ids=mention_role_ids,
        ctx=live_ctx,
    )

    assert send_result["success"] is True
    message_id = send_result["message_id"]
    persisted_content = send_result["content"]
    assert base_content in persisted_content
    assert f"<@{live_bot.user.id}>" in persisted_content
    if TEST_ROLE_ID:
        assert f"<@&{int(TEST_ROLE_ID)}>" in persisted_content

    message_result = await discord_get_message(
        channel_id=TEST_CHANNEL_ID,
        message_id=message_id,
        ctx=live_ctx,
    )
    assert message_result["id"] == message_id
    assert message_result["content"] == persisted_content

    recent_result = await discord_get_recent_messages(
        channel_id=TEST_CHANNEL_ID,
        limit=20,
        ctx=live_ctx,
    )
    assert any(msg["id"] == message_id for msg in recent_result["messages"])

    channel_info = await discord_get_channel_info(
        channel_id=TEST_CHANNEL_ID,
        ctx=live_ctx,
    )
    assert channel_info["id"] == TEST_CHANNEL_ID
    assert channel_info["name"] == message_result["channel_name"]

    # Clean up the message to avoid polluting the channel
    channel = live_bot.get_channel(
        int(TEST_CHANNEL_ID)
    ) or await live_bot.fetch_channel(int(TEST_CHANNEL_ID))
    try:
        message = await channel.fetch_message(int(message_id))
        await message.delete()
    except Exception:
        # If cleanup fails we still allow the test to pass, but we log via context.
        await live_ctx.info(f"Failed to delete test message {message_id}")
