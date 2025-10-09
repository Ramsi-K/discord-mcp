# Diagnostics Flow Documentation

## Overview

The diagnostics workflow provides health checks, status monitoring, and connection verification for the Discord MCP bot. It helps troubleshoot issues, verify bot connectivity, and ensure proper configuration before performing operations.

## Use Case

**Scenario**: Before running important automation, you want to verify the bot is online, connected to Discord, has access to required servers, and has necessary permissions. The diagnostics workflow checks everything in one call.

## Diagnostics Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                   DIAGNOSTICS LIFECYCLE                      │
└─────────────────────────────────────────────────────────────┘

1. STATUS        → Check bot connection and health
2. PING          → Verify Discord API latency
3. ACCESS        → Confirm server/channel access
4. PERMISSIONS   → Validate bot permissions
5. CONFIG        → Verify configuration settings
6. REPORT        → Generate comprehensive health report
```

## Workflow Actions

### 1. Bot Status Check

**Tool**: `discord_diagnostics`

**When**: Verify bot is online and connected

**Parameters**:
- `action`: "status"
- `detailed`: Include detailed info (default: true)

**Example**:

```python
# Quick status
discord_diagnostics(action="status")

# Detailed status
discord_diagnostics(action="status", detailed=True)
```

**What happens**:

1. **Connection Check**: Verify bot is connected to Discord
2. **User Info**: Get bot's username and ID
3. **Guild Count**: Count servers bot is in
4. **Latency**: Measure API response time
5. **Uptime**: Calculate time since bot started

**Returns**:

```json
{
  "success": true,
  "action": "status",
  "data": {
    "bot_user": "MyBot#1234",
    "bot_id": "123456789012345678",
    "connected": true,
    "status": "online",
    "guilds": {
      "count": 5,
      "names": ["Server A", "Server B", "Server C", "Server D", "Server E"]
    },
    "latency_ms": 45.3,
    "uptime_seconds": 3600,
    "shard_id": 0,
    "shard_count": 1
  },
  "steps": [
    {"action": "check_connection", "connected": true},
    {"action": "get_bot_info", "bot_id": "123456789012345678"},
    {"action": "count_guilds", "count": 5},
    {"action": "measure_latency", "latency_ms": 45.3}
  ],
  "errors": []
}
```

---

### 2. Ping Discord

**Tool**: `discord_diagnostics`

**When**: Check connection health and latency

**Parameters**:
- `action`: "ping"
- `guild_id`: Optional server to verify access to

**Example**:

```python
# Basic ping
discord_diagnostics(action="ping")

# Ping with server verification
discord_diagnostics(
    action="ping",
    guild_id="111222333444555666"
)
```

**What happens**:

1. **API Ping**: Send test request to Discord API
2. **Measure Latency**: Calculate round-trip time
3. **Verify Access**: If guild_id provided, check bot can access it
4. **Return Status**: Report connection health

**Returns**:

```json
{
  "success": true,
  "action": "ping",
  "data": {
    "latency_ms": 42.7,
    "api_version": 10,
    "status": "healthy",
    "guild_accessible": true,
    "timestamp": "2025-01-09T12:00:00Z"
  },
  "steps": [
    {"action": "ping_api", "latency_ms": 42.7},
    {"action": "verify_guild_access", "guild_id": "111222333444555666", "accessible": true}
  ],
  "errors": []
}
```

**Latency Interpretation**:
- **< 100ms**: Excellent
- **100-200ms**: Good
- **200-500ms**: Moderate
- **> 500ms**: Slow (potential issues)

---

### 3. Verify Server Access

**Tool**: `discord_diagnostics`

**When**: Confirm bot has access to specific servers

**Parameters**:
- `action`: "verify_access"
- `guild_ids`: List of server IDs to check
- `check_permissions`: Whether to check permissions (default: false)

**Example**:

```python
discord_diagnostics(
    action="verify_access",
    guild_ids=[
        "111222333444555666",
        "777888999000111222"
    ],
    check_permissions=True
)
```

**Returns**:

```json
{
  "success": true,
  "action": "verify_access",
  "data": {
    "checked": 2,
    "accessible": 2,
    "inaccessible": 0,
    "results": [
      {
        "guild_id": "111222333444555666",
        "accessible": true,
        "guild_name": "Community Hub",
        "permissions": {
          "send_messages": true,
          "manage_messages": true,
          "mention_everyone": false
        }
      },
      {
        "guild_id": "777888999000111222",
        "accessible": true,
        "guild_name": "Gaming Server",
        "permissions": {
          "send_messages": true,
          "manage_messages": false,
          "mention_everyone": true
        }
      }
    ]
  }
}
```

---

### 4. Check Permissions

**Tool**: `discord_diagnostics`

**When**: Verify bot has required permissions in a channel/server

**Parameters**:
- `action`: "check_permissions"
- `channel_id` OR `guild_id`: Where to check permissions
- `required_permissions`: List of required permissions

**Example**:

```python
# Check channel permissions
discord_diagnostics(
    action="check_permissions",
    channel_id="123456789012345678",
    required_permissions=[
        "send_messages",
        "embed_links",
        "attach_files"
    ]
)

