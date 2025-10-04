# PostgreSQL Database Schemas (Future)

**Status**: ❌ NOT IMPLEMENTED - Future version (v0.3.0+)

These SQL files define PostgreSQL database schemas for **future versions** of the Discord MCP server.

## Current Implementation (v0.1.0)

The current version uses **SQLite** with a much simpler schema:
- `campaigns` table
- `opt_ins` table
- `reminder_logs` table

See [../implemented/database.md](../implemented/database.md) for actual implementation.

## Planned PostgreSQL Migration (v0.3.0+)

These schemas are for when we migrate to PostgreSQL and add advanced features:

### Files

- **servers.sql** - Server registry and bot permissions (v0.2.0)
- **channels.sql** - Channel information (v0.2.0)
- **roles.sql** - Role information (v0.2.0)
- **members.sql** - Member tracking and analytics (v0.3.0)
- **activity.sql** - Member activity metrics (v0.3.0)
- **logging.sql** - Tool usage and audit logs (v0.2.0)
- **aliases.sql** - Natural language entity aliases (v0.2.0)
- **styles.sql** - Message styling system (v0.5.0)

### Migration Path

**v0.1.0 → v0.2.0**:
- Continue using SQLite
- Add `servers`, `channels`, `roles` tables to existing SQLite database
- Keep campaigns tables

**v0.3.0**:
- Migrate to PostgreSQL for better performance
- Add member tracking tables
- Add activity analytics
- Keep backward compatibility for configurations

**v0.5.0**:
- Add styles tables for message styling system
- Full PostgreSQL feature set

### Why PostgreSQL Later?

Current SQLite is sufficient for v0.1.0 because:
- ✅ Simple campaign system
- ✅ Low data volume
- ✅ Single-user (bot) access
- ✅ Easy deployment (no separate DB server)

PostgreSQL will be needed for:
- 📊 Complex analytics queries
- 🔄 Concurrent access at scale
- 📈 Large member datasets
- 🔍 Full-text search
- 🎯 Advanced indexing

## Do NOT Use These Files

These schemas are **reference only**. The actual v0.1.0 database schema is defined in:

[../../implemented/database.md](../../implemented/database.md)

Using these PostgreSQL files now will cause errors because:
1. Uses PostgreSQL syntax (`SERIAL`, `JSONB`, etc.)
2. References tables that don't exist
3. Not compatible with current SQLite implementation
