"""
Server registry initialization module.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .db import DatabaseConnection
from .db.init_db import initialize_database
from .api import ServerRegistryAPIImpl
from ..database.migrations import initialize_campaign_database

logger = logging.getLogger(__name__)


def init_server_registry(
    discord_client=None, db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initialize the server registry.

    Args:
        discord_client: The Discord client to use for API calls.
        db_path (Optional[str]): Path to the database file. If not provided, will use MCP_DISCORD_DB_PATH env var or default.

    Returns:
        Dict[str, Any]: Result of the initialization.
    """
    try:
        # Initialize database connection
        db_conn = DatabaseConnection(db_path)

        # Initialize database schema
        initialize_database(db_conn)

        # Initialize campaign database schema in the same database file
        db_path_obj = Path(db_conn._db_path)
        campaign_init_success = initialize_campaign_database(db_path_obj)
        if not campaign_init_success:
            logger.warning(
                "Campaign database initialization failed, but continuing with server registry"
            )

        # Create API implementation
        api = ServerRegistryAPIImpl(discord_client=discord_client)

        return {
            "success": True,
            "message": "Server registry initialized successfully",
            "api": api,
            "db_path": db_conn._db_path,
            "campaign_db_initialized": campaign_init_success,
        }
    except Exception as e:
        logger.error(f"Failed to initialize server registry: {e}")
        return {
            "success": False,
            "message": f"Failed to initialize server registry: {str(e)}",
        }


def load_registry_from_memory(discord_client=None) -> Dict[str, Any]:
    """
    Load the server registry from memory if it exists, otherwise initialize it.

    Args:
        discord_client: The Discord client to use for API calls.

    Returns:
        Dict[str, Any]: Result of the loading or initialization.
    """
    # This is a simple implementation that just initializes the registry
    # In a more complex implementation, you might want to check if the registry is already loaded
    # and return the existing instance if it is.
    return init_server_registry(discord_client)
