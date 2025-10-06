# Core Discord Tools (v0.1.0)

These are the currently implemented and tested tools in the Discord MCP server.

## Server & Channel Information

### `discord_list_servers`

- **Description**: List all servers (guilds) the bot is a member of
- **Parameters**: None
- **Returns**: List of server IDs, names, and member counts
- **Status**: ✅ Implemented

### `discord_list_channels`

- **Description**: List channels in a Discord server with optional type filtering
- **Parameters**:
  - `server_id` (string, required): Discord server/guild ID
  - `channel_type` (string, optional): Filter by type ("text", "voice", "category", "forum")
- **Returns**: List of channels with IDs, names, types, and topics
- **Status**: ✅ Implemented

### `discord_get_channel_info`

- **Description**: Get detailed information about a Discord channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
- **Returns**: Channel details including permissions, topic, type, etc.
- **Status**: ✅ Implemented

### `discord_bot_status`

- **Description**: Get the current status and health information of the Discord bot
- **Parameters**: None
- **Returns**: Connection status, latency, server count, user info
- **Status**: ✅ Implemented

## Message Tools

### `discord_get_recent_messages`

- **Description**: Get recent messages from a Discord channel with pagination support
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `limit` (integer, optional, default=10): Number of messages to retrieve (1-100)
- **Returns**: List of messages with content, author, timestamp, reactions
- **Status**: ✅ Implemented

### `discord_get_message`

- **Description**: Get a specific message by ID from a Discord channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message_id` (string, required): Discord message ID
- **Returns**: Message details including content, author, embeds, reactions
- **Status**: ✅ Implemented

### `discord_send_message`

- **Description**: Send a message to a Discord channel with optional reply support
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `content` (string, required): Message content
  - `reply_to_message_id` (string, optional): Message ID to reply to
- **Returns**: Sent message ID and timestamp
- **Status**: ✅ Implemented
- **DRY_RUN**: Supported

## Campaign & Reminder Tools (v0.1.0)

### `discord_create_campaign`

- **Description**: Create a new reaction opt-in reminder campaign
- **Parameters**:
  - `title` (string, optional): Campaign title
  - `channel_id` (string, required): Channel ID for the announcement
  - `message_id` (string, required): Message ID to track reactions on
  - `emoji` (string, required): Emoji to track (e.g., "✅", "👍")
  - `remind_at` (string, required): ISO timestamp for when to send reminder
- **Returns**: Campaign ID and details
- **Status**: ✅ Implemented
- **Database**: SQLite with campaigns table

### `discord_tally_optins`

- **Description**: Fetch reactions from Discord and store deduplicated opt-ins for a campaign
- **Parameters**:
  - `campaign_id` (integer, required): Campaign ID
- **Returns**: List of users who reacted, count of new opt-ins
- **Status**: ✅ Implemented
- **Idempotent**: Yes (no duplicates)

### `discord_list_optins`

- **Description**: List opt-ins for a campaign with pagination support
- **Parameters**:
  - `campaign_id` (integer, required): Campaign ID
  - `limit` (integer, optional, default=50): Results per page
  - `offset` (integer, optional, default=0): Pagination offset
- **Returns**: Paginated list of opt-ins with user IDs and usernames
- **Status**: ✅ Implemented

### `discord_build_reminder`

- **Description**: Build reminder message with @mention chunking under 2000 characters
- **Parameters**:
  - `campaign_id` (integer, required): Campaign ID
  - `custom_message` (string, optional): Custom reminder text
- **Returns**: Array of message chunks ready to send
- **Status**: ✅ Implemented
- **Features**: Automatic chunking, mention formatting

### `discord_send_reminder`

- **Description**: Send reminder messages with rate limiting and batch processing
- **Parameters**:
  - `campaign_id` (integer, required): Campaign ID
  - `custom_message` (string, optional): Custom reminder text
- **Returns**: Success status, messages sent count, reminder log ID
- **Status**: ✅ Implemented
- **Features**: Rate limiting (1 msg/sec), DRY_RUN support

### `discord_run_due_reminders`

- **Description**: Process scheduled campaigns that are due for reminders
- **Parameters**: None
- **Returns**: List of processed campaigns and results
- **Status**: ✅ Implemented
- **Use case**: Call via scheduler or manually

## Legacy Server Registry Tools

These tools are maintained for backward compatibility but will be deprecated in v0.2.0:

- `server_info` → Use `discord_list_servers`
- `list_servers` → Use `discord_list_servers`
- `server_channels` → Use `discord_list_channels`
- `server_roles` → Use `discord_list_roles` (when implemented)
- `find_server` → Use natural language with registry
- `find_channel` → Use natural language with registry
- `find_role` → Use natural language with registry

## Environment Variables

All tools respect these environment variables:

- `DISCORD_TOKEN` (required): Discord bot token
- `MCP_DISCORD_DB_PATH` (optional): Database path (default: discord_mcp.db)
- `DRY_RUN` (optional): Set to "true" to mock Discord API calls
- `LOG_LEVEL` (optional): Logging level (default: INFO)
- `GUILD_ALLOWLIST` (optional): Comma-separated allowed server IDs

## Testing

All implemented tools have been tested with:

- DRY_RUN mode for offline testing
- Real Discord API integration
- Error handling and validation
- Permission checks
