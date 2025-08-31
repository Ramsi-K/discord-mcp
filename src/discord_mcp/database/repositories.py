"""Repository classes for campaign data access."""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Campaign, OptIn, ReminderLog, DatabaseConnection

logger = logging.getLogger(__name__)


class CampaignRepository:
    """Repository for campaign data operations."""

    def __init__(self, db_path: Path):
        """Initialize campaign repository."""
        self.db_connection = DatabaseConnection(db_path)

    def create_campaign(self, campaign: Campaign) -> Optional[int]:
        """Create a new campaign and return its ID."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO campaigns (title, channel_id, message_id, emoji, remind_at, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        campaign.title,
                        campaign.channel_id,
                        campaign.message_id,
                        campaign.emoji,
                        (
                            campaign.remind_at.isoformat()
                            if campaign.remind_at
                            else None
                        ),
                        campaign.status,
                    ),
                )

                campaign_id = cursor.lastrowid
                logger.info(f"Created campaign with ID {campaign_id}")
                return campaign_id

        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            return None

    def get_campaign(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, title, channel_id, message_id, emoji, remind_at, created_at, status
                    FROM campaigns WHERE id = ?
                """,
                    (campaign_id,),
                )

                row = cursor.fetchone()
                if row:
                    return Campaign(
                        id=row["id"],
                        title=row["title"],
                        channel_id=row["channel_id"],
                        message_id=row["message_id"],
                        emoji=row["emoji"],
                        remind_at=(
                            datetime.fromisoformat(row["remind_at"])
                            if row["remind_at"]
                            else None
                        ),
                        created_at=(
                            datetime.fromisoformat(row["created_at"])
                            if row["created_at"]
                            else None
                        ),
                        status=row["status"],
                    )
                return None

        except Exception as e:
            logger.error(f"Failed to get campaign {campaign_id}: {e}")
            return None

    def get_campaigns_by_status(
        self, status: str = "active"
    ) -> List[Campaign]:
        """Get campaigns by status."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, title, channel_id, message_id, emoji, remind_at, created_at, status
                    FROM campaigns WHERE status = ?
                    ORDER BY remind_at ASC
                """,
                    (status,),
                )

                campaigns = []
                for row in cursor.fetchall():
                    campaigns.append(
                        Campaign(
                            id=row["id"],
                            title=row["title"],
                            channel_id=row["channel_id"],
                            message_id=row["message_id"],
                            emoji=row["emoji"],
                            remind_at=(
                                datetime.fromisoformat(row["remind_at"])
                                if row["remind_at"]
                                else None
                            ),
                            created_at=(
                                datetime.fromisoformat(row["created_at"])
                                if row["created_at"]
                                else None
                            ),
                            status=row["status"],
                        )
                    )

                return campaigns

        except Exception as e:
            logger.error(f"Failed to get campaigns by status {status}: {e}")
            return []

    def get_due_campaigns(self, now: datetime = None) -> List[Campaign]:
        """Get campaigns that are due for reminders."""
        if now is None:
            now = datetime.now()

        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, title, channel_id, message_id, emoji, remind_at, created_at, status
                    FROM campaigns 
                    WHERE status = 'active' AND remind_at <= ?
                    ORDER BY remind_at ASC
                """,
                    (now.isoformat(),),
                )

                campaigns = []
                for row in cursor.fetchall():
                    campaigns.append(
                        Campaign(
                            id=row["id"],
                            title=row["title"],
                            channel_id=row["channel_id"],
                            message_id=row["message_id"],
                            emoji=row["emoji"],
                            remind_at=(
                                datetime.fromisoformat(row["remind_at"])
                                if row["remind_at"]
                                else None
                            ),
                            created_at=(
                                datetime.fromisoformat(row["created_at"])
                                if row["created_at"]
                                else None
                            ),
                            status=row["status"],
                        )
                    )

                return campaigns

        except Exception as e:
            logger.error(f"Failed to get due campaigns: {e}")
            return []

    def update_campaign_status(self, campaign_id: int, status: str) -> bool:
        """Update campaign status."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE campaigns SET status = ? WHERE id = ?
                """,
                    (status, campaign_id),
                )

                if cursor.rowcount > 0:
                    logger.info(
                        f"Updated campaign {campaign_id} status to {status}"
                    )
                    return True
                else:
                    logger.warning(f"No campaign found with ID {campaign_id}")
                    return False

        except Exception as e:
            logger.error(
                f"Failed to update campaign {campaign_id} status: {e}"
            )
            return False


class OptInRepository:
    """Repository for opt-in data operations."""

    def __init__(self, db_path: Path):
        """Initialize opt-in repository."""
        self.db_connection = DatabaseConnection(db_path)

    def add_optin(self, optin: OptIn) -> bool:
        """Add an opt-in (idempotent - won't duplicate)."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO optins (campaign_id, user_id, username, tallied_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        optin.campaign_id,
                        optin.user_id,
                        optin.username,
                        (
                            optin.tallied_at.isoformat()
                            if optin.tallied_at
                            else datetime.now().isoformat()
                        ),
                    ),
                )

                logger.debug(
                    f"Added opt-in for user {optin.user_id} in campaign {optin.campaign_id}"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to add opt-in: {e}")
            return False

    def get_optins(
        self, campaign_id: int, limit: int = 100, after_user_id: str = None
    ) -> List[OptIn]:
        """Get opt-ins for a campaign with pagination."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                if after_user_id:
                    cursor.execute(
                        """
                        SELECT id, campaign_id, user_id, username, tallied_at
                        FROM optins 
                        WHERE campaign_id = ? AND user_id > ?
                        ORDER BY user_id ASC
                        LIMIT ?
                    """,
                        (campaign_id, after_user_id, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, campaign_id, user_id, username, tallied_at
                        FROM optins 
                        WHERE campaign_id = ?
                        ORDER BY user_id ASC
                        LIMIT ?
                    """,
                        (campaign_id, limit),
                    )

                optins = []
                for row in cursor.fetchall():
                    optins.append(
                        OptIn(
                            id=row["id"],
                            campaign_id=row["campaign_id"],
                            user_id=row["user_id"],
                            username=row["username"],
                            tallied_at=(
                                datetime.fromisoformat(row["tallied_at"])
                                if row["tallied_at"]
                                else None
                            ),
                        )
                    )

                return optins

        except Exception as e:
            logger.error(
                f"Failed to get opt-ins for campaign {campaign_id}: {e}"
            )
            return []

    def get_optin_count(self, campaign_id: int) -> int:
        """Get total count of opt-ins for a campaign."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT COUNT(*) as count FROM optins WHERE campaign_id = ?
                """,
                    (campaign_id,),
                )

                row = cursor.fetchone()
                return row["count"] if row else 0

        except Exception as e:
            logger.error(
                f"Failed to get opt-in count for campaign {campaign_id}: {e}"
            )
            return 0

    def clear_optins(self, campaign_id: int) -> bool:
        """Clear all opt-ins for a campaign (for re-tallying)."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    DELETE FROM optins WHERE campaign_id = ?
                """,
                    (campaign_id,),
                )

                logger.info(
                    f"Cleared {cursor.rowcount} opt-ins for campaign {campaign_id}"
                )
                return True

        except Exception as e:
            logger.error(
                f"Failed to clear opt-ins for campaign {campaign_id}: {e}"
            )
            return False


