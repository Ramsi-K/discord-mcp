"""Main MCP server entry point for Discord MCP."""

import asyncio
import logging
import os
from functools import wraps

from mcp.server.fastmcp import FastMCP

from .config import Config


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Global variables
discord_bot = None
bot_task = None
registry = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(
    name="Discord MCP",
    description="MCP server for Discord integration",
    log_level="INFO",
)


# MCP Resources - provide documentation and tool listings
@mcp.resource("discord://tools/list")
async def list_all_tools():
    """List all available Discord MCP tools with descriptions."""
    return {
        "core_tools": {
            "discord_list_servers": "List all servers (guilds) the bot is a member of",
            "discord_list_channels": "List channels in a Discord server with optional type filtering",
            "discord_get_channel_info": "Get detailed information about a Discord channel",
            "discord_bot_status": "Get the current status and health information of the Discord bot",
            "discord_ping": "Ping Discord to check connection health and optionally verify server access",
            "discord_get_recent_messages": "Get recent messages from a Discord channel with pagination support",
            "discord_get_message": "Get a specific message by ID from a Discord channel",
            "discord_send_message": "Send a message to a Discord channel with optional reply and mention controls (@here, @everyone, users, roles)",
        },
        "campaign_tools": {
            "discord_create_campaign": "Create a new reaction opt-in reminder campaign",
            "discord_list_campaigns": "List all campaigns with optional status filtering",
            "discord_get_campaign": "Get detailed information about a specific campaign",
            "discord_update_campaign_status": "Update campaign status (active, completed, cancelled)",
            "discord_delete_campaign": "Delete a campaign and all its associated opt-ins",
            "discord_tally_optins": "Fetch reactions from Discord and store deduplicated opt-ins for a campaign",
            "discord_list_optins": "List opt-ins for a campaign with pagination support",
            "discord_build_reminder": "Build reminder message with @mention chunking under 2000 characters",
            "discord_send_reminder": "Send reminder messages with rate limiting and batch processing",
            "discord_run_due_reminders": "Process scheduled campaigns that are due for reminders",
        },
        "search_tools": {
            "server_info": "Get detailed information about a Discord server",
            "list_servers": "List all servers the bot is in",
            "server_channels": "Get all channels in a Discord server",
            "server_roles": "Get all roles in a Discord server",
            "find_server": "Find a server by name (supports partial matching)",
            "find_channel": "Find a channel by name in a server (supports partial matching)",
            "find_role": "Find a role by name in a server (supports partial matching)",
        },
    }


@mcp.resource("discord://docs/campaign-flow")
async def campaign_flow_docs():
    """Get campaign workflow documentation."""
    try:
        from pathlib import Path
        docs_path = Path(__file__).parent.parent.parent / "docs" / "CAMPAIGN_FLOW.md"
        if docs_path.exists():
            return docs_path.read_text(encoding="utf-8")
        else:
            return "Campaign flow documentation not found. See docs/CAMPAIGN_FLOW.md in the repository."
    except Exception as e:
        return f"Error loading campaign flow documentation: {e}"


@mcp.resource("discord://config/info")
async def config_info():
    """Get current Discord MCP configuration."""
    config = Config()
    return {
        "database_path": str(config.database_path),
        "guild_allowlist": config.guild_allowlist,
        "log_level": config.log_level,
        "dry_run": config.dry_run,
        "token_configured": bool(config.discord_token),
    }


