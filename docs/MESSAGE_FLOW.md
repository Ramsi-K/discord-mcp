# Message Flow Documentation

## Overview

The message workflow handles all Discord message operations: sending messages with mentions and replies, retrieving recent or specific messages, and managing message content. It provides a unified interface for message-related actions with context awareness and safety features.

## Use Case

**Scenario**: You want to send an announcement to a channel, mentioning specific roles, with proper rate limiting and mention controls. The message workflow handles parsing mentions, checking permissions, and sending safely.

## Message Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                     MESSAGE LIFECYCLE                        │
└─────────────────────────────────────────────────────────────┘

1. SEND          → Create and deliver messages with mentions
2. GET           → Retrieve specific or recent messages
3. REPLY         → Respond to existing messages
4. EDIT          → Modify sent messages (future)
5. DELETE        → Remove messages (future)
```

## Workflow Actions

### 1. Send Message

**Tool**: `discord_message`

**When**: Send a new message to a channel

**Parameters**:
- `action`: "send"
- `channel_id`: Target channel ID
- `content`: Message text (up to 2000 characters)
- `reply_to`: Optional message ID to reply to
- `mention_everyone`: Allow @everyone (default: false)
- `mention_here`: Allow @here (default: false)
- `mention_roles`: List of role IDs to @mention
- `mention_users`: List of user IDs to @mention
- `silent`: Send without notification (default: false)

**Example**:

```python
# Simple message
discord_message(
    action="send",
    channel_id="123456789012345678",
    content="Hello everyone!"
)

# With role mentions
discord_message(
    action="send",
    channel_id="123456789012345678",
    content="Tournament starting! @Moderators please prepare.",
    mention_roles=["987654321098765432"]
)

# Reply to another message
discord_message(
    action="send",
    channel_id="123456789012345678",
    content="Thanks for the update!",
    reply_to="111222333444555666"
)
```

**What happens**:

1. **Validate**: Check channel access and permissions
2. **Parse**: Process mention syntax (@user, @role, @everyone, @here)
3. **Format**: Build Discord-compatible message
4. **Safety Check**: Verify mention permissions
5. **Send**: Deliver message via Discord API
6. **Return**: Confirm delivery with message ID

**Returns**:

```json
{
  "success": true,
  "action": "send_message",
  "data": {
    "message_id": "999888777666555444",
    "channel_id": "123456789012345678",
    "content": "Hello everyone!",
    "sent_at": "2025-01-09T12:00:00Z",
    "mentions": {
      "users": [],
      "roles": [],
      "everyone": false,
      "here": false
    }
  },
  "steps": [
    {"action": "validate_channel", "channel_id": "123456789012345678"},
    {"action": "parse_mentions", "parsed": {...}},
    {"action": "send_message", "message_id": "999888777666555444"}
  ],
  "errors": []
}
```

---

### 2. Get Recent Messages

**Tool**: `discord_message`

**When**: Retrieve message history from a channel

**Parameters**:
- `action`: "get_recent"
- `channel_id`: Target channel ID
- `limit`: Max messages to retrieve (default: 50, max: 100)
- `before`: Get messages before this message ID
- `after`: Get messages after this message ID

**Example**:

```python
# Get last 50 messages
discord_message(
    action="get_recent",
    channel_id="123456789012345678",
    limit=50
)

