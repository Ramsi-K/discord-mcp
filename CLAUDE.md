# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discord MCP Server - A Model Context Protocol (MCP) server providing Discord integration for AI assistants. Enables Discord bot operations through FastMCP tools including messaging, server/channel/role management, and reaction-based campaign reminders.

## Package Manager

**Use `uv` for all Python operations.** This project uses `uv` as the package manager and build tool.

## Common Commands

### Development

- **Run MCP inspector**: `python dev.py inspector`
- **Run server directly**: `python dev.py server`
- **Run development server**: `uv run python -m discord_mcp.server`

### Testing

- **Run all tests**: `uv run pytest`
- **Run specific test**: `uv run pytest tests/test_core_tools.py`
- **Run with verbose output**: `uv run pytest -v`

### Code Quality

- **Format code**: `uv run black src/ tests/`
- **Sort imports**: `uv run isort src/ tests/`

### Build & Package

- **Build package**: `uv build`
- **Install in editable mode**: `uv pip install -e ".[dev]"`

## Architecture

### Entry Point & Server

- **Entry point**: [src/discord_mcp/server.py](src/discord_mcp/server.py) - Main MCP server using FastMCP, manages Discord bot lifecycle
- **Command**: `discord-mcp` (defined in pyproject.toml)
- **Bot management**: Global `discord_bot` instance managed via `ensure_bot_running()`, runs in background task

### Core Components

#### Discord Client

- **Location**: [src/discord_mcp/discord_client/bot.py](src/discord_mcp/discord_client/bot.py)
- `DiscordMCPBot` class extends discord.py Client
- Handles Discord API connection and events

#### Tools (MCP Tool Implementations)

- **Core tools**: [src/discord_mcp/tools/core.py](src/discord_mcp/tools/core.py) - Server/channel listing, messaging, bot status
- **Campaign tools**: [src/discord_mcp/tools/campaigns.py](src/discord_mcp/tools/campaigns.py) - Reaction opt-in campaigns, reminders with @mention chunking
- **Registry tools**: [src/discord_mcp/tools/server_registry_tools.py](src/discord_mcp/tools/server_registry_tools.py) - Legacy server registry lookup
- **Registration**: [src/discord_mcp/tools/register_tools.py](src/discord_mcp/tools/register_tools.py) - Registers all tools with FastMCP

#### Database Layer

- **Models**: [src/discord_mcp/database/models.py](src/discord_mcp/database/models.py) - Campaign, OptIn, ReminderLog dataclasses
- **Migrations**: [src/discord_mcp/database/migrations.py](src/discord_mcp/database/migrations.py) - SQLite schema migrations
- **Repositories**: [src/discord_mcp/database/repositories.py](src/discord_mcp/database/repositories.py) - Campaign/opt-in CRUD operations

#### Server Registry (Legacy)

- **Location**: [src/discord_mcp/server_registry/](src/discord_mcp/server_registry/)
- Maintains local SQLite registry of servers, channels, roles
- Natural language entity resolution with aliases
- See [src/discord_mcp/server_registry/README.md](src/discord_mcp/server_registry/README.md)

### Configuration

- **Config class**: [src/discord_mcp/config.py](src/discord_mcp/config.py)
- **Environment variables**:
  - `DISCORD_TOKEN` (required) - Discord bot token
  - `MCP_DISCORD_DB_PATH` (optional) - SQLite database path, default: `discord_mcp.db`
  - `GUILD_ALLOWLIST` (optional) - Comma-separated guild IDs
  - `LOG_LEVEL` (optional) - Default: INFO
  - `DRY_RUN` (optional) - Set to "true" for mock Discord API calls

### Tool Pattern

Tools use `@require_discord_bot` decorator to ensure bot is connected before execution. All tools support DRY_RUN mode for testing without Discord API calls.

### Database Design

- Single SQLite database at `MCP_DISCORD_DB_PATH`
- Campaign system: campaigns → opt_ins (many-to-many via reactions) → reminder_logs
- Server registry: servers → channels/roles with aliases and context tracking

## Testing Strategy

Tests use real Discord API calls when `DISCORD_TOKEN` is available, fall back to mocks otherwise. Campaign tests verify idempotency and DRY_RUN paths.
