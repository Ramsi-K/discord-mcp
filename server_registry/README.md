# Server Registry for MCP Discord

This module provides a registry for Discord servers, channels, and roles, allowing natural language references and context tracking.

## Overview

The Server Registry maintains information about Discord servers, channels, and roles that the bot has access to. It provides:

- Natural language references to servers, channels, and roles
- Context tracking for conversation history
- Permission checking for bot operations
- Persistent storage in SQLite

## Usage

### Environment Variables

- `MCP_DISCORD_DB_PATH`: Path to the SQLite database file (optional)

### Initialization

```python
# Server-side initialization
from server_registry.init import init_server_registry

# Initialize with Discord client
result = init_server_registry(discord_client=discord_bot)
if result["success"]:
    api = result["api"]
    print(f"Server registry initialized successfully using database at {result.get('db_path')}")
else:
    print(f"Failed to initialize server registry: {result.get('message')}")
```

### Client-side Usage

```python
# Client-side usage
import os
from mcp_client import MCPClient

# Set up environment variables
env = {}
db_path = os.getenv("MCP_DISCORD_DB_PATH")
if db_path:
    env["MCP_DISCORD_DB_PATH"] = db_path

# Create client with environment variables
async with MCPClient(
    command="uv",
    args=["run", "mcp_server/server.py"],
    env=env,
) as client:
    # Use the client
    await client.call_tool("discord_start_bot", {})
```

## API

The Server Registry API provides the following methods:

- `get_server(reference)`: Get a server by name, alias, or ID
- `get_channel(reference, server_reference)`: Get a channel by name, alias, or ID
- `get_role(reference, server_reference)`: Get a role by name, alias, or ID
- `update_registry(server_reference)`: Update the registry with current Discord data
- `check_permission(server_reference, permission)`: Check if the bot has a specific permission
- `track_context(user_id, entity_type, entity_id)`: Track an entity in the conversation context

## Tools

The following MCP tools are available:

- `registry_update`: Update the server registry with current Discord data
- `registry_find_entity`: Find an entity (server, channel, role) by name
- `registry_track_context`: Track an entity in the conversation context
- `server_info`: Get detailed information about a Discord server
- `list_servers`: List all servers the bot is in
- `server_channels`: Get all channels in a Discord server
- `server_roles`: Get all roles in a Discord server
- `find_server`: Find a server by name
- `find_channel`: Find a channel by name
- `find_role`: Find a role by name

## Database Schema

The database schema includes tables for:

- Servers
- Channels
- Roles
- Aliases
- Permissions
- Conversation context

See the `specs/schema` directory for the complete schema.