class ReminderLogRepository:
    """Repository for reminder log operations."""

    def __init__(self, db_path: Path):
        """Initialize reminder log repository."""
        self.db_connection = DatabaseConnection(db_path)

    def log_reminder(self, log_entry: ReminderLog) -> Optional[int]:
        """Log a reminder attempt."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO reminders_log (campaign_id, sent_at, recipient_count, message_chunks, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        log_entry.campaign_id,
                        (
                            log_entry.sent_at.isoformat()
                            if log_entry.sent_at
                            else datetime.now().isoformat()
                        ),
                        log_entry.recipient_count,
                        log_entry.message_chunks,
                        log_entry.success,
                        log_entry.error_message,
                    ),
                )

                log_id = cursor.lastrowid
                logger.info(f"Logged reminder attempt with ID {log_id}")
                return log_id

        except Exception as e:
            logger.error(f"Failed to log reminder: {e}")
            return None

    def get_reminder_logs(self, campaign_id: int) -> List[ReminderLog]:
        """Get reminder logs for a campaign."""
        try:
            with self.db_connection as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT id, campaign_id, sent_at, recipient_count, message_chunks, success, error_message
                    FROM reminders_log 
                    WHERE campaign_id = ?
                    ORDER BY sent_at DESC
                """,
                    (campaign_id,),
                )

                logs = []
                for row in cursor.fetchall():
                    logs.append(
                        ReminderLog(
                            id=row["id"],
                            campaign_id=row["campaign_id"],
                            sent_at=(
                                datetime.fromisoformat(row["sent_at"])
                                if row["sent_at"]
                                else None
                            ),
                            recipient_count=row["recipient_count"],
                            message_chunks=row["message_chunks"],
                            success=bool(row["success"]),
                            error_message=row["error_message"],
                        )
                    )

                return logs

        except Exception as e:
            logger.error(
                f"Failed to get reminder logs for campaign {campaign_id}: {e}"
            )
            return []