# Pagination: get messages before a specific message
discord_message(
    action="get_recent",
    channel_id="123456789012345678",
    limit=50,
    before="999888777666555444"
)
```

**Returns**:

```json
{
  "success": true,
  "action": "get_recent",
  "data": {
    "channel_id": "123456789012345678",
    "messages": [
      {
        "id": "999888777666555444",
        "author": {
          "id": "111222333444555666",
          "username": "User123",
          "display_name": "User"
        },
        "content": "Hello!",
        "timestamp": "2025-01-09T12:00:00Z",
        "edited_at": null,
        "mentions": [],
        "reactions": [
          {"emoji": "👍", "count": 5}
        ],
        "reply_to": null
      }
    ],
    "count": 50,
    "has_more": true
  }
}
```

---

### 3. Get Specific Message

**Tool**: `discord_message`

**When**: Retrieve a single message by ID

**Parameters**:
- `action`: "get"
- `channel_id`: Channel containing the message
- `message_id`: The message ID to retrieve

**Example**:

```python
discord_message(
    action="get",
    channel_id="123456789012345678",
    message_id="999888777666555444"
)
```

**Returns**: Full message details including:
- Content
- Author info
- Timestamp
- Edit history
- Reactions
- Attachments
- Embeds

---

### 4. Send with Advanced Mentions

**Mention Syntax**: The workflow automatically parses mention syntax

**User Mentions**:
```python
# In content
content="Hey @User123, check this out!"

# Or explicit
mention_users=["111222333444555666"]
```

**Role Mentions**:
```python
# In content
content="@Moderators please review"

# Or explicit
mention_roles=["987654321098765432"]
```

**Everyone/Here Mentions**:
```python
# Requires explicit permission
mention_everyone=True  # Enables @everyone
mention_here=True      # Enables @here
```

**Safety Features**:
- `mention_everyone` and `mention_here` default to `false`
- Bot must have "Mention Everyone" permission
- Mentions are validated before sending
- Invalid mentions are stripped

---

### 5. Reply to Message

**Tool**: `discord_message`

**When**: Respond to an existing message with threading

**Example**:

```python
discord_message(
    action="send",
    channel_id="123456789012345678",
    content="That's a great point!",
    reply_to="999888777666555444"  # Message ID to reply to
)
```

**What happens**:
- Creates a threaded reply
- Shows reference to original message
- Pings original author (unless `silent=True`)
- Maintains conversation context

---

## Message Formatting

### Text Formatting

Discord supports Markdown:

```python
content="""
**Bold text**
*Italic text*
***Bold and italic***
__Underline__
~~Strikethrough~~
`inline code`
```
code block
```
> Quote
"""
```

### Embeds (Future v0.2)

Rich embed support coming in future versions:

```python
discord_message(
    action="send",
    channel_id="123456",
    embeds=[{
        "title": "Announcement",
        "description": "Important update",
        "color": 0x5865F2,
        "fields": [
            {"name": "Field 1", "value": "Value 1"}
        ]
    }]
)
```

### Attachments (Future v0.2)

File upload support:

```python
discord_message(
    action="send",
    channel_id="123456",
    content="Here's the file",
    attachments=["path/to/file.pdf"]
)
```

---

## Internal Helpers

### `_parse_mentions()`

Parses mention syntax in message content.

**Signature**:

```python
async def _parse_mentions(
    content: str,
    ctx: Context,
    *,
    guild_id: Optional[str] = None,
    allow_everyone: bool = False,
    allow_here: bool = False
) -> Dict[str, Any]
```

**What it does**:
- Finds @username, @role patterns
- Resolves to Discord IDs
- Validates permissions
- Returns structured mention data

---

### `_validate_message_permissions()`

Checks if bot can send to channel.

**Validates**:
- Send Messages permission
- Mention Everyone permission (if needed)
- Embed Links permission (if needed)
- Attach Files permission (if needed)
- View Channel permission

---

### `_format_message_content()`

Formats message content for Discord API.

**Handles**:
- Character limit (2000)
- Mention formatting
- Markdown escaping
- URL formatting

---

## Complete Example Workflows

### Workflow 1: Announcement with Mentions

```python
# Scenario: Send tournament announcement mentioning Moderators role

# Step 1: Find the announcements channel
channel = discord_discovery(
    entity_type="channel",
    query="announcements",
    guild_name="Gaming Server"
)
channel_id = channel["data"]["matches"][0]["id"]

# Step 2: Find the Moderators role
role = discord_discovery(
    entity_type="role",
    query="Moderators",
    guild_name="Gaming Server"
)
role_id = role["data"]["matches"][0]["id"]

