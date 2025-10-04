# Discord MCP Server - Version Roadmap

## ✅ v0.1.0 - Core Tools & Campaigns (Current Release)

**Status**: Ready for PyPI release
**Release Date**: TBD

### Implemented Features

#### Core Discord Tools
- ✅ Server and channel listing
- ✅ Channel information retrieval
- ✅ Bot status and health checks
- ✅ Message retrieval (recent and by ID)
- ✅ Message sending with reply support

#### Campaign & Reminder System
- ✅ Create reaction-based opt-in campaigns
- ✅ Tally opt-ins from message reactions
- ✅ Build reminder messages with @mention chunking
- ✅ Send reminders with rate limiting
- ✅ Scheduled reminder processing
- ✅ SQLite database with migrations

#### Infrastructure
- ✅ FastMCP server implementation
- ✅ Discord bot integration (discord.py)
- ✅ Configuration via environment variables
- ✅ DRY_RUN mode for testing
- ✅ Comprehensive error handling
- ✅ Legacy server registry (basic)

#### Developer Experience
- ✅ PyPI package with entry point (`discord-mcp`)
- ✅ Development script (`dev.py`)
- ✅ Test suite
- ✅ Documentation

### Known Limitations
- Server registry is legacy/basic
- No natural language processing
- No member analytics
- No thread/forum support
- No advanced role management
- No message styling system

---

## 🚧 v0.2.0 - Enhanced Discord Operations

**Status**: Planned
**Target**: Q2 2025

### Planned Features

#### Role Management
- `discord_create_role` - Create roles with permissions
- `discord_assign_role` - Assign roles to users
- `discord_remove_role` - Remove roles from users
- `discord_bulk_assign_role` - Bulk role assignment with filters

#### Thread & Forum Support
- `discord_create_thread` - Create threads in channels
- `discord_list_threads` - List active/archived threads
- `discord_add_to_thread` - Add users to threads
- `discord_archive_thread` - Archive/close threads

#### Enhanced Channel Operations
- `discord_create_channel` - Create new channels
- `discord_edit_channel` - Modify channel settings
- `discord_channel_stats` - Get channel statistics
- `discord_reaction_analytics` - Analyze reactions

#### Server Registry v2
- Refactor legacy registry
- Better entity resolution
- Persistent context tracking
- Permission-aware operations

### Database Changes
- Add role management tables
- Add thread tracking tables
- Remove unused legacy tables
- Add migration versioning

---

## 🔮 v0.3.0 - Member Intelligence

**Status**: Planned
**Target**: Q3 2025

### Planned Features

#### Member Management
- `discord_export_members` - Export member lists with filters
- `discord_member_analysis` - Analyze member activity
- `discord_new_members` - Track new member joins
- `discord_sync_members` - Sync member database
- `discord_store_member_info` - Store custom member data

#### Analytics & Insights
- Member activity patterns
- Interest detection from messages
- Engagement metrics
- Peak activity time analysis

#### Database Schema
- `members` table - User profiles
- `member_interests` table - Detected interests
- `member_messages` table - Message history (optional)
- `member_activity` table - Daily activity metrics

### Integration
- AI-powered interest detection
- Conversation history analysis
- Member matching/recommendations

---

## 🎯 v0.4.0 - Advanced Automation

**Status**: Future
**Target**: Q4 2025

### Planned Features

#### Context & Memory
- `discord_set_context_note` - Store conversation context
- `discord_get_context_summary` - Retrieve context
- `discord_store_conversation_memory` - Long-term memory

#### Event Management
- `discord_create_event` - Schedule server events
- `discord_notify_event` - Send event reminders
- `discord_event_attendance` - Track attendees

#### Automation Rules
- Scheduled messages
- Event-based triggers
- Conditional actions
- Recurring tasks

### Infrastructure
- Job scheduler integration
- Event-driven architecture
- Webhook support

---

## 🚀 v0.5.0 - Natural Language & Styling

**Status**: Future
**Target**: 2026

### Planned Features

#### Message Styling System
- Style templates for different message types
- Server-specific style definitions
- Style learning from examples
- Import/export styles
- Style application with preview

#### Natural Language Processing
- Intent detection for commands
- Entity extraction (servers, channels, roles)
- Context-aware resolution
- Ambiguity handling
- Conversational interface

#### Prompt System
- `summarize_channel` - AI channel summaries
- `analyze_member_interests` - AI interest analysis
- `generate_welcome_message` - Personalized welcomes
- `create_announcement` - Formatted announcements
- `create_event_description` - Event formatting

### AI Integration
- Anthropic API for prompts
- Custom prompt templates
- Multi-turn conversations

---

## 🌟 v1.0.0 - Semantic Search & Advanced Intelligence

**Status**: Future Vision
**Target**: 2026+

### Planned Features

#### Semantic Matching
- Vector database integration (Qdrant/Chroma)
- Embedding generation for messages
- Semantic member matching
- Interest-based recommendations
- Topic clustering

#### Advanced Analytics
- Server health reports
- Engagement scoring
- Predictive analytics
- Visualization tools

#### Onboarding Automation
- Guided onboarding flows
- Role recommendations
- Channel suggestions
- Follow-up automation
- Retention tracking

#### Enterprise Features
- Multi-server management
- Advanced permissions
- Audit logging
- Compliance tools
- API rate optimization

---

## Migration Path

### v0.1.0 → v0.2.0
- Legacy server registry tools will be deprecated
- Database migration will add new tables
- Configuration format remains compatible
- All v0.1.0 tools remain functional

### Breaking Changes Policy
- Major versions (1.0, 2.0): May have breaking changes
- Minor versions (0.x): Deprecations with warnings
- Patch versions (0.1.x): Bug fixes only

---

## Contributing to Roadmap

Priority is based on:
1. **User demand** - Most requested features
2. **Foundation first** - Build stable base before advanced features
3. **Discord API** - What Discord supports
4. **Maintainability** - Sustainable development pace

Feature requests: [GitHub Issues](https://github.com/yourusername/mcp-discord/issues)

---

## Version History

- **v0.1.0** (Current) - Core tools & campaigns
- _Previous versions not tracked (pre-release development)_
