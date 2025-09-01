🚧 Work in Progress 

# Discord MCP Server

A Model Context Protocol (MCP) server that provides Discord integration tools for AI assistants like Claude.

## Overview

This MCP server enables AI assistants to interact with Discord servers through a comprehensive set of tools for:

- Sending messages to Discord channels
- Retrieving server, channel, and role information
- Managing Discord bot operations
- Maintaining a local registry of Discord entities with natural language aliases

## Installation

### From PyPI (Recommended)

```bash
pip install discord-mcp
```

### From Source

```bash
git clone https://github.com/yourusername/mcp-discord.git
cd mcp-discord
pip install -e .
```

## Configuration

### Prerequisites

1. **Discord Bot Token**: Create a Discord application and bot at the [Discord Developer Portal](https://discord.com/developers/applications)
2. **Bot Permissions**: Ensure your bot has the necessary permissions in your Discord server:
   - Read Messages
   - Send Messages
   - View Channels
   - Read Message History

### MCP Configuration

Add the Discord MCP server to your MCP client configuration. The exact method depends on your MCP client:

#### For Kiro IDE

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "discord": {
      "command": "discord-mcp",
      "env": {
        "DISCORD_TOKEN": "your_discord_bot_token_here",
        "MCP_DISCORD_DB_PATH": "/path/to/discord_registry.db",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": [
        "discord_send_message",
        "discord_get_channel_info",
        "discord_list_servers",
        "discord_list_channels",
        "discord_bot_status"
      ]
    }
  }
}
```

#### For Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "discord": {
      "command": "discord-mcp",
      "env": {
        "DISCORD_TOKEN": "your_discord_bot_token_here",
        "MCP_DISCORD_DB_PATH": "/path/to/discord_registry.db",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Using uvx (Alternative)

If you prefer to use uvx instead of installing globally:

```json
{
  "mcpServers": {
    "discord": {
      "command": "uvx",
      "args": ["discord-mcp"],
      "env": {
        "DISCORD_TOKEN": "your_discord_bot_token_here",
        "MCP_DISCORD_DB_PATH": "/path/to/discord_registry.db",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false
    }
  }
}
```

### Environment Variables

The following environment variables can be configured in the MCP server environment:

- **`DISCORD_TOKEN`** (required): Your Discord bot token
- **`MCP_DISCORD_DB_PATH`** (optional): Path to SQLite database file. Default: `discord_mcp.db`
- **`GUILD_ALLOWLIST`** (optional): Comma-separated list of Discord server IDs to restrict bot access
- **`LOG_LEVEL`** (optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: `INFO`
- **`DRY_RUN`** (optional): Set to "true" to enable dry-run mode (no actual Discord API calls). Default: `false`

#### Complete Configuration Example

See [`example-mcp-config.json`](example-mcp-config.json) for a complete configuration template.

```json
{
  "mcpServers": {
    "discord": {
      "command": "discord-mcp",
      "env": {
        "DISCORD_TOKEN": "your_discord_bot_token_here",
        "MCP_DISCORD_DB_PATH": "/path/to/discord_registry.db",
        "GUILD_ALLOWLIST": "123456789012345678,987654321098765432",
        "LOG_LEVEL": "INFO",
        "DRY_RUN": "false"
      },
      "disabled": false,
      "autoApprove": [
        "discord_send_message",
        "discord_get_channel_info",
        "discord_list_servers",
        "discord_list_channels",
        "discord_list_roles",
        "discord_bot_status",
        "registry_update",
        "registry_get_server",
        "registry_get_channel",
        "registry_get_role"
      ]
    }
  }
}
```

## Usage

Once configured, the Discord MCP server will automatically start when your MCP client connects. The server provides tools that AI assistants can use to interact with Discord.

### Example Interactions

- "Send a message to the general channel saying hello"
- "List all channels in the server"
- "Get information about the moderator role"
- "Show me the status of the Discord bot"

### Dry Run Mode

For testing purposes, you can enable dry-run mode by setting `DRY_RUN=true` in the environment variables. In this mode, the server will simulate Discord operations without making actual API calls.

## Available Tools

The MCP server provides the following tools for AI assistants:

### Discord Communication

- **`discord_send_message`**: Send a message to a Discord channel
- **`discord_get_channel_info`**: Get detailed information about a Discord channel
- **`discord_bot_status`**: Get the current status and connection info of the Discord bot

### Server Management

- **`discord_list_servers`**: List all Discord servers the bot has access to
- **`discord_list_channels`**: List all channels in a specific Discord server
- **`discord_list_roles`**: List all roles in a specific Discord server

### Server Registry

- **`registry_update`**: Update the local registry with current Discord server data
- **`registry_get_server`**: Get server information by name, alias, or ID
- **`registry_get_channel`**: Get channel information by name, alias, or ID
- **`registry_get_role`**: Get role information by name, alias, or ID
- **`registry_track_context`**: Track entities in conversation context for better natural language understanding

## Features

### Natural Language Entity Resolution

The server includes intelligent entity resolution that allows AI assistants to use natural language references:

- "general channel" → resolves to actual channel ID
- "admin role" → resolves to actual role ID
- "main server" → resolves to actual server ID

### Local Server Registry

Maintains a local SQLite database with:

- Server, channel, and role information
- Natural language aliases for easy reference
- Conversation context tracking
- Automatic updates from Discord API

### Robust Error Handling

- Graceful handling of Discord API rate limits
- Automatic reconnection on connection loss
- Detailed error messages for troubleshooting
- Dry-run mode for testing without API calls

## Troubleshooting

### Common Issues

1. **Bot not connecting**: Verify your Discord token is correct and the bot is added to your server
2. **Permission errors**: Ensure the bot has necessary permissions in your Discord server
3. **Database errors**: Check that the bot has write permissions for the database file location
4. **Rate limiting**: The server automatically handles Discord rate limits, but very high usage may cause delays

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your MCP configuration:

```json
{
  "env": {
    "DISCORD_TOKEN": "your_token",
    "LOG_LEVEL": "DEBUG"
  }
}
```

### Testing Configuration

Use dry-run mode to test your configuration without making actual Discord API calls:

```json
{
  "env": {
    "DISCORD_TOKEN": "your_token",
    "DRY_RUN": "true"
  }
}
```

### Security Considerations

- **Token Security**: Never commit your Discord bot token to version control
- **Database Location**: Choose a secure location for your database file with appropriate permissions
- **Guild Allowlist**: Use `GUILD_ALLOWLIST` to restrict which Discord servers the bot can access
- **Permissions**: Grant your Discord bot only the minimum required permissions

````

## Development

### Local Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/mcp-discord.git
   cd mcp-discord
````

2. Install in development mode:

   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

### Project Structure

```
src/discord_mcp/
├── __init__.py
├── config.py                    # Configuration management
├── server.py                    # Main MCP server
├── server_registry_wrapper.py   # Registry wrapper
├── discord_client/              # Discord bot implementation
├── server_registry/             # Local data registry
├── tools/                       # MCP tool implementations
├── core/                        # Core utilities
└── database/                    # Database utilities
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
