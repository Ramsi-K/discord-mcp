# Atomic Tools Analysis

## Overview

This document analyzes all current 26 tools and categorizes them into:

1. **Atomic Tools** - Keep as standalone, simple operations
2. **Workflow Operations** - Absorb into workflow actions
3. **Automation Tools** - Background processes (kept separate)

---

## Decision Criteria

A tool should remain **atomic** if it:

- ✅ Performs a **single, simple operation**
- ✅ Takes **exact IDs** (no search/fuzzy matching)
- ✅ Is a **building block** for workflows
- ✅ Needs **maximum performance** (no overhead)
- ✅ Is used **programmatically** in scripts/automation

A tool should become a **workflow action** if it:

- ❌ Requires **multi-step logic**
- ❌ Involves **search/discovery**
- ❌ Has **complex parameters**
- ❌ Is primarily **user-facing**
- ❌ Benefits from **intent parsing**

---

## Analysis by Category

### ✅ ATOMIC TOOLS (Keep as-is)

#### 1. `discord_send` (Simplified from `discord_send_message`)

**Reason**: Core building block, high performance needed

**Signature**:

```python
async def discord_send(
    channel_id: str,
    content: str,
    *,
    reply_to_id: Optional[str] = None,
    ctx: Context
) -> Dict[str, Any]
```

**Why atomic**:

- Simple: Just send text to exact channel ID
- Fast: No mention parsing, no validation overhead
- Building block: Workflows use this internally
- Programmatic: Scripts need direct send capability

**What it does NOT include** (moved to workflow):

- ❌ Mention parsing/validation
- ❌ Channel discovery by name
- ❌ Template rendering
- ❌ Intent understanding

---

#### 2. `discord_get` (New - consolidates get operations)

**Reason**: Direct entity retrieval by exact ID

**Signature**:

```python
async def discord_get(
    entity_type: Literal["channel", "message", "server", "role"],
    entity_id: str,
    *,
    ctx: Context
) -> Dict[str, Any]
```

**Why atomic**:

- Fast lookup: No search, just ID-based retrieval
- Building block: Workflows need entity details
- Simple: One operation per call

**Maps to current**:

- `discord_get_channel_info(channel_id)` → `discord_get("channel", id)`
- `discord_get_message(channel_id, message_id)` → `discord_get("message", id)`
- New: `discord_get("server", id)` for server details
- New: `discord_get("role", id)` for role details

---

#### 3. `discord_list` (New - simple listing)

**Reason**: Basic enumeration without filtering logic

**Signature**:

```python
async def discord_list(
    entity_type: Literal["servers", "channels", "roles"],
    *,
    guild_id: Optional[str] = None,
    ctx: Context
) -> Dict[str, Any]
```

**Why atomic**:

- Simple: Just list IDs and names
- Fast: No complex filtering
- Building block: Workflows iterate over results

**Maps to current**:

- `discord_list_servers()` → `discord_list("servers")`
- `discord_list_channels(guild_id)` → `discord_list("channels", guild_id=id)`
- New: `discord_list("roles", guild_id=id)`

**What it does NOT include**:

- ❌ Type filtering (move to workflow)
- ❌ Search/matching (move to discovery workflow)
- ❌ Detailed info (use `discord_get` for that)

---

#### 4. `discord_get_recent_messages` (Keep as-is)

**Reason**: Simple pagination operation, commonly used

**Signature**:

```python
async def discord_get_recent_messages(
    channel_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    after: Optional[str] = None,
    *,
    ctx: Context
) -> Dict[str, Any]
```

**Why atomic**:

- Simple: Direct Discord API call
- Commonly used: Many workflows need message history
- Performance: Bulk message retrieval is time-sensitive

---

### 🔄 WORKFLOW OPERATIONS (Absorb into workflows)

#### Discovery Operations → `discord_discovery` workflow

**Absorb these**:

- `find_server_by_name()` → `discord_discovery(entity_type="server", query=name)`
- `find_channel_by_name()` → `discord_discovery(entity_type="channel", query=name, guild_id=...)`
- `find_role_by_name()` → `discord_discovery(entity_type="role", query=name, guild_id=...)`
- `get_server_info()` → `discord_discovery(entity_type="server", query=id, detailed=True)`
- `get_server_channels()` → `discord_discovery(entity_type="channel", query="*", guild_id=...)`
- `get_server_roles()` → `discord_discovery(entity_type="role", query="*", guild_id=...)`
- `list_servers()` → `discord_discovery(entity_type="server", query="*")`

**Why workflow**:

- Complex: Fuzzy matching, relevance scoring
- Multi-step: Search → rank → fetch details
- User-facing: Benefits from natural language
- Can use intent parsing

---

#### Message Operations → `discord_message` workflow

