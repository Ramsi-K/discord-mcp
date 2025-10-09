# Discovery Flow Documentation

## Overview

The discovery workflow enables finding and exploring Discord entities (servers, channels, roles, members) through natural language queries or structured searches. It consolidates multiple search operations into a single, intelligent workflow.

## Use Case

**Scenario**: You want to send a message to the "general" channel in a server called "Community Hub", but you don't know the channel ID. The discovery workflow helps you find it in one call.

## Discovery Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    DISCOVERY LIFECYCLE                       │
└─────────────────────────────────────────────────────────────┘

1. PARSE         → Understand what you're looking for
2. RESOLVE       → Find parent entities (e.g., server first)
3. SEARCH        → Find target entity with fuzzy matching
4. FETCH         → Get detailed information
5. RETURN        → Provide structured results
```

## Workflow Actions

### 1. Find Entity by Name

**Tool**: `discord_discovery`

**When**: You know an approximate name but not the ID

**Parameters**:
- `intent`: Natural language description OR structured search
- `entity_type`: Optional explicit type ("server", "channel", "role", "member")
- `query`: Search string (name or partial name)
- `guild_id` or `guild_name`: For scoped searches
- `detailed`: Whether to fetch full details (default: true)
- `limit`: Max results to return (default: 5)

**Example Intents**:

```python
# Natural language (intent parsing)
discord_discovery("find channel general in Community Hub")
discord_discovery("get all channels in server 123456")
discord_discovery("find moderator role")

# Structured search
discord_discovery(
    entity_type="channel",
    query="general",
    guild_name="Community Hub",
    detailed=True
)
```

**What happens**:

1. **Parse**: Extracts entity_type, query, guild context
2. **Resolve**: Finds guild if referenced by name
3. **Search**: Fuzzy matches entities (exact > prefix > contains)
4. **Fetch**: Gets detailed info for top match(es)
5. **Return**: Sorted results with relevance scores

**Returns**:

```json
{
  "success": true,
  "action": "discovery",
  "data": {
    "entity_type": "channel",
    "query": "general",
    "matches": [
      {
        "id": "123456789012345678",
        "name": "general",
        "match_type": "exact",
        "details": {
          "type": "text",
          "topic": "General discussion",
          "guild_id": "111222333444555666",
          "guild_name": "Community Hub",
          "permissions": {...}
        }
      }
    ],
    "total_candidates": 25,
    "match_count": 3
  },
  "steps": [
    {"action": "parse_intent", "parsed": {...}},
    {"action": "resolve_guild", "guild_id": "111222333444555666"},
    {"action": "find_entity", "matches": 3},
    {"action": "fetch_details", "entity_id": "123456789012345678"}
  ],
  "errors": []
}
```

---

### 2. List All Entities

**Tool**: `discord_discovery`

**When**: You want to see all entities of a type

**Examples**:

```python
# List all servers
discord_discovery("list all servers")

# List all channels in a server
discord_discovery(
    entity_type="channel",
    query="*",  # wildcard
    guild_id="123456789"
)