# Check server permissions
discord_diagnostics(
    action="check_permissions",
    guild_id="111222333444555666",
    required_permissions=[
        "manage_roles",
        "kick_members"
    ]
)
```

**Returns**:

```json
{
  "success": true,
  "action": "check_permissions",
  "data": {
    "channel_id": "123456789012345678",
    "channel_name": "general",
    "all_permissions_granted": false,
    "permissions": {
      "send_messages": {
        "granted": true,
        "required": true
      },
      "embed_links": {
        "granted": true,
        "required": true
      },
      "attach_files": {
        "granted": false,
        "required": true
      }
    },
    "missing_permissions": ["attach_files"]
  },
  "warnings": ["Missing required permission: attach_files"]
}
```

---

### 5. Configuration Check

**Tool**: `discord_diagnostics`

**When**: Verify environment configuration is correct

**Parameters**:
- `action`: "check_config"
- `verbose`: Show full config details (default: false)

**Example**:

```python
discord_diagnostics(action="check_config", verbose=True)
```

**Returns**:

```json
{
  "success": true,
  "action": "check_config",
  "data": {
    "token_configured": true,
    "database_configured": true,
    "database_path": "C:/path/to/discord_mcp.db",
    "dry_run": false,
    "log_level": "INFO",
    "guild_allowlist": ["111222333444555666"],
    "guild_allowlist_enabled": true,
    "environment_variables": {
      "DISCORD_TOKEN": "configured (hidden)",
      "MCP_DISCORD_DB_PATH": "C:/path/to/discord_mcp.db",
      "GUILD_ALLOWLIST": "1 guild(s) configured",
      "LOG_LEVEL": "INFO",
      "DRY_RUN": "false"
    }
  },
  "warnings": [],
  "errors": []
}
```

---

### 6. Full Health Report

**Tool**: `discord_diagnostics`

**When**: Generate comprehensive diagnostic report

**Parameters**:
- `action`: "health_report"
- `include_guilds`: Include guild details (default: true)
- `include_permissions`: Check permissions (default: false)

**Example**:

```python
discord_diagnostics(
    action="health_report",
    include_guilds=True,
    include_permissions=True
)
```

**What happens**:

Runs all diagnostic checks:
1. Bot status
2. Connection ping
3. Configuration validation
4. Guild access verification
5. Permission checks (if enabled)

**Returns**: Comprehensive report with all diagnostic data

---

## Common Diagnostic Patterns

### Pre-Operation Check

Before running important operations, verify everything is ready:

```python
# Run full diagnostics
report = discord_diagnostics(action="health_report")

if not report["success"]:
    print("Bot health check failed!")
    print(report["errors"])
    exit(1)

# Check specific guild access
if guild_id in report["data"]["inaccessible_guilds"]:
    print(f"Bot cannot access guild {guild_id}")
    exit(1)

# Proceed with operation
discord_campaign(...)
```

---

### Troubleshooting Connection Issues

```python
# Step 1: Check bot status
status = discord_diagnostics(action="status")

if not status["data"]["connected"]:
    print("Bot is not connected to Discord!")
    # Check token, restart bot
    exit(1)

# Step 2: Ping Discord API
ping = discord_diagnostics(action="ping")

if ping["data"]["latency_ms"] > 500:
    print("High latency detected, connection may be unstable")

# Step 3: Verify specific guild
access = discord_diagnostics(
    action="ping",
    guild_id="123456789"
)

if not access["data"]["guild_accessible"]:
    print("Bot cannot access guild 123456789")
    print("Ensure bot is invited and has proper permissions")
