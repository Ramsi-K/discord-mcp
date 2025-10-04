# Discord MCP Server Specification

This directory contains specifications for the Discord MCP (Model Context Protocol) server implementation.

## Overview

The Discord MCP server provides Discord integration for AI assistants through the Model Context Protocol (MCP). It allows AI assistants like Claude to interact with Discord servers through a set of well-defined tools.

## Current Status: v0.1.0 (Released)

The project is organized into **implemented** (current release) and **future** (planned) features.

See [ROADMAP.md](ROADMAP.md) for version planning (v0.1.0 → v1.0.0).

## Directory Structure

```text
📁 specs/
├── README.md                     # This file
├── ROADMAP.md                    # Version roadmap (v0.1.0 → v1.0.0)
├── requirements.md               # Original requirements (reference)
├── design.md                     # Original design doc (reference)
├── tasks.md                      # Original task list (reference)
├── server_registry.md            # Server registry design (reference)
├── implemented/                  # ✅ Currently implemented features
│   ├── core_tools.md            # Core Discord tools (v0.1.0)
│   ├── database.md              # SQLite schema documentation
│   ├── channel_tools.md         # Partial channel tools
│   └── role_tools.md            # Partial role tools (legacy)
└── future/                      # 🔮 Planned features
    ├── roadmap.md               # Phase 3-5 features
    ├── member_tools.md          # Member management (v0.3.0)
    ├── thread_tools.md          # Thread support (v0.2.0)
    ├── context_tools.md         # Context system (v0.4.0)
    ├── infra_tools.md           # Infrastructure tools (v0.2.0)
    ├── debug_tools.md           # Debug tools (v0.2.0)
    ├── message_styling.md       # Styling system (v0.5.0)
    └── prompts/                 # AI prompts (v0.5.0)
        └── prompt_tools.md
```

## What's Implemented (v0.1.0)

### Core Discord Tools
- Server and channel listing
- Channel information retrieval
- Message retrieval and sending
- Bot status and health checks

### Campaign & Reminder System
- Reaction-based opt-in campaigns
- Participant tracking
- Reminder scheduling and sending
- SQLite database backend

### Infrastructure
- FastMCP server
- Discord.py bot integration
- DRY_RUN mode for testing
- Configuration via environment variables

See [implemented/core_tools.md](implemented/core_tools.md) for full details.

## What's Planned

### v0.2.0 - Enhanced Operations
- Role management (create, assign, remove)
- Thread and forum support
- Enhanced channel operations
- Server registry refactor

### v0.3.0 - Member Intelligence
- Member analytics and tracking
- Activity pattern analysis
- Interest detection
- Engagement metrics

### v0.4.0 - Advanced Automation
- Context and memory system
- Event management
- Automation rules
- Scheduled tasks

### v0.5.0 - NLP & Styling
- Natural language command processing
- Message styling system
- AI-powered prompts
- Template management

### v1.0.0 - Semantic Intelligence
- Vector database integration
- Semantic member matching
- Advanced analytics
- Enterprise features

See [ROADMAP.md](ROADMAP.md) for complete version planning.

## Implementation Philosophy

The Discord MCP server is designed to be:

1. **Incremental**: Release early, add features over time
2. **Bot-Based**: Uses Discord bot for API access
3. **Permission-Aware**: Respects Discord's permission system
4. **Database-Backed**: SQLite for persistence (PostgreSQL in future)
5. **Testable**: DRY_RUN mode for testing without API calls
6. **Secure**: Rate limiting, input validation, error handling

## For Contributors

Current priorities:
1. Test v0.1.0 in production
2. Gather user feedback
3. Plan v0.2.0 features based on demand
4. Maintain backward compatibility

See [CONTRIBUTING.md](../CONTRIBUTING.md) if it exists, or file issues on GitHub.
