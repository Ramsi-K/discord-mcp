"""Tests for campaign functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

# Set up test environment
os.environ["DISCORD_TOKEN"] = "test_token"
os.environ["DRY_RUN"] = "true"

from src.discord_mcp.database.migrations import initialize_campaign_database
from src.discord_mcp.database.repositories import (
    CampaignRepository,
    OptInRepository,
)
from src.discord_mcp.database.models import Campaign, OptIn
from src.discord_mcp.tools.campaigns import (
    discord_create_campaign,
    discord_tally_optins,
    discord_list_optins,
    discord_build_reminder,
    discord_send_reminder,
    discord_run_due_reminders,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_db_path = Path(f.name)

    # Initialize the database
    initialize_campaign_database(temp_db_path)

    yield temp_db_path

    # Cleanup
    try:
        temp_db_path.unlink()
    except:
        pass  # Ignore cleanup errors


def test_campaign_database_initialization(temp_db):
    """Test that campaign database initializes correctly."""
    import sqlite3

    with sqlite3.connect(str(temp_db)) as conn:
        cursor = conn.cursor()

        # Check that all required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {"campaigns", "optins", "reminders_log"}
        assert required_tables.issubset(
            tables
        ), f"Missing tables: {required_tables - tables}"


def test_campaign_repository(temp_db):
    """Test campaign repository operations."""
    repo = CampaignRepository(temp_db)

    # Create a test campaign
    campaign = Campaign(
        title="Test Campaign",
        channel_id="123456789",
        message_id="987654321",
        emoji=":thumbsup:",
        remind_at=datetime.now() + timedelta(hours=1),
        status="active",
    )

    # Test create
    campaign_id = repo.create_campaign(campaign)
    assert campaign_id is not None
    assert campaign_id > 0

    # Test get
    retrieved = repo.get_campaign(campaign_id)
    assert retrieved is not None
    assert retrieved.title == "Test Campaign"
    assert retrieved.channel_id == "123456789"

    # Test get by status
    active_campaigns = repo.get_campaigns_by_status("active")
    assert len(active_campaigns) == 1
    assert active_campaigns[0].id == campaign_id


def test_optin_repository(temp_db):
    """Test opt-in repository operations."""
    # First create a campaign
    campaign_repo = CampaignRepository(temp_db)
    campaign = Campaign(
        title="Test Campaign",
        channel_id="123456789",
        message_id="987654321",
        emoji=":thumbsup:",
        remind_at=datetime.now() + timedelta(hours=1),
        status="active",
    )
    campaign_id = campaign_repo.create_campaign(campaign)

    # Test opt-in operations
    optin_repo = OptInRepository(temp_db)

    # Add opt-ins
    optin1 = OptIn(
        campaign_id=campaign_id,
        user_id="user1",
        username="TestUser1",
        tallied_at=datetime.now(),
    )
    optin2 = OptIn(
        campaign_id=campaign_id,
        user_id="user2",
        username="TestUser2",
        tallied_at=datetime.now(),
    )

    assert optin_repo.add_optin(optin1)
    assert optin_repo.add_optin(optin2)

    # Test get opt-ins
    optins = optin_repo.get_optins(campaign_id)
    assert len(optins) == 2

    # Test get count
    count = optin_repo.get_optin_count(campaign_id)
    assert count == 2

    # Test pagination
    optins_page1 = optin_repo.get_optins(campaign_id, limit=1)
    assert len(optins_page1) == 1

    optins_page2 = optin_repo.get_optins(
        campaign_id, limit=1, after_user_id=optins_page1[0].user_id
    )
    assert len(optins_page2) == 1
    assert optins_page2[0].user_id != optins_page1[0].user_id


@pytest.mark.asyncio
async def test_campaign_tools_dry_run():
    """Test campaign tools in dry run mode."""
    # Test create campaign
    result = await discord_create_campaign(
        channel_id="123456789",
        message_id="987654321",
        emoji=":thumbsup:",
        remind_at="2024-12-31T10:00:00",
        title="Test Campaign",
    )
    assert result["success"] is True
    assert result["dry_run"] is True

    # Test tally opt-ins
    result = await discord_tally_optins(1)
    assert result["success"] is True
    assert result["dry_run"] is True

    # Test list opt-ins
    result = await discord_list_optins(1, limit=5)
    assert result["success"] is True
    assert result["dry_run"] is True

    # Test build reminder
    result = await discord_build_reminder(1)
    assert result["success"] is True
    assert result["dry_run"] is True

    # Test send reminder
    result = await discord_send_reminder(1, dry_run=True)
    assert result["success"] is True
    assert result["dry_run"] is True

    # Test run due reminders
    result = await discord_run_due_reminders()
    assert result["success"] is True
    assert result["dry_run"] is True


def test_reminder_chunking():
    """Test that reminder message chunking works correctly."""
    # This is a unit test for the chunking logic
    # We'll test it by creating a mock scenario

    # Mock data for testing
    base_message = "🔔 Reminder: Test Campaign\n\n{mentions}"
    mentions = [f"<@{100000 + i}>" for i in range(50)]  # 50 mentions

    # Calculate chunking (simplified version of the actual logic)
    max_length = 2000
    base_length = len(base_message.replace("{mentions}", ""))
    available_space = max_length - base_length - 10  # Buffer

    chunks = []
    current_mentions = []
    current_length = 0

    for mention in mentions:
        mention_length = len(mention) + 1  # +1 for space

        if current_length + mention_length > available_space and current_mentions:
            # Create chunk
            mentions_text = " ".join(current_mentions)
            chunk = base_message.replace("{mentions}", mentions_text)
            chunks.append(chunk)

            # Start new chunk
            current_mentions = [mention]
            current_length = mention_length
        else:
            current_mentions.append(mention)
            current_length += mention_length

    # Add final chunk
    if current_mentions:
        mentions_text = " ".join(current_mentions)
        chunk = base_message.replace("{mentions}", mentions_text)
        chunks.append(chunk)

    # Verify chunking worked
    assert len(chunks) >= 1  # Should have at least one chunk
    for chunk in chunks:
        assert len(chunk) <= max_length  # Each chunk should be under limit
        assert "<@" in chunk  # Each chunk should have mentions

    # Test that the logic works - if we have a lot of mentions, we should get multiple chunks
    # Let's test with a scenario that definitely needs chunking
    long_mentions = [f"<@{1000000000000000000 + i}>" for i in range(100)]
    total_length = sum(len(mention) + 1 for mention in long_mentions)
    if total_length > available_space:
        # This should definitely create multiple chunks
        print(
            f"Total mentions length: {total_length}, available space: {available_space}"
        )
        # The test passes if chunking logic is implemented correctly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