```

---

### Permission Validation

Before attempting operations that require specific permissions:

```python
# Check if bot can send messages in target channel
perms = discord_diagnostics(
    action="check_permissions",
    channel_id="123456789",
    required_permissions=["send_messages", "embed_links"]
)

if not perms["data"]["all_permissions_granted"]:
    print("Missing permissions:")
    for perm in perms["data"]["missing_permissions"]:
        print(f"  - {perm}")
    exit(1)

# Permissions OK, proceed
discord_message(...)
```

---

## Internal Helpers

### `_check_bot_connection()`

Verifies bot is connected to Discord.

**Signature**:

```python
async def _check_bot_connection(ctx: Context) -> bool
```

**Returns**: True if connected, False otherwise

---

### `_measure_latency()`

Measures Discord API latency.

**Signature**:

```python
async def _measure_latency(ctx: Context) -> float
```

**Returns**: Latency in milliseconds

---

### `_verify_guild_access()`

Checks if bot can access a specific guild.

**Signature**:

```python
async def _verify_guild_access(
    guild_id: str,
    ctx: Context
) -> Dict[str, Any]
```

**Returns**:
```python
{
    "guild_id": "123456789",
    "accessible": True,
    "guild_name": "Community Hub",
    "member_count": 1234,
    "bot_permissions": [...]
}
```

---

### `_check_channel_permissions()`

Validates bot permissions in a channel.

**Signature**:

```python
async def _check_channel_permissions(
    channel_id: str,
    required_permissions: List[str],
    ctx: Context
) -> Dict[str, Any]
```

---

## Complete Example Workflows

### Workflow 1: Pre-Deployment Check

```python
# Before deploying bot to production

# Step 1: Check configuration
config = discord_diagnostics(action="check_config", verbose=True)

if not config["data"]["token_configured"]:
    print("ERROR: DISCORD_TOKEN not configured!")
    exit(1)

# Step 2: Verify bot is online
status = discord_diagnostics(action="status")

if not status["data"]["connected"]:
    print("ERROR: Bot is not connected to Discord!")
    exit(1)

# Step 3: Verify access to required guilds
required_guilds = ["123456", "789012"]
access = discord_diagnostics(
    action="verify_access",
    guild_ids=required_guilds
)

if access["data"]["inaccessible"] > 0:
    print("WARNING: Bot cannot access some required guilds")
    for result in access["data"]["results"]:
        if not result["accessible"]:
            print(f"  - Cannot access: {result['guild_id']}")

# Step 4: Full health report
report = discord_diagnostics(action="health_report")

print("✅ All checks passed - bot is ready for deployment")
```

---

### Workflow 2: Monitor Bot Health

```python
# Periodic health monitoring

import asyncio

async def monitor_health():
    while True:
        # Check every 5 minutes
        await asyncio.sleep(300)

        # Quick ping check
        ping = discord_diagnostics(action="ping")

        latency = ping["data"]["latency_ms"]

        if latency > 500:
            print(f"⚠️ High latency detected: {latency}ms")
            # Send alert
        elif latency > 200:
            print(f"ℹ️ Moderate latency: {latency}ms")

        # Check bot status
        status = discord_diagnostics(action="status")

        if not status["data"]["connected"]:
            print("🚨 Bot disconnected from Discord!")
            # Send critical alert
            # Attempt reconnect

asyncio.run(monitor_health())
```

---

### Workflow 3: Debug Permission Issues

```python
# User reports bot isn't working in a channel

channel_id = "123456789"

# Step 1: Check if bot can access channel
try:
    channel_info = discord_get(
        entity_type="channel",
        entity_id=channel_id
    )
    print(f"✅ Bot can see channel: {channel_info['name']}")
except:
    print(f"❌ Bot cannot access channel {channel_id}")
    print("Possible causes:")
    print("  - Channel doesn't exist")
    print("  - Bot not in server")
    print("  - Bot blocked from channel")
    exit(1)

# Step 2: Check bot permissions in channel
perms = discord_diagnostics(
    action="check_permissions",
    channel_id=channel_id,
    required_permissions=[
        "view_channel",
        "send_messages",
        "embed_links",
        "attach_files",
        "read_message_history"
    ]
)

if not perms["data"]["all_permissions_granted"]:
    print("❌ Missing permissions:")
    for perm in perms["data"]["missing_permissions"]:
        print(f"  - {perm}")
    print("\nFix: Grant these permissions to bot role")
else:
    print("✅ Bot has all required permissions")

