"""
Tools for Discord MCP server.
"""

from mcp.server.fastmcp import FastMCP
from .server_registry_tools import (
    get_server_info,
    list_servers,
    get_server_channels,
    get_server_roles,
    find_server_by_name,
    find_channel_by_name,
    find_role_by_name,
)


async def register_tools(mcp: FastMCP) -> None:
    """
    Register all tools with the MCP server.

    Args:
        mcp (FastMCP): The MCP server.
    """
    # Server Registry Tools
    mcp.tool(name="server_info")(get_server_info)
    mcp.tool(name="list_servers")(list_servers)
    mcp.tool(name="server_channels")(get_server_channels)
    mcp.tool(name="server_roles")(get_server_roles)
    mcp.tool(name="find_server")(find_server_by_name)
    mcp.tool(name="find_channel")(find_channel_by_name)
    mcp.tool(name="find_role")(find_role_by_name)