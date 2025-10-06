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
- **Campaign tools**: [src/discord_mcp/tools/campaigns.py](src/discord_mcp/tools/campaigns.py) - Full campaign CRUD + reaction opt-ins + reminder building/sending with @mention chunking
- **Search tools**: [src/discord_mcp/tools/search_tools.py](src/discord_mcp/tools/search_tools.py) - Server/channel/role search by name (partial matching)
- **Registration**: [src/discord_mcp/tools/register_tools.py](src/discord_mcp/tools/register_tools.py) - Registers all tools with FastMCP

#### Campaign Tools (Complete CRUD)

Campaign management provides full lifecycle control:
- **Create**: `discord_create_campaign` - Set up reaction-based opt-in campaigns
- **Read**: `discord_list_campaigns`, `discord_get_campaign` - View all or specific campaigns
- **Update**: `discord_update_campaign_status` - Change status (active/completed/cancelled)
- **Delete**: `discord_delete_campaign` - Remove campaigns and associated opt-ins
- **Operations**: `discord_tally_optins`, `discord_list_optins`, `discord_build_reminder`, `discord_send_reminder`, `discord_run_due_reminders`

#### Database Layer

- **Models**: [src/discord_mcp/database/models.py](src/discord_mcp/database/models.py) - Campaign, OptIn, ReminderLog dataclasses
- **Migrations**: [src/discord_mcp/database/migrations.py](src/discord_mcp/database/migrations.py) - SQLite schema migrations
- **Repositories**: [src/discord_mcp/database/repositories.py](src/discord_mcp/database/repositories.py) - Campaign/opt-in CRUD operations

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
- Campaign system tables:
  - `campaigns` - Campaign metadata (channel, message, emoji, remind_at, status)
  - `optins` - User opt-ins per campaign (unique constraint on campaign_id + user_id)
  - `reminders_log` - Reminder send history and outcomes

## Testing Strategy

Tests use real Discord API calls when `DISCORD_TOKEN` is available, fall back to mocks otherwise. Campaign tests verify idempotency and DRY_RUN paths.
