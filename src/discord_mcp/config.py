"""Configuration management for Discord MCP server."""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Discord MCP server."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self._validate_required_env_vars()

    @property
    def discord_token(self) -> str:
        """Discord bot token."""
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is required")
        return token

    @property
    def guild_allowlist(self) -> Optional[List[str]]:
        """List of allowed guild IDs. If None, all guilds are allowed."""
        allowlist = os.getenv("GUILD_ALLOWLIST")
        if not allowlist:
            return None
        return [
            guild_id.strip()
            for guild_id in allowlist.split(",")
            if guild_id.strip()
        ]

    @property
    def log_level(self) -> str:
        """Logging level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def dry_run(self) -> bool:
        """Whether to run in dry-run mode (mock Discord API calls)."""
        return os.getenv("DRY_RUN", "false").lower() in (
            "true",
            "1",
            "yes",
            "on",
        )

    @property
    def database_path(self) -> Path:
        """Path to SQLite database file."""
        db_path = os.getenv("MCP_DISCORD_DB_PATH", "discord_mcp.db")
        return Path(db_path)

    def _validate_required_env_vars(self) -> None:
        """Validate that required environment variables are set."""
        required_vars = ["DISCORD_TOKEN"]
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            error_msg = (
                f"Missing required environment variables: {', '.join(missing_vars)}\n\n"
                f"Please configure your MCP client to include:\n"
                f'  "env": {{\n'
                f'    "DISCORD_TOKEN": "your_discord_bot_token_here",\n'
                f'    "MCP_DISCORD_DB_PATH": "/path/to/discord_registry.db"\n'
                f"  }}\n\n"
                f"See the README for complete configuration instructions."
            )
            raise ValueError(error_msg)

    def validate_log_level(self) -> None:
        """Validate that log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL '{self.log_level}'. Must be one of: {', '.join(valid_levels)}"
            )

    def is_guild_allowed(self, guild_id: str) -> bool:
        """Check if a guild ID is in the allowlist."""
        if self.guild_allowlist is None:
            return True
        return guild_id in self.guild_allowlist