**Absorb these**:

- `discord_send_message()` → `discord_message(action="send", ...)`
- `discord_get_message()` → `discord_message(action="get", ...)`

**Why workflow**:

- Complex mention parsing
- Template support
- Safety validation
- Intent understanding

**Keep atomic**: `discord_send()` for simple programmatic sends

---

#### Diagnostics Operations → `discord_diagnostics` workflow

**Absorb these**:

- `discord_bot_status()` → `discord_diagnostics(action="status")`
- `discord_ping()` → `discord_diagnostics(action="ping", ...)`

**Why workflow**:

- Multi-check health reports
- Permission validation
- Config verification
- Comprehensive reporting

---

#### Campaign Operations → `discord_campaign` workflow

**Absorb these** (already workflow-ready):

- `discord_create_campaign()` → `discord_campaign(action="create", ...)`
- `discord_list_campaigns()` → `discord_campaign(action="list", ...)`
- `discord_get_campaign()` → `discord_campaign(action="get", ...)`
- `discord_update_campaign_status()` → `discord_campaign(action="update_status", ...)`
- `discord_delete_campaign()` → `discord_campaign(action="delete", ...)`
- `discord_tally_optins()` → `discord_campaign(action="tally", ...)`
- `discord_list_optins()` → `discord_campaign(action="list_optins", ...)`
- `discord_build_reminder()` → `discord_campaign(action="preview", ...)`
- `discord_send_reminder()` → `discord_campaign(action="send", ...)`

**Why workflow**:

- Multi-step operations (tally → build → send)
- Template rendering
- Rate limiting coordination
- Safety checks (dry_run)

---

### ⚙️ AUTOMATION TOOLS (Keep separate)

#### `discord_run_due_reminders`

**Reason**: Background automation, not user-triggered

**Keep as standalone tool** because:

- Run by cron/scheduler, not by users
- Processes multiple campaigns autonomously
- Needs to be independently executable
- Not part of any workflow

**Usage**:

```bash
# Cron job
*/5 * * * * uv run python -m discord_mcp --run-due-reminders
```

---

## Final Tool Count

### Before (26 tools)

**Core Tools (8)**:

- discord_list_servers
- discord_list_channels
- discord_get_channel_info
- discord_bot_status
- discord_ping
- discord_get_recent_messages
- discord_get_message
- discord_send_message

**Campaign Tools (10)**:

- discord_create_campaign
- discord_list_campaigns
- discord_get_campaign
- discord_update_campaign_status
- discord_delete_campaign
- discord_tally_optins
- discord_list_optins
- discord_build_reminder
- discord_send_reminder
- discord_run_due_reminders

**Search Tools (7)**:

- server_info
- list_servers
- server_channels
- server_roles
- find_server
- find_channel
- find_role

**Registry Tools (1)**:

- (various registry operations)

---

### After (8 tools total)

**Workflow Tools (4)**:

1. `discord_discovery` - Entity search and exploration
2. `discord_message` - Message operations with templates
3. `discord_campaign` - Campaign lifecycle management
4. `discord_diagnostics` - Health checks and monitoring

**Atomic Tools (3)**: 5. `discord_send` - Simple text send (no mention parsing) 6. `discord_get` - Get entity by exact ID 7. `discord_list` - List entities (simple enumeration)

**Automation Tools (1)**: 8. `discord_run_due_reminders` - Background campaign processor

---

## Comparison Table

| Current Tool                  | New Tool                               | Type       | Reason                      |
| ----------------------------- | -------------------------------------- | ---------- | --------------------------- |
| `discord_send_message`        | `discord_message(action="send")`       | Workflow   | Complex mentions, templates |
|                               | `discord_send(channel_id, content)`    | Atomic     | Simple programmatic send    |
| `discord_get_message`         | `discord_message(action="get")`        | Workflow   | Context-aware retrieval     |
|                               | `discord_get("message", id)`           | Atomic     | Direct ID lookup            |
| `discord_get_channel_info`    | `discord_discovery(...)`               | Workflow   | With search capability      |
|                               | `discord_get("channel", id)`           | Atomic     | Direct ID lookup            |
| `discord_list_servers`        | `discord_discovery(...)`               | Workflow   | With filtering              |
|                               | `discord_list("servers")`              | Atomic     | Simple enumeration          |
| `discord_list_channels`       | `discord_discovery(...)`               | Workflow   | With type filtering         |
|                               | `discord_list("channels", guild_id)`   | Atomic     | Simple enumeration          |
| `find_server_by_name`         | `discord_discovery(...)`               | Workflow   | Fuzzy search                |
| `find_channel_by_name`        | `discord_discovery(...)`               | Workflow   | Fuzzy search                |
| `find_role_by_name`           | `discord_discovery(...)`               | Workflow   | Fuzzy search                |
| `discord_bot_status`          | `discord_diagnostics(action="status")` | Workflow   | Comprehensive check         |
| `discord_ping`                | `discord_diagnostics(action="ping")`   | Workflow   | With verification           |
| `discord_get_recent_messages` | `discord_get_recent_messages()`        | Atomic     | Keep as-is                  |
| All campaign tools            | `discord_campaign(action=...)`         | Workflow   | Multi-step operations       |
| `discord_run_due_reminders`   | `discord_run_due_reminders()`          | Automation | Keep as-is                  |

