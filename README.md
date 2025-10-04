# Discord MCP Server

> ⚠️ **ALPHA SOFTWARE** - This project is in early alpha development. Features may be incomplete or buggy. Use at your own risk.

A Model Context Protocol (MCP) server that provides Discord integration tools for AI assistants like Claude.

**Current Version**: 0.0.1-alpha1 (Local Development)

## Project Status

- 🔬 **Phase: Local Development** - Testing with MCP Inspector
- 📋 **Next: Alpha Release** - Publish to PyPI for Claude Desktop testing
- 🎯 **Future: Beta & v1.0** - Feature-complete and stable

See [specs/ROADMAP.md](specs/ROADMAP.md) for version planning.

## Overview

This MCP server enables AI assistants to interact with Discord servers through tools for:

- ✅ **Core Operations**: List servers, channels, send messages
- ✅ **Campaign System**: Reaction-based opt-in campaigns with reminders
- 🚧 **Future Features**: Role management, member analytics, thread support, and more

## Development Setup

### Prerequisites

1. **Python 3.10+** with `uv` package manager
2. **Discord Bot**: Create at [Discord Developer Portal](https://discord.com/developers/applications)
3. **Node.js** (for MCP Inspector)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-discord.git
cd mcp-discord

# Install with uv
uv pip install -e ".[dev]"
```

### Configuration

Create a `.env` file:

```bash
DISCORD_TOKEN=your_discord_bot_token_here
MCP_DISCORD_DB_PATH=discord_mcp.db
LOG_LEVEL=INFO
DRY_RUN=false  # Set to true for testing without Discord API
```

## Testing with MCP Inspector

The MCP Inspector lets you test tools locally before deploying.

### 1. Start the MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m discord_mcp
```

This will:
- Start your Discord MCP server
- Launch the MCP Inspector web UI
- Open in your browser (usually http://localhost:5173)

### 2. Test Available Tools

In the inspector, you can test:
- `discord_list_servers` - See all servers your bot is in
- `discord_list_channels` - List channels in a server
- `discord_send_message` - Send test messages
- `discord_create_campaign` - Create reaction campaigns
- And more...

### 3. Alternative: Direct Module Run

```bash
# Run server directly (for stdio transport)
python -m discord_mcp

# Run with development script
python dev.py server

# Run with inspector mode
python dev.py inspector
```

## Claude Desktop Configuration (Alpha/Beta Only)

> ⚠️ **Not ready yet** - First test locally with inspector, then we'll publish to PyPI

Once published to PyPI, you can configure Claude Desktop:

**Windows**: Edit `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "discord": {
      "command": "python",
      "args": ["-m", "discord_mcp"],
      "env": {
        "DISCORD_TOKEN": "your_token_here",
        "MCP_DISCORD_DB_PATH": "C:\\path\\to\\discord_mcp.db",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Restart Claude Desktop to load the server.

## Available Tools (v0.0.1-alpha)

### Core Discord Tools
- `discord_list_servers` - List all Discord servers
- `discord_list_channels` - List channels with type filtering
- `discord_get_channel_info` - Get detailed channel information
- `discord_bot_status` - Check bot connection status
- `discord_get_recent_messages` - Retrieve recent messages
- `discord_get_message` - Get specific message by ID
- `discord_send_message` - Send messages with reply support

### Campaign & Reminder Tools
- `discord_create_campaign` - Create reaction opt-in campaigns
- `discord_tally_optins` - Track campaign participants
- `discord_list_optins` - List opt-ins with pagination
- `discord_build_reminder` - Build reminder messages
- `discord_send_reminder` - Send reminders with rate limiting
- `discord_run_due_reminders` - Process scheduled reminders

See [specs/implemented/core_tools.md](specs/implemented/core_tools.md) for detailed documentation.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `MCP_DISCORD_DB_PATH` | No | `discord_mcp.db` | SQLite database path |
| `GUILD_ALLOWLIST` | No | - | Comma-separated server IDs to restrict access |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `DRY_RUN` | No | `false` | Test mode without Discord API calls |

## Development Commands

```bash
# Run tests
uv run pytest

# Format code
uv run black src/ tests/
uv run isort src/ tests/

# Build package
uv build

# Run MCP inspector
npx @modelcontextprotocol/inspector python -m discord_mcp
```

## Project Structure

```
discord-mcp/
├── src/discord_mcp/          # Main package
│   ├── server.py             # MCP server entry point
│   ├── __main__.py           # Module runner (python -m discord_mcp)
│   ├── config.py             # Configuration
│   ├── discord_client/       # Discord bot implementation
│   ├── database/             # SQLite models & repos
│   ├── tools/                # MCP tool implementations
│   └── server_registry/      # Legacy entity registry
├── tests/                    # Test suite
├── specs/                    # Documentation
│   ├── implemented/          # Current features
│   ├── future/               # Planned features
│   └── ROADMAP.md            # Version roadmap
├── pyproject.toml            # Package configuration
└── README.md                 # This file
```

## Known Issues & Limitations

- ⚠️ **Alpha quality** - Bugs expected
- ⚠️ **Limited features** - Only basic tools implemented
- ⚠️ **No error recovery** - Some edge cases not handled
- ⚠️ **Database migrations** - Manual schema updates may be needed

See [GitHub Issues](https://github.com/yourusername/mcp-discord/issues) for known bugs.

## Contributing

This is an alpha project - contributions welcome but expect things to change!

1. Test locally with MCP Inspector first
2. Check [specs/ROADMAP.md](specs/ROADMAP.md) for planned features
3. Open an issue to discuss changes
4. Submit PR against `develop` branch

## Release Stages

- **Now (Local)**: Testing with MCP Inspector only
- **Alpha (0.0.x)**: Published to PyPI, testing with Claude Desktop
- **Beta (0.1.x)**: Feature-complete, polishing bugs
- **Release (1.0.0)**: Stable, production-ready

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- 📖 **Documentation**: [specs/](specs/) directory
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/mcp-discord/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-discord/discussions)

---

**Remember**: This is alpha software. Always test in a non-production Discord server first!