# Step 3: Test send message
print("\nTesting message send...")
test = discord_message(
    action="send",
    channel_id=channel_id,
    content="Test message from diagnostics",
    dry_run=True
)

if test["success"]:
    print("✅ Message send test passed")
else:
    print(f"❌ Message send failed: {test['errors']}")
```

---

## Diagnostic Alerts

### Warning Levels

**INFO**: Informational, no action needed
- Moderate latency (100-200ms)
- Large guild count
- Shard information

**WARNING**: Potential issue, monitor
- High latency (200-500ms)
- Missing non-critical permissions
- Configuration suggestions

**ERROR**: Critical issue, requires action
- Bot disconnected
- Very high latency (>500ms)
- Missing critical permissions
- Configuration errors

---

## Best Practices

1. **Run diagnostics before critical operations**: Always check health before important tasks

2. **Monitor latency regularly**: High latency indicates connection issues

3. **Validate permissions proactively**: Check permissions before attempting operations

4. **Log diagnostic results**: Keep health check logs for troubleshooting

5. **Set up alerts**: Monitor bot health and alert on failures

6. **Check configuration on startup**: Verify config when bot starts

7. **Test in DRY_RUN first**: Use dry_run mode to test without side effects

---

## Error Scenarios

### Bot Disconnected

```json
{
  "success": false,
  "action": "status",
  "data": {
    "connected": false
  },
  "errors": ["Bot is not connected to Discord"]
}
```

**Solutions**:
- Check DISCORD_TOKEN is valid
- Verify network connectivity
- Restart bot process
- Check Discord API status

---

### Guild Not Accessible

```json
{
  "success": false,
  "action": "verify_access",
  "data": {
    "guild_id": "123456",
    "accessible": false
  },
  "errors": ["Bot is not a member of guild 123456"]
}
```

**Solutions**:
- Invite bot to server
- Check guild allowlist
- Verify bot wasn't kicked/banned

---

### Missing Permissions

```json
{
  "success": false,
  "action": "check_permissions",
  "data": {
    "all_permissions_granted": false,
    "missing_permissions": ["send_messages", "embed_links"]
  },
  "errors": ["Missing required permissions"]
}
```

**Solutions**:
- Update bot role permissions
- Check channel-specific overrides
- Contact server admin

---

### High Latency

```json
{
  "success": true,
  "action": "ping",
  "data": {
    "latency_ms": 842.5,
    "status": "degraded"
  },
  "warnings": ["High latency detected (>500ms)"]
}
```

**Solutions**:
- Check network connection
- Verify Discord API status
- Consider shard rebalancing
- Monitor for improvements

---

## Resources

### Templates

Located: `resources/diagnostics/templates/`

- `health_report.txt.j2`: Formatted health report
- `permission_report.txt.j2`: Permission check summary
- `alert.txt.j2`: Alert notification format

**Example usage**:

```python
template = ctx.resources.get_template("diagnostics/templates/health_report.txt.j2")
report_text = template.render(
    status=status_data,
    guilds=guild_data,
    latency=latency_data
)
```

---

## Future Enhancements (v0.2+)

### Planned Features:

1. **Historical tracking**: Store diagnostic history in database
2. **Trend analysis**: Detect degrading performance over time
3. **Automated remediation**: Auto-restart on failures
4. **Detailed logging**: Per-operation performance metrics
5. **Shard diagnostics**: Per-shard health monitoring
6. **Webhook alerts**: Send health alerts to Discord webhook
7. **Dashboard**: Web UI for monitoring bot health

---

## Database Schema (Future)

```sql
-- Diagnostic history (future)
CREATE TABLE diagnostic_history (
    id INTEGER PRIMARY KEY,
    check_type TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    latency_ms REAL,
    guild_count INTEGER,
    details TEXT,  -- JSON
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alert log (future)
CREATE TABLE alert_log (
    id INTEGER PRIMARY KEY,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,  -- INFO, WARNING, ERROR
    message TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);
```

---

## Troubleshooting

**Diagnostics returning stale data?**
- No caching currently implemented
- All checks query live Discord API
- Ensure bot is connected

**Permission checks inconsistent?**
- Permissions can change dynamically
- Channel overrides may apply
- Check both role and channel permissions

**Latency measurements vary widely?**
- Normal variation based on network/load
- Take average of multiple measurements
- Compare to Discord API status page

**Bot appears online but operations fail?**
- Check specific guild access
- Verify channel permissions
- Look for rate limiting
- Check for partial outages