---

## Migration Strategy

### Phase 1: Add Atomic Tools (Non-breaking)

```python
# Add new atomic tools alongside existing
@mcp.tool("discord_send")
async def discord_send(channel_id: str, content: str, *, ctx: Context):
    """Simple message send - no mention parsing, no templates."""
    # Direct send implementation
    pass

@mcp.tool("discord_get")
async def discord_get(entity_type: str, entity_id: str, *, ctx: Context):
    """Get entity by exact ID."""
    # Direct lookup implementation
    pass

@mcp.tool("discord_list")
async def discord_list(entity_type: str, *, guild_id: Optional[str] = None, ctx: Context):
    """List entities - simple enumeration."""
    # Simple listing implementation
    pass
```

### Phase 2: Add Workflow Tools (Non-breaking)

```python
# Add workflows that internally use atomic tools
@mcp.tool("discord_discovery")
async def discord_discovery_workflow(...):
    # Uses discord_get, discord_list internally
    pass

@mcp.tool("discord_message")
async def discord_message_workflow(...):
    # Uses discord_send internally
    pass
```

### Phase 3: Deprecate Old Tools (v0.2.0)

```python
# Mark old tools as deprecated
@mcp.tool("discord_send_message")
async def discord_send_message(...):
    """
    ⚠️ DEPRECATED: Use discord_message(action="send") for full features
    or discord_send() for simple sends.
    """
    # Keep functional for 1-2 versions
    pass
```

### Phase 4: Remove Deprecated Tools (v0.3.0)

- Remove old tool registrations
- Keep internal functions (workflows still use them)
- Update all documentation

---

## Usage Examples

### Atomic Tool Usage (Scripts/Automation)

```python
# Fast, simple send - no overhead
discord_send(
    channel_id="123456",
    content="Bot restarted successfully"
)

# Quick ID lookup
channel = discord_get("channel", "123456")
print(f"Channel name: {channel['name']}")

# List all servers
servers = discord_list("servers")
for server in servers["items"]:
    print(server["name"])
```

### Workflow Usage (User-facing)

```python
# Intelligent discovery
channel = discord_discovery(
    intent="find announcements channel in MyServer"
)

# Rich message sending
discord_message(
    action="send",
    intent="announce tournament to all participants",
    template="event_announcement"
)

# Campaign management
discord_campaign(
    action="create_and_run",
    intent="tournament reminder for tomorrow at 6pm"
)
```

---

## Benefits of This Split

### For Power Users

✅ Atomic tools provide maximum performance
✅ Direct control, no "magic" behavior
✅ Scriptable and predictable

### For Regular Users

✅ Workflows handle complexity
✅ Natural language understanding
✅ Safety and validation built-in

### For Maintainers

✅ Clear separation of concerns
✅ Easier to test (atomic = pure functions)
✅ Workflows can evolve without breaking atomics

---

## Recommendations

1. **Implement atomic tools first** - They're simpler and used by workflows
2. **Test atomic tools thoroughly** - They're the foundation
3. **Build workflows on top of atomics** - Reuse, don't duplicate
4. **Keep `discord_run_due_reminders` separate** - It's automation, not a workflow
5. **Document both usage patterns** - Power users vs. regular users
6. **Provide migration guide** - Help users transition from old tools

---

## Questions for Review

1. ✅ Do these 3 atomic tools cover the core building blocks needed?
2. ✅ Should `discord_get_recent_messages` remain atomic or become `discord_message(action="get_recent")`?
   - **Recommendation**: Keep atomic - it's simple pagination
3. ✅ Should we add `discord_create` for creating channels/roles?
   - **Recommendation**: Future v0.2.0, keep focused on messaging for now
4. ✅ Do we need a `discord_delete` atomic tool?
   - **Recommendation**: Future v0.2.0, requires careful permission handling

---

## Summary

**Keep simple, keep fast**: Atomic tools are the high-performance foundation.

**Make it smart, make it safe**: Workflows add intelligence and safety.

**Keep it separate**: Automation tools run independently.

This gives you the best of both worlds: powerful building blocks for developers and intelligent workflows for users.
