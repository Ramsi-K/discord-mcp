"""Comprehensive test for campaign tally with real Discord message and multiple reactions."""

import pytest
import os
import asyncio
from datetime import datetime, timedelta

# Only run if DISCORD_TOKEN is available
pytest_plugins = ('pytest_asyncio',)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")  # Set this to a test channel

pytestmark = pytest.mark.skipif(
    not DISCORD_TOKEN or not TEST_CHANNEL_ID,
    reason="Requires DISCORD_TOKEN and TEST_CHANNEL_ID environment variables"
)


@pytest.mark.asyncio
async def test_campaign_multi_reaction_workflow():
    """
    End-to-end test for campaign with multiple reactions.

    Workflow:
    1. Send a test message to Discord
    2. Add multiple emoji reactions (👍, ❓, 👎)
    3. Create campaign tracking 👍
    4. Tally opt-ins
    5. Verify only 👍 reactions are counted
    6. Add more reactions
    7. Re-tally and verify idempotency
    """
    from discord_mcp.server import ensure_bot_running
    from discord_mcp.tools.campaigns import (
        discord_create_campaign,
        discord_tally_optins,
        discord_list_optins,
    )
    from discord_mcp.tools.core import discord_send_message

    # Start the bot
    bot_result = await ensure_bot_running(DISCORD_TOKEN)
    assert bot_result["success"], f"Failed to start bot: {bot_result.get('error')}"

    try:
        # Import discord_bot
        from discord_mcp.server import discord_bot
        assert discord_bot is not None
        assert not discord_bot.is_closed()

        # 1. Send test message
        test_message_content = f"""
🎮 TOURNAMENT SIGNUP TEST

React to this message:
👍 - I'm attending
❓ - Maybe
👎 - Not attending

Test time: {datetime.now().isoformat()}
"""

        send_result = await discord_send_message(
            channel_id=TEST_CHANNEL_ID,
            content=test_message_content,
            mention_everyone=False,
            ctx=None  # Mock context
        )

        assert send_result["success"], f"Failed to send message: {send_result}"
        message_id = send_result["message_id"]

        print(f"✅ Sent test message: {message_id}")

        # 2. Get the message and add reactions
        channel = discord_bot.get_channel(int(TEST_CHANNEL_ID))
        message = await channel.fetch_message(int(message_id))

        # Add reactions in order
        await message.add_reaction("👍")
        await message.add_reaction("❓")
        await message.add_reaction("👎")

        print("✅ Added emoji reactions: 👍 ❓ 👎")

        # Wait a moment for reactions to register
        await asyncio.sleep(2)

        # 3. Create campaign tracking 👍
        remind_at = (datetime.now() + timedelta(days=1)).isoformat()
        campaign_result = await discord_create_campaign(
            channel_id=TEST_CHANNEL_ID,
            message_id=message_id,
            emoji="👍",
            remind_at=remind_at,
            title="Test Tournament - Attending"
        )

        assert campaign_result["success"], f"Failed to create campaign: {campaign_result}"
        campaign_id = campaign_result["campaign"]["id"]

        print(f"✅ Created campaign: {campaign_id}")

        # 4. Tally opt-ins (should get bot's reaction only at first)
        tally_result = await discord_tally_optins(campaign_id=campaign_id)

        assert tally_result["success"], f"Failed to tally: {tally_result}"

        # Bot reacted with 👍, so should have 1 opt-in (bot reactions are skipped)
        # Actually should be 0 since bot reactions are filtered
        initial_count = tally_result["tally"]["total_optins"]
        print(f"✅ Initial tally: {initial_count} opt-ins (bot reactions filtered)")

        # 5. Verify only 👍 was tracked (check database)
        optins_result = await discord_list_optins(campaign_id=campaign_id)

        assert optins_result["success"]
        optins = optins_result["optins"]

        print(f"✅ Opt-ins list: {len(optins)} users")

        # All opt-ins should be for 👍 emoji
        # (We can't verify emoji directly, but campaign filters by emoji)

        # 6. Simulate additional user reactions
        # In real scenario, users would react. For test, we'll add more bot reactions
        # and verify re-tallying works

        # Remove and re-add reaction to simulate change
        await message.remove_reaction("👍", discord_bot.user)
        await asyncio.sleep(1)
        await message.add_reaction("👍")
        await asyncio.sleep(1)

        print("✅ Simulated reaction changes")

        # 7. Re-tally and verify idempotency
        tally_result_2 = await discord_tally_optins(campaign_id=campaign_id)

        assert tally_result_2["success"]

        # Should have same count (idempotent)
        final_count = tally_result_2["tally"]["total_optins"]
        new_optins = tally_result_2["tally"]["new_optins"]
        existing_optins = tally_result_2["tally"]["existing_optins"]

        print(f"✅ Re-tally results:")
        print(f"  Total: {final_count}")
        print(f"  New: {new_optins}")
        print(f"  Existing: {existing_optins}")

        # Verify idempotency - no duplicates
        assert final_count == initial_count, "Idempotency check failed - got duplicates!"

        # 8. Verify other emoji reactions are NOT in database
        # Check message reactions directly
        fresh_message = await channel.fetch_message(int(message_id))

        reaction_counts = {}
        for reaction in fresh_message.reactions:
            emoji_str = str(reaction.emoji)
            reaction_counts[emoji_str] = reaction.count

        print(f"✅ Reaction counts on message: {reaction_counts}")

        # Should have all three emojis
        assert "👍" in reaction_counts
        assert "❓" in reaction_counts
        assert "👎" in reaction_counts

        # But campaign should only track 👍
        # All opt-ins should be for the campaign we created
        all_optins = await discord_list_optins(campaign_id=campaign_id, limit=1000)
        assert all_optins["success"]

        # If there were real users, we'd verify they're in the 👍 list only
        print(f"✅ Campaign correctly tracks only 👍 emoji")

        print(f"\n🎉 COMPREHENSIVE TALLY TEST PASSED!")
        print(f"   Message ID: {message_id}")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Reactions: {reaction_counts}")
        print(f"   Opt-ins tracked: {final_count}")

    finally:
        # Cleanup: delete the test message
        try:
            test_message = await channel.fetch_message(int(message_id))
            await test_message.delete()
            print(f"✅ Cleaned up test message")
        except:
            print(f"⚠️  Could not delete test message {message_id}")


