# MCP Discord

A Discord MCP (Model Context Protocol) server for AI-assisted Discord server management.

## Overview

This project implements a Discord MCP server that provides tools for AI assistants like Claude to interact with Discord servers. It includes:

- MCP server with Discord-specific tools
- Simple Discord bot for testing
- SQLite database for local storage

## Getting Started

### Prerequisites

- Python 3.10 or higher
- UV package manager (`pip install uv`)
- Discord bot token (create one at [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/mcp-discord.git
   cd mcp-discord
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   uv venv
   uv pip install -e .
   ```

3. Set up your Discord bot token:

   ```bash
   # On Windows
   set DISCORD_TOKEN=your_token_here

   # On Linux/macOS
   export DISCORD_TOKEN=your_token_here
   ```

4. (Optional) Set the database path:

   ```bash
   # On Windows
   set MCP_DISCORD_DB_PATH=C:\path\to\server_registry.db

   # On Linux/macOS
   export MCP_DISCORD_DB_PATH=/path/to/server_registry.db
   ```

### Running the MCP Server

Run the MCP server:

```bash
uv run mcp_server/server.py
```

### Running the Discord Bot

The Discord bot is started automatically by the MCP server when needed. You don't need to run it separately.

### Testing with the Client

Test the MCP server with the test client:

```bash
uv run client.py
```

## Project Structure

```
mcp-discord/
├── mcp_server/         # MCP server implementation
│   ├── __init__.py
│   ├── server.py       # Main FastMCP server
│   ├── server_registry_wrapper.py  # Wrapper for server registry
│   └── tools/          # Tool implementations
│       ├── __init__.py
│       └── server_registry_tools.py  # Server registry tools
├── server_registry/    # Server registry implementation
│   ├── __init__.py
│   ├── api.py          # API interfaces
│   ├── init.py         # Registry initialization
│   ├── models/         # Data models
│   ├── services/       # Business logic
│   └── db/             # Database access
├── bot/                # Discord bot implementation
│   ├── __init__.py
│   └── bot.py          # Simple Discord bot
├── client.py           # Test client
├── pyproject.toml      # Project configuration
└── README.md           # Project documentation
```

## Available Tools

The MCP server provides the following tools:

### Discord Communication

- `discord_send_message`: Send a message to a Discord channel
- `discord_get_channel_info`: Get information about a Discord channel
- `discord_list_servers`: List all servers the bot is in
- `discord_bot_status`: Get the current status of the Discord bot
- `discord_list_channels`: List all channels in a Discord server
- `discord_list_roles`: List all roles in a Discord server

### Server Registry

- `registry_update`: Update the server registry with current Discord data
- `registry_get_server`: Get a server by name, alias, or ID
- `registry_get_channel`: Get a channel by name, alias, or ID
- `registry_get_role`: Get a role by name, alias, or ID
- `registry_track_context`: Track an entity in the conversation context

## MCP Architecture

This project follows the Model Context Protocol (MCP) architecture:

1. **Client-side**: The LLM (e.g., Claude) handles natural language understanding and intent detection
2. **Server-side**: The MCP server provides tools that the client can call directly

The server includes an entity resolver that helps convert natural language references (like "general channel") to Discord IDs. This allows the client to use either direct IDs or human-readable names when calling tools.

## Connecting to Kiro IDE

To use this MCP server with Kiro IDE, add the following to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "discord-tools": {
      "command": "uv",
      "args": ["run", "path/to/mcp-discord/mcp_server/server.py"],
      "disabled": false
    }
  }
}
```

## Features

### Server Registry

The Server Registry maintains information about Discord servers, channels, and roles. It provides:

- Persistent storage of server data in SQLite
- Natural language references to servers, channels, and roles
- Context tracking for conversation history
- Permission checking for bot operations

See [Server Registry Documentation](server_registry/README.md) for more details.

## Development

### Adding New Tools

To add new tools, create a new file in the `mcp_server/tools/` directory and register your tools with the MCP server.

Example:

```python
async def register_my_tools(mcp: FastMCP):
    @mcp.tool(name="my_tool")
    async def my_tool(param: str, *, ctx: Context):
        return {"result": f"Processed {param}"}
```

Then import and register your tools in `mcp_server/server.py`.

### Running Tests

```bash
uv pip install -e ".[dev]"
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.