# Step 3: Send announcement
discord_message(
    action="send",
    channel_id=channel_id,
    content="""
🎮 **Tournament Announcement**

The annual tournament starts this Saturday at 6 PM!

@Moderators please prepare the tournament channels.

React with 👍 to sign up!
    """,
    mention_roles=[role_id]
)
```

---

### Workflow 2: Conversation Reply

```python
# Scenario: Reply to a user's question

# Step 1: Get recent messages to find the question
messages = discord_message(
    action="get_recent",
    channel_id="123456789",
    limit=10
)

# Step 2: Find message containing "how do I"
question = next(
    m for m in messages["data"]["messages"]
    if "how do i" in m["content"].lower()
)

# Step 3: Reply to the question
discord_message(
    action="send",
    channel_id="123456789",
    content="Here's how you can do that: [explanation]",
    reply_to=question["id"]
)
```

---

### Workflow 3: Broadcast to Multiple Channels

```python
# Scenario: Send same message to all announcement channels

# Step 1: Find all channels with "announce" in name
channels = discord_discovery(
    entity_type="channel",
    query="announce",
    guild_name="Gaming Server"
)

# Step 2: Send to each channel
for channel in channels["data"]["matches"]:
    discord_message(
        action="send",
        channel_id=channel["id"],
        content="Important server update: [message]"
    )
    # Rate limit: wait 1 second between sends
    await asyncio.sleep(1)
```

---

## Safety & Rate Limiting

### Built-in Safety

1. **Content validation**: Checks for empty or too-long messages
2. **Permission checks**: Verifies bot has required permissions
3. **Mention protection**: Blocks @everyone unless explicitly allowed
4. **DRY_RUN mode**: Test without actually sending

### Rate Limiting

Discord enforces rate limits:
- **5 messages per 5 seconds per channel**
- **50 messages per second globally**

The workflow automatically:
- Tracks send rate
- Delays when approaching limits
- Returns rate limit info in errors

**Manual rate limiting**:

```python
for msg in messages:
    discord_message(action="send", ...)
    await asyncio.sleep(1)  # 1 second between messages
```

---

### DRY_RUN Mode

Test message sending without actually sending:

```python
discord_message(
    action="send",
    channel_id="123456",
    content="Test message",
    dry_run=True  # Won't actually send
)

# Returns what WOULD be sent:
{
  "success": true,
  "data": {
    "would_send": {
      "channel_id": "123456",
      "content": "Test message",
      "mentions": {...}
    }
  },
  "dry_run": true
}
```

---

## Mention Controls

### Default Behavior (Safe)

```python
# This is SAFE - mentions are disabled by default
discord_message(
    action="send",
    content="@everyone check this out!"
)
# Result: Sends literal "@everyone" text, doesn't ping
```

### Explicit Mentions (Controlled)

```python
# This enables @everyone mentions
discord_message(
    action="send",
    content="@everyone important announcement!",
    mention_everyone=True  # Must be explicitly enabled
)
# Result: Pings all users
```

### Individual Mentions (Always Allowed)

```python
# User/role mentions are always parsed
discord_message(
    action="send",
    content="Hey <@123456789>, thanks!",
    mention_users=["123456789"]
)
# Result: Pings user 123456789
```

---

## Best Practices

1. **Always validate channel access first**: Use `discord_discovery` to verify channel exists

2. **Use `reply_to` for context**: Threading keeps conversations organized

3. **Respect rate limits**: Add delays between bulk sends

4. **Test with DRY_RUN**: Always test mention-heavy messages first

5. **Limit @everyone usage**: Only use for critical announcements

6. **Check message length**: Max 2000 characters, plan for chunking

7. **Use silent mode for bulk messages**: Avoid notification spam with `silent=True`

---

## Error Handling

### Channel Not Found

```json
{
  "success": false,
  "errors": ["Channel '123456' not found or bot has no access"]
}
```

**Solutions**:
- Verify channel ID
- Check bot permissions
- Use `discord_discovery` to find channel

---

### Missing Permissions

```json
{
  "success": false,
  "errors": ["Missing permission: SEND_MESSAGES in channel 123456"]
}
```

**Solutions**:
- Check bot role permissions
- Verify channel-specific overrides
- Contact server admin

---

### Rate Limited

```json
{
  "success": false,
  "errors": ["Rate limited: retry after 3.2 seconds"],
  "retry_after": 3.2
}
```

**Solutions**:
- Wait the specified duration
- Reduce send frequency
- Implement retry logic

---

### Message Too Long

```json
{
  "success": false,
  "errors": ["Message exceeds 2000 character limit (2450 characters)"]
}
```

**Solutions**:
- Split into multiple messages
- Use message chunking (see campaign workflow)
- Shorten content

---

## Message Retrieval Patterns

### Recent Activity

```python
# Get last 10 messages for context
discord_message(
    action="get_recent",
    channel_id="123456",
    limit=10
)
```

### Search History

```python
# Get older messages by pagination
messages = []
last_id = None