# List all roles
discord_discovery("show me all roles in MyServer")
```

**What happens**:

- Returns all entities (no filtering)
- Sorted alphabetically
- Includes basic info (no deep details unless requested)

---

### 3. Get Entity by Exact ID

**Tool**: `discord_get` (atomic tool)

**When**: You have the exact ID and just need details

**Example**:

```python
# Fast lookup by ID (no search needed)
discord_get(
    entity_type="channel",
    entity_id="123456789012345678"
)
```

**What happens**:

- Direct fetch (no fuzzy matching)
- Returns full details
- Faster than discovery workflow

---

## Matching Algorithm

### Match Types

1. **Exact**: Query matches name exactly (case-insensitive)
   - Query: "general" → Match: "general"
   - **Highest priority**

2. **Prefix**: Name starts with query
   - Query: "gen" → Match: "general", "gen-chat"
   - **Medium priority**

3. **Contains**: Query appears anywhere in name
   - Query: "chat" → Match: "general-chat", "off-topic-chat"
   - **Lower priority**

### Sorting

Results are automatically sorted:
1. Exact matches first
2. Prefix matches second
3. Contains matches third
4. Alphabetically within each tier

**Example**:

```python
# Query: "gen"
# Results:
[
  {"name": "gen", "match_type": "exact"},        # 1st
  {"name": "general", "match_type": "prefix"},   # 2nd
  {"name": "gen-chat", "match_type": "prefix"},  # 3rd
  {"name": "hydrogen", "match_type": "contains"} # 4th
]
```

---

## Entity Types

### Server (Guild)

**Fields returned**:
- `id`: Server ID
- `name`: Server name
- `description`: Server description
- `member_count`: Total members
- `owner_id`: Server owner
- `icon_url`: Server icon
- `channels`: List of channel IDs
- `roles`: List of role IDs

**Example**:

```python
discord_discovery("find server Community Hub")
```

---

### Channel

**Fields returned**:
- `id`: Channel ID
- `name`: Channel name
- `type`: Channel type (text, voice, category, etc.)
- `topic`: Channel topic
- `guild_id`: Parent server ID
- `guild_name`: Parent server name
- `permissions`: Bot's permissions in channel
- `parent_category`: Category name (if applicable)

**Example**:

```python
discord_discovery(
    entity_type="channel",
    query="announcements",
    guild_name="Community Hub"
)
```

---

### Role

**Fields returned**:
- `id`: Role ID
- `name`: Role name
- `color`: Role color (hex)
- `position`: Role hierarchy position
- `permissions`: Role permissions
- `mentionable`: Whether role can be @mentioned
- `guild_id`: Parent server ID
- `guild_name`: Parent server name
- `member_count`: Users with this role

**Example**:

```python
discord_discovery("find moderator role in Community Hub")
```

---

### Member (Future v0.3.0)

**Fields returned**:
- `id`: User ID
- `username`: Username
- `display_name`: Server nickname
- `avatar_url`: Avatar URL
- `roles`: List of role IDs
- `joined_at`: Server join date
- `status`: Online status
- `guild_id`: Server ID

---

## Natural Language Intent Parsing

The workflow supports natural language queries that are parsed into structured searches.

### Supported Patterns

**Find specific entity**:
- "find channel general"
- "find channel general in MyServer"
- "show me the announcements channel"

**List entities**:
- "list all channels in MyServer"
- "show me all servers"
- "get roles for Community Hub"

**Get details**:
- "tell me about the general channel"
- "what's the ID of the mods role?"

### Parser Logic

```python
# Input: "find channel general in Community Hub"
# Parsed output:
{
  "entity_type": "channel",
  "query": "general",
  "guild_name": "Community Hub",
  "detailed": True,
  "limit": 5
}
```

The parser extracts:
1. **Action verb**: find, list, get, show
2. **Entity type**: server, channel, role, member
3. **Query**: The name to search for
4. **Scope**: Guild name/ID if mentioned
5. **Options**: detailed, limit

---

## Internal Helpers

### `_find_entity()`

Shared helper used by:
- `discord_discovery` workflow
- `find_server_by_name()` (legacy)
- `find_channel_by_name()` (legacy)
- `find_role_by_name()` (legacy)

**Signature**:

```python
async def _find_entity(
    entity_type: Literal["server", "channel", "role", "member"],
    query: str,
    ctx: Context,
    *,
    guild_id: Optional[str] = None,
    exact_match: bool = False,
    limit: int = 5
) -> Dict[str, Any]
```

**Features**:
- DRY_RUN support
- Allowlist checking
- Fuzzy matching
- Relevance sorting
- Caching (future)

---

### `_get_entity_details()`

Fetches comprehensive information about an entity.

**Signature**:

```python
async def _get_entity_details(
    entity_type: str,
    entity_id: str,
    ctx: Context
) -> Dict[str, Any]
```

**What it fetches**:
- All public properties
- Bot's permissions
- Related entities (e.g., channels in a server)
- Metadata (created_at, etc.)

---

### `parse_discovery_intent()`

Parses natural language into structured query.

**Uses**:
- LLM-based parsing (Anthropic Claude)
- Prompt templates from `resources/discovery/prompts/`
- Fallback to pattern matching

---

## Complete Example Workflow

```python
# Scenario: Send message to #announcements in "Gaming Server"

# Step 1: Find the channel
result = discord_discovery(
    intent="find announcements channel in Gaming Server"
)

# Returns:
{
  "success": True,
  "data": {
    "matches": [
      {
        "id": "123456789",
        "name": "announcements",
        "details": {
          "guild_id": "111222333",
          "guild_name": "Gaming Server",
          "type": "text",
          "permissions": {"send_messages": true}
        }
      }
    ]
  }
}

