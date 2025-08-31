"""Database migrations for Discord MCP campaigns."""

import sqlite3
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class CampaignMigrations:
    """Database migrations for campaign functionality."""

    def __init__(self, db_path: Path):
        """Initialize migrations manager."""
        self.db_path = db_path

    def get_migrations(self) -> List[str]:
        """Get list of migration SQL statements."""
        return [
            # Migration 1: Create campaigns table
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                channel_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                emoji TEXT NOT NULL,
                remind_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            );
            """,
            # Migration 2: Create optins table
            """
            CREATE TABLE IF NOT EXISTS optins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT,
                tallied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                UNIQUE(campaign_id, user_id)
            );
            """,
            # Migration 3: Create reminders_log table
            """
            CREATE TABLE IF NOT EXISTS reminders_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recipient_count INTEGER,
                message_chunks INTEGER,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            );
            """,
            # Migration 4: Create indexes for performance
            """
            CREATE INDEX IF NOT EXISTS idx_campaigns_status 
            ON campaigns (status);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_campaigns_remind_at 
            ON campaigns (remind_at);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_optins_campaign_id 
            ON optins (campaign_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_optins_user_id 
            ON optins (user_id);
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_reminders_log_campaign_id 
            ON reminders_log (campaign_id);
            """,
        ]

    def run_migrations(self) -> bool:
        """Run all migrations."""
        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Run each migration
                for i, migration in enumerate(self.get_migrations(), 1):
                    try:
                        cursor.execute(migration)
                        logger.debug(f"Migration {i} completed successfully")
                    except sqlite3.Error as e:
                        logger.error(f"Migration {i} failed: {e}")
                        return False

                conn.commit()
                logger.info("All campaign migrations completed successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False

    def verify_schema(self) -> bool:
        """Verify that all tables exist with correct schema."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Check if all required tables exist
                required_tables = ["campaigns", "optins", "reminders_log"]

                for table in required_tables:
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table,),
                    )
                    if not cursor.fetchone():
                        logger.error(f"Table '{table}' does not exist")
                        return False

                logger.info("Campaign schema verification passed")
                return True

        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            return False


def initialize_campaign_database(db_path: Path) -> bool:
    """Initialize campaign database with all required tables."""
    migrations = CampaignMigrations(db_path)

    # Run migrations
    if not migrations.run_migrations():
        logger.error("Failed to run campaign migrations")
        return False

    # Verify schema
    if not migrations.verify_schema():
        logger.error("Campaign schema verification failed")
        return False

    logger.info("Campaign database initialized successfully")
    return True
