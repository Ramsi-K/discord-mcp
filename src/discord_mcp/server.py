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


@mcp.tool(
    name="discord_send_message",
    description="Send a message to a Discord channel",
)
@require_discord_bot
async def discord_send_message(
    channel_id: str,
    message: str,
    mention_everyone: bool = False,
    server_id: str = None,
    token: str = "",
):
    """Send a message to a Discord channel, starting bot if needed.

    The channel_id can be a channel name, alias, or ID. If it's a name or alias,
    it will be resolved to an ID using the server registry.
    """
    global discord_bot

    try:
        # Resolve channel ID if it's not a numeric ID
        if not channel_id.isdigit():
            resolver = await get_entity_resolver()
            if resolver:
                resolved_id = await resolver.resolve_channel(
                    channel_id, server_id
                )
                logger.info(
                    f"Resolved channel '{channel_id}' to ID '{resolved_id}'"
                )
                channel_id = resolved_id

        logger.info(f"Sending message to channel {channel_id}")
        return await discord_bot.send_direct_message(
            channel_id, message, mention_everyone
        )
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return {"error": f"Error sending message: {str(e)}"}


@mcp.tool(
    name="discord_get_channel_info",
    description="Get information about a Discord channel",
)
@require_discord_bot
async def discord_get_channel_info(
    channel_id: str, server_id: str = None, token: str = ""
):
    """Get information about a Discord channel, starting bot if needed.

    The channel_id can be a channel name, alias, or ID. If it's a name or alias,
    it will be resolved to an ID using the server registry.
    """
    global discord_bot

    try:
        # Resolve channel ID if it's not a numeric ID
        if not channel_id.isdigit():
            resolver = await get_entity_resolver()
            if resolver:
                resolved_id = await resolver.resolve_channel(
                    channel_id, server_id
                )
                logger.info(
                    f"Resolved channel '{channel_id}' to ID '{resolved_id}'"
                )
                channel_id = resolved_id

        logger.info(f"Getting info for channel {channel_id}")
        return await discord_bot.get_channel_info(channel_id)
    except Exception as e:
        logger.error(f"Error getting channel info: {str(e)}")
        return {"error": f"Error getting channel info: {str(e)}"}


# discord_list_servers tool removed - using server_registry_tools.list_servers instead


@mcp.tool(
    name="discord_bot_status",
    description="Get the current status of the Discord bot",
)
async def discord_bot_status():
    """Get the current status of the Discord bot."""
    global discord_bot

    if not discord_bot:
        return {
            "status": "not_started",
            "message": "Discord bot has not been started",
        }

    if discord_bot.is_closed():
        return {
            "status": "closed",
            "message": "Discord bot is closed",
        }

    return {
        "status": "running",
        "bot_user": (
            str(discord_bot.user) if discord_bot.user else "Connecting..."
        ),
        "guild_count": len(discord_bot.guilds) if discord_bot.guilds else 0,
        "guilds": (
            [{"id": str(g.id), "name": g.name} for g in discord_bot.guilds]
            if discord_bot.guilds
            else []
        ),
    }


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
                    "id": server.id,
                    "discord_id": server.discord_id,
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
                    "id": channel.id,
                    "discord_id": channel.discord_id,
                    "name": channel.name,
                    "type": (
                        channel.type.value
                        if hasattr(channel.type, "value")
                        else str(channel.type)
                    ),
                    "server_id": channel.server_id,
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
                    "id": role.id,
                    "discord_id": role.discord_id,
                    "name": role.name,
                    "color": role.color,
                    "server_id": role.server_id,
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
        from .tools.server_registry_tools import (
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