# Step 2: Use the channel ID to send message
channel_id = result["data"]["matches"][0]["id"]

discord_message(
    action="send",
    channel_id=channel_id,
    content="New tournament starting!"
)
```

---

## Scoped vs Global Searches

### Global Search (No Guild Specified)

Searches across **all** servers the bot is in.

```python
# Searches all servers
discord_discovery("find general channel")

# Returns channels from multiple servers:
[
  {"name": "general", "guild_name": "Server A"},
  {"name": "general", "guild_name": "Server B"},
  {"name": "general-chat", "guild_name": "Server C"}
]
```

### Scoped Search (Guild Specified)

Searches only within specified server.

```python
# Searches only "Community Hub"
discord_discovery(
    entity_type="channel",
    query="general",
    guild_name="Community Hub"
)

# Returns channels only from "Community Hub"
```

**Tip**: Scoped searches are faster and more accurate.

---

## Best Practices

1. **Use scoped searches when possible**: Specify guild_name or guild_id to narrow results

2. **Check match_type**: Exact matches are most reliable

3. **Handle multiple matches**: Always check if multiple results were returned

4. **Cache frequently used IDs**: Store IDs once discovered to avoid repeated searches

5. **Use structured queries for precision**: Natural language is convenient, but structured is more reliable

6. **Check permissions**: Verify bot has required permissions before attempting operations

---

## Error Handling

### No Matches Found

```json
{
  "success": true,
  "data": {
    "matches": [],
    "match_count": 0,
    "total_candidates": 25
  }
}
```

**Suggestions**:
- Try partial name (e.g., "gen" instead of "general")
- Check spelling
- Try global search (remove guild filter)
- Use `discord_list` to see all available entities

---

### Guild Not Found

```json
{
  "success": false,
  "errors": ["Server 'MyServer' not found"]
}
```

**Solutions**:
- List all servers: `discord_discovery("list all servers")`
- Check server name spelling
- Verify bot is in the server

---

### Permission Denied

```json
{
  "success": false,
  "errors": ["Access denied: Guild 123456 not in allowlist"]
}
```

**Solutions**:
- Check `GUILD_ALLOWLIST` environment variable
- Contact admin to add guild to allowlist
- Verify bot has necessary permissions

---

## Comparison: Discovery vs Atomic Tools

### Use Discovery When:
- You don't know exact IDs
- You want natural language queries
- You need fuzzy matching
- You want to explore available entities

### Use Atomic Tools When:
- You have exact IDs
- You need fastest performance
- You're building automation scripts
- You don't need search capabilities

**Example**:

```python
# Discovery (flexible, user-friendly)
discord_discovery("find general channel")

# Atomic (fast, precise)
discord_get("channel", "123456789")
```

---

## Future Enhancements (v0.2+)

### Planned Features:

1. **Caching**: Remember recent searches
2. **Fuzzy scoring**: Levenshtein distance for better matching
3. **Filters**: Search by category, permissions, activity
4. **Suggestions**: "Did you mean...?" for close matches
5. **Batch discovery**: Find multiple entities in one call
6. **History**: Track past searches for context

---

## Database Schema (Future)

**Note**: Current implementation is stateless. Future versions may cache search results.

```sql
-- Discovery cache (future)
CREATE TABLE discovery_cache (
    id INTEGER PRIMARY KEY,
    query TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    guild_id TEXT,
    results TEXT,  -- JSON
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

---

## Resources

### Templates

Located: `resources/discovery/templates/`

- `entity_summary.txt.j2`: Format entity details
- `search_results.txt.j2`: Format search results list

### Prompts

Located: `resources/discovery/prompts/`

- `discovery_intent.yaml`: LLM prompt for intent parsing

**Example usage**:

```python
# In workflow
template = ctx.resources.get_template("discovery/templates/entity_summary.txt.j2")
summary = template.render(entity=match_details)
```

---

## Troubleshooting

**Query returns too many results?**
- Add guild scope to narrow search
- Use more specific query
- Set lower `limit` parameter

**Search is slow?**
- Use `discord_get` if you have the ID
- Enable caching (future)
- Reduce `detailed` to False

**Wrong entity returned?**
- Check `match_type` field
- Use exact_match=True for precise matching
- Specify guild_name explicitly

**Bot can't see entities?**
- Verify bot permissions
- Check guild allowlist
- Ensure bot is in the server
