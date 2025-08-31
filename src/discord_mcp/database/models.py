"""Database models for Discord MCP campaigns."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pathlib import Path


@dataclass
class Campaign:
    """Campaign model for reaction opt-in reminders."""

    id: Optional[int] = None
    title: Optional[str] = None
    channel_id: str = ""
    message_id: str = ""
    emoji: str = ""
    remind_at: datetime = None
    created_at: datetime = None
    status: str = "active"

    def to_dict(self) -> dict:
        """Convert campaign to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "channel_id": self.channel_id,
            "message_id": self.message_id,
            "emoji": self.emoji,
            "remind_at": (
                self.remind_at.isoformat() if self.remind_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "status": self.status,
        }


@dataclass
class OptIn:
    """OptIn model for campaign participants."""

    id: Optional[int] = None
    campaign_id: int = 0
    user_id: str = ""
    username: Optional[str] = None
    tallied_at: datetime = None

    def to_dict(self) -> dict:
        """Convert opt-in to dictionary."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "user_id": self.user_id,
            "username": self.username,
            "tallied_at": (
                self.tallied_at.isoformat() if self.tallied_at else None
            ),
        }


@dataclass
class ReminderLog:
    """ReminderLog model for tracking sent reminders."""

    id: Optional[int] = None
    campaign_id: int = 0
    sent_at: datetime = None
    recipient_count: int = 0
    message_chunks: int = 0
    success: bool = False
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert reminder log to dictionary."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "recipient_count": self.recipient_count,
            "message_chunks": self.message_chunks,
            "success": self.success,
            "error_message": self.error_message,
        }


class DatabaseConnection:
    """Database connection manager for campaigns."""

    def __init__(self, db_path: Path):
        """Initialize database connection."""
        self.db_path = db_path
        self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self):
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._connection:
            if exc_type is None:
                self._connection.commit()
            else:
                self._connection.rollback()