for _ in range(5):  # Get 5 pages
    result = discord_message(
        action="get_recent",
        channel_id="123456",
        limit=100,
        before=last_id
    )
    messages.extend(result["data"]["messages"])
    last_id = result["data"]["messages"][-1]["id"]
```

### Find Specific Content

```python
# Get recent messages and filter
messages = discord_message(
    action="get_recent",
    channel_id="123456",
    limit=100
)

# Find messages containing keyword
matches = [
    m for m in messages["data"]["messages"]
    if "tournament" in m["content"].lower()
]
```

---

## Resources

### Templates

Located: `resources/message/templates/`

- `announcement.txt.j2`: Standard announcement format
- `reply.txt.j2`: Reply message format
- `error_response.txt.j2`: Error message format

**Example usage**:

```python
template = ctx.resources.get_template("message/templates/announcement.txt.j2")
content = template.render(
    title="Tournament Update",
    body="Registration closes tomorrow!",
    mentions=["@Moderators"]
)

discord_message(action="send", content=content, ...)
```

---

### Prompts

Located: `resources/message/prompts/`

- `message_intent.yaml`: Parse natural language message requests
- `mention_suggestion.yaml`: Suggest who to mention

---

## Future Enhancements (v0.2+)

### Planned Features:

1. **Message editing**: Modify sent messages
2. **Message deletion**: Remove messages
3. **Bulk operations**: Send to multiple channels
4. **Rich embeds**: Create formatted embed messages
5. **File attachments**: Upload files with messages
6. **Reactions**: Add reactions to messages
7. **Message templates**: Reusable message formats
8. **Scheduled messages**: Send at specific times

---

## Comparison: Message Workflow vs Atomic

### Use Message Workflow When:
- Sending messages with mentions
- Need mention validation
- Want reply threading
- Building user-facing features

### Use `discord_send` (Atomic) When:
- Have exact channel ID
- Simple text message
- Need fastest performance
- No mention parsing needed

**Example**:

```python
# Workflow (safe, feature-rich)
discord_message(
    action="send",
    channel_id="123",
    content="@Mods check this",
    mention_roles=["456"]
)

# Atomic (fast, basic)
discord_send(
    channel_id="123",
    content="Simple message"
)
```

---

## Troubleshooting

**Messages not sending?**
- Check bot permissions
- Verify channel ID is correct
- Check rate limits
- Ensure bot is in the server

**Mentions not working?**
- Verify mention_everyone/mention_here are set
- Check bot has "Mention Everyone" permission
- Use explicit mention_users/mention_roles lists
- Ensure user/role IDs are correct

**Messages getting truncated?**
- Check 2000 character limit
- Split into multiple messages
- Use chunking logic

**Reply not threading?**
- Verify reply_to message ID exists
- Check message is in same channel
- Ensure bot can view referenced message