# Helper function to ensure Discord bot is ready
def require_discord_bot(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global discord_bot
        if not discord_bot or discord_bot.is_closed() or not discord_bot.user:
            # Try to start the bot if it's not running
            token = kwargs.get("token", "") or os.getenv("DISCORD_TOKEN", "")
            if not token:
                return {
                    "error": "Discord token not provided and DISCORD_TOKEN environment variable not set"
                }

            start_result = await ensure_bot_running(token)
            if not start_result.get("success"):
                return {
                    "error": f"Could not start Discord bot: {start_result.get('error', 'Unknown error')}"
                }

        return await func(*args, **kwargs)

    return wrapper


async def ensure_bot_running(token: str = "") -> dict:
    """Ensure the Discord bot is running and connected."""
    global discord_bot, bot_task, registry

    config = Config()
    logger = logging.getLogger(__name__)

    if not token:
        token = config.discord_token

    # Check if bot is already running and connected
    if discord_bot and not discord_bot.is_closed() and discord_bot.user:
        logger.info(f"Bot is already running as {discord_bot.user}")
        return {
            "success": True,
            "message": "Bot is already running",
            "bot_user": str(discord_bot.user),
            "guild_count": (
                len(discord_bot.guilds) if discord_bot.guilds else 0
            ),
        }

    try:
        # Import the bot class
        from .discord_client.bot import DiscordMCPBot

        # Create new bot instance
        discord_bot = DiscordMCPBot(config)

        # Start the bot in a background task
        bot_task = asyncio.create_task(discord_bot.start(token))

        # Wait for the bot to connect and guilds to load
        max_wait = 15  # seconds
        for i in range(max_wait):
            if discord_bot.user:
                logger.info(
                    f"Bot connected after {i+1} seconds as {discord_bot.user}"
                )
                # Wait a bit more for guilds to load
                logger.info("Waiting for guilds to load...")
                for j in range(5):  # Wait up to 5 more seconds for guilds
                    await asyncio.sleep(1)
                    if discord_bot.guilds:
                        logger.info(
                            f"Guilds loaded: {len(discord_bot.guilds)} guilds found"
                        )
                        break
                    logger.info(f"Waiting for guilds: {j+1}s")
                break
            await asyncio.sleep(1)
            logger.info(f"Waiting for bot to connect: {i+1}s")

        if not discord_bot.user:
            return {"error": "Bot failed to connect within timeout period"}

        # Initialize server registry if not already done
        if not registry:
            from .server_registry_wrapper import ServerRegistry

            registry = ServerRegistry(discord_bot)
            init_success = await registry.initialize()
            if not init_success:
                logger.warning("Failed to initialize server registry")
            else:
                # Automatically populate the registry with current Discord data
                logger.info("Populating server registry with Discord data...")
                update_result = await registry.update_registry()
                if update_result.get("success"):
                    logger.info("Server registry populated successfully")
                else:
                    logger.warning(
                        f"Failed to populate server registry: {update_result.get('error', 'Unknown error')}"
                    )

        return {
            "success": True,
            "message": "Discord bot started successfully",
            "bot_user": str(discord_bot.user),
            "guild_count": (
                len(discord_bot.guilds) if discord_bot.guilds else 0
            ),
        }

    except Exception as e:
        logger.error(f"Failed to start Discord bot: {str(e)}")
        return {"error": f"Failed to start Discord bot: {str(e)}"}


@mcp.tool(
    name="discord_start_bot",
    description="Start the Discord bot",
)
async def discord_start_bot(token: str = ""):
    """Start the Discord bot."""
    return await ensure_bot_running(token)


# discord_get_channel_info moved to core.py and registered via register_tools()
# discord_bot_status moved to core.py and registered via register_tools()


# Registry management tools
@mcp.tool(
    name="registry_get_server",
    description="Get a server by name, alias, or ID",
)
@require_discord_bot
async def registry_get_server(reference: str, user_id: str = "system"):
    """Get a server by name, alias, or ID."""
    global registry

    if not registry:
        return {"error": "Server registry not initialized"}

    try:
        # Set the current user for context tracking
        registry.set_current_user(user_id)

        # Get the server
        server = registry.api.get_server(reference)
        if server:
            # Track this server in context
            registry.track_context("server", server.id)

            return {
                "success": True,
                "server": {
                    "id": server.discord_id,  # Use Discord ID directly
                    "name": server.name,
                    "description": server.description,
                },
            }
        else:
            return {
                "success": False,
                "error": f"Server '{reference}' not found",
            }
    except Exception as e:
        logger.error(f"Error getting server: {str(e)}")
        return {"error": f"Error getting server: {str(e)}"}


@mcp.tool(
    name="registry_get_channel",
    description="Get a channel by name, alias, or ID",
)
@require_discord_bot
async def registry_get_channel(
    reference: str, server_reference: str = None, user_id: str = "system"
):
    """Get a channel by name, alias, or ID."""
    global registry

    if not registry:
        return {"error": "Server registry not initialized"}

    try:
        # Set the current user for context tracking
        registry.set_current_user(user_id)

        # Get the channel
        channel = registry.api.get_channel(reference, server_reference)
        if channel:
            # Track this channel in context
            registry.track_context("channel", channel.id)

            return {
                "success": True,
                "channel": {
                    "id": channel.discord_id,  # Use Discord ID directly
                    "name": channel.name,
                    "type": (
                        channel.type.value
                        if hasattr(channel.type, "value")
                        else str(channel.type)
                    ),
                },
            }
        else:
            return {
                "success": False,
                "error": f"Channel '{reference}' not found",
            }
    except Exception as e:
        logger.error(f"Error getting channel: {str(e)}")
        return {"error": f"Error getting channel: {str(e)}"}


@mcp.tool(
    name="registry_get_role",
    description="Get a role by name, alias, or ID",
)
@require_discord_bot
async def registry_get_role(
    reference: str, server_reference: str = None, user_id: str = "system"
):
    """Get a role by name, alias, or ID."""
    global registry

    if not registry:
        return {"error": "Server registry not initialized"}

    try:
        # Set the current user for context tracking
        registry.set_current_user(user_id)

        # Get the role
        role = registry.api.get_role(reference, server_reference)
        if role:
            # Track this role in context
            registry.track_context("role", role.id)

            return {
                "success": True,
                "role": {
                    "id": role.discord_id,  # Use Discord ID directly
                    "name": role.name,
                    "color": role.color,
                    "mentionable": role.mentionable,
                },
            }
        else:
            return {"success": False, "error": f"Role '{reference}' not found"}
    except Exception as e:
        logger.error(f"Error getting role: {str(e)}")
        return {"error": f"Error getting role: {str(e)}"}


@mcp.tool(
    name="registry_update",
    description="Update the server registry with current Discord data",
)
@require_discord_bot
async def registry_update(server_id: str = ""):
    """Update the server registry with current Discord data."""
    global registry

    if not registry:
        return {"error": "Server registry not initialized"}

    try:
        result = await registry.update_registry(
            server_id if server_id else None
        )
        return result
    except Exception as e:
        logger.error(f"Error updating registry: {str(e)}")
        return {"error": f"Error updating registry: {str(e)}"}


@mcp.tool(
    name="registry_track_context",
    description="Track an entity in the conversation context",
)
@require_discord_bot
async def registry_track_context(
    entity_type: str,
    entity_id: str,
    user_id: str = "system",
):
    """Track an entity in the conversation context."""
    global registry

    if not registry:
        return {"error": "Server registry not initialized"}

    try:
        # Set the current user for context tracking
        registry.set_current_user(user_id)

        # Track the entity
        success = registry.track_context(entity_type, int(entity_id))

        if success:
            return {
                "success": True,
                "message": f"Entity {entity_type}:{entity_id} tracked in context for user {user_id}",
            }
        else:
            return {
                "error": f"Failed to track entity {entity_type}:{entity_id} in context"
            }
    except Exception as e:
        logger.error(f"Error tracking context: {str(e)}")
        return {"error": f"Error tracking context: {str(e)}"}


# discord_list_channels tool removed - using server_registry_tools.get_server_channels instead


# discord_list_roles tool removed - using server_registry_tools.get_server_roles instead


# Register additional tools from the tools module
async def register_additional_tools():
    try:
        # Import tools
        from .tools.register_tools import register_tools
        from .tools.search_tools import (
            list_servers,
            get_server_channels,
            get_server_roles,
            get_server_info,
            find_server_by_name,
            find_channel_by_name,
            find_role_by_name,
        )

        # Register standard tools (this registers: server_info, list_servers, server_channels, server_roles, find_server, find_channel, find_role)
        await register_tools(mcp)

        # Note: Core Discord tools are now registered via register_tools()

        logger.info("Additional tools registered successfully")
    except Exception as e:
        logger.error(f"Error registering additional tools: {e}")


# Initialize entity resolver
entity_resolver = None


async def get_entity_resolver():
    """Get or initialize the entity resolver."""
    global entity_resolver, registry

    if entity_resolver is None and registry and registry.api:
        from .nlp_processor import EntityResolver

        entity_resolver = EntityResolver(registry.api)

    return entity_resolver


def run_server() -> None:
    """Run the Discord MCP server."""
    config = Config()

    # Set up logging
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)

    logger.info("Starting Discord MCP Server...")
    logger.info(f"DRY_RUN mode: {config.dry_run}")

    if config.guild_allowlist:
        logger.info(f"Guild allowlist: {config.guild_allowlist}")
    else:
        logger.info(
            "No guild allowlist configured - bot will work with all guilds"
        )

    # Update MCP server log level
    mcp.log_level = config.log_level

    # Register additional tools before starting the server
    asyncio.run(register_additional_tools())

    # Run the MCP server
    logger.info("Starting MCP server on stdio transport...")
    mcp.run(transport="stdio")


def main() -> None:
    """Main entry point for the discord-mcp console script."""
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nShutting down Discord MCP Server...")
    except Exception as e:
        print(f"Error starting Discord MCP Server: {e}")
        exit(1)


if __name__ == "__main__":
    main()
