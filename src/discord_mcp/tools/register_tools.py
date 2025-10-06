"""
Tools for Discord MCP server.
"""

from mcp.server.fastmcp import FastMCP
from .search_tools import (
    get_server_info,
    list_servers,
    get_server_channels,
    get_server_roles,
    find_server_by_name,
    find_channel_by_name,
    find_role_by_name,
)
from .core import (
    discord_list_servers,
    discord_list_channels,
    discord_get_channel_info,
    discord_bot_status,
    discord_ping,
    discord_get_recent_messages,
    discord_get_message,
    discord_send_message,
)
from .campaigns import (
    discord_create_campaign,
    discord_list_campaigns,
    discord_get_campaign,
    discord_update_campaign_status,
    discord_delete_campaign,
    discord_tally_optins,
    discord_list_optins,
    discord_build_reminder,
    discord_send_reminder,
    discord_run_due_reminders,
)


async def register_tools(mcp: FastMCP) -> None:
    """
    Register all tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server.
    """
    # Core Discord MCP Tools (Task 2.1, 2.2, 2.3)
    mcp.tool(
        name="discord_list_servers",
        description="List all servers (guilds) the bot is a member of",
    )(discord_list_servers)

    mcp.tool(
        name="discord_list_channels",
        description="List channels in a Discord server with optional type filtering",
    )(discord_list_channels)

    mcp.tool(
        name="discord_get_channel_info",
        description="Get detailed information about a Discord channel",
    )(discord_get_channel_info)

    mcp.tool(
        name="discord_bot_status",
        description="Get the current status and health information of the Discord bot",
    )(discord_bot_status)

    mcp.tool(
        name="discord_ping",
        description="Ping Discord to check connection health and optionally verify server access",
    )(discord_ping)

    mcp.tool(
        name="discord_get_recent_messages",
        description="Get recent messages from a Discord channel with pagination support",
    )(discord_get_recent_messages)

    mcp.tool(
        name="discord_get_message",
        description="Get a specific message by ID from a Discord channel",
    )(discord_get_message)

    mcp.tool(
        name="discord_send_message",
        description="Send a message to a Discord channel with optional reply support",
    )(discord_send_message)

    # Campaign Management Tools (Task 3.2)
    mcp.tool(
        name="discord_create_campaign",
        description="Create a new reaction opt-in reminder campaign",
    )(discord_create_campaign)

    mcp.tool(
        name="discord_list_campaigns",
        description="List all campaigns with optional status filtering",
    )(discord_list_campaigns)

    mcp.tool(
        name="discord_get_campaign",
        description="Get detailed information about a specific campaign",
    )(discord_get_campaign)

    mcp.tool(
        name="discord_update_campaign_status",
        description="Update campaign status (active, completed, cancelled)",
    )(discord_update_campaign_status)

    mcp.tool(
        name="discord_delete_campaign",
        description="Delete a campaign and all its associated opt-ins",
    )(discord_delete_campaign)

    mcp.tool(
        name="discord_tally_optins",
        description="Fetch reactions from Discord and store deduplicated opt-ins for a campaign",
    )(discord_tally_optins)

    mcp.tool(
        name="discord_list_optins",
        description="List opt-ins for a campaign with pagination support",
    )(discord_list_optins)

    mcp.tool(
        name="discord_build_reminder",
        description="Build reminder message with @mention chunking under 2000 characters",
    )(discord_build_reminder)

    mcp.tool(
        name="discord_send_reminder",
        description="Send reminder messages with rate limiting and batch processing",
    )(discord_send_reminder)

    mcp.tool(
        name="discord_run_due_reminders",
        description="Process scheduled campaigns that are due for reminders",
    )(discord_run_due_reminders)

    # Search & Discovery Tools (for finding servers/channels/roles by name)
    mcp.tool(name="server_info", description="Get detailed information about a Discord server")(get_server_info)
    mcp.tool(name="list_servers", description="List all servers the bot is in")(list_servers)
    mcp.tool(name="server_channels", description="Get all channels in a Discord server")(get_server_channels)
    mcp.tool(name="server_roles", description="Get all roles in a Discord server")(get_server_roles)
    mcp.tool(name="find_server", description="Find a server by name (supports partial matching)")(find_server_by_name)
    mcp.tool(name="find_channel", description="Find a channel by name in a server (supports partial matching)")(find_channel_by_name)
    mcp.tool(name="find_role", description="Find a role by name in a server (supports partial matching)")(find_role_by_name)