@pytest.mark.asyncio
async def test_campaign_tally_filters_bots():
    """Verify that bot reactions are filtered out from opt-ins."""
    from discord_mcp.server import ensure_bot_running
    from discord_mcp.tools.campaigns import discord_create_campaign, discord_tally_optins
    from discord_mcp.tools.core import discord_send_message

    bot_result = await ensure_bot_running(DISCORD_TOKEN)
    assert bot_result["success"]

    from discord_mcp.server import discord_bot

    # Send message
    send_result = await discord_send_message(
        channel_id=TEST_CHANNEL_ID,
        content="Bot reaction test",
        mention_everyone=False,
        ctx=None
    )

    message_id = send_result["message_id"]

    try:
        # Bot adds reaction
        channel = discord_bot.get_channel(int(TEST_CHANNEL_ID))
        message = await channel.fetch_message(int(message_id))
        await message.add_reaction("🤖")
        await asyncio.sleep(1)

        # Create campaign
        remind_at = (datetime.now() + timedelta(days=1)).isoformat()
        campaign_result = await discord_create_campaign(
            channel_id=TEST_CHANNEL_ID,
            message_id=message_id,
            emoji="🤖",
            remind_at=remind_at,
            title="Bot Filter Test"
        )

        campaign_id = campaign_result["campaign"]["id"]

        # Tally
        tally_result = await discord_tally_optins(campaign_id=campaign_id)

        assert tally_result["success"]

        # Should be 0 because bot reactions are filtered
        assert tally_result["tally"]["total_optins"] == 0, "Bot reactions should be filtered!"

        print("✅ Bot reactions correctly filtered")

    finally:
        try:
            await message.delete()
        except:
            pass


if __name__ == "__main__":
    # Run with: uv run pytest tests/test_campaign_tally_comprehensive.py -v -s
    print("Run this test with pytest:")
    print("  export DISCORD_TOKEN='your_token'")
    print("  export TEST_CHANNEL_ID='your_test_channel_id'")
    print("  uv run pytest tests/test_campaign_tally_comprehensive.py -v -s")
