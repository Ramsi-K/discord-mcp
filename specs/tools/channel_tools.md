# Channel Management Tools

This document specifies the channel management tools for the Discord MCP server.

## Channel Information Tools

### `discord_channel_stats`

- **Description**: Get activity statistics for a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `days` (integer, optional, default=7): Timeframe in days
  - `include_user_stats` (boolean, optional, default=true): Whether to include per-user statistics
- **Returns**: Message count, unique authors, peak times, engagement metrics
- **Example Response**:

  ```json
  {
    "channel_id": "111222333444555666",
    "channel_name": "general",
    "days_analyzed": 7,
    "message_count": 1250,
    "unique_authors": 45,
    "reactions_count": 230,
    "peak_times": ["18:00-20:00 UTC", "22:00-00:00 UTC"],
    "top_authors": [
      { "id": "123456789012345678", "name": "Username", "messages": 42 }
    ]
  }
  ```

- **Permissions**: View Channel

### `discord_list_channels`

- **Description**: List all channels in a server
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `type` (string, optional): Filter by channel type ("text", "voice", "category", "forum", "thread")
  - `include_private` (boolean, optional, default=false): Whether to include private channels
- **Returns**: List of channels with their details
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "channels": [
      {
        "id": "111222333444555666",
        "name": "general",
        "type": "text",
        "topic": "General discussion",
        "position": 0,
        "parent_id": null,
        "is_nsfw": false
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: View Channels

## Message Tools

### `discord_send_message`

- **Description**: Send a message to a specific channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message` (string, required): Message content
  - `mention_everyone` (boolean, optional, default=false): Whether to mention @everyone
  - `embeds` (array, optional): Array of embed objects for rich content
  - `components` (array, optional): Array of component objects for interactive elements
- **Returns**: Message ID and timestamp
- **Example Response**:

  ```json
  {
    "success": true,
    "message_id": "111222333444555666",
    "channel_id": "111222333444555666",
    "timestamp": "2023-01-01T00:00:00Z"
  }
  ```

- **Permissions**: Send Messages in the channel

### `discord_get_message`

- **Description**: Get a specific message by ID
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message_id` (string, required): Discord message ID
- **Returns**: Message content and metadata
- **Example Response**:

  ```json
  {
    "id": "111222333444555666",
    "channel_id": "111222333444555666",
    "author": {
      "id": "123456789012345678",
      "name": "Username",
      "display_name": "Display Name"
    },
    "content": "Hello world!",
    "timestamp": "2023-01-01T00:00:00Z",
    "edited_timestamp": null,
    "attachments": [],
    "embeds": [],
    "reactions": [{ "emoji": "👍", "count": 3 }]
  }
  ```

- **Permissions**: View Channel, Read Message History

### `discord_get_recent_messages`

- **Description**: Get recent messages from a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `limit` (integer, optional, default=50): Maximum number of messages to retrieve
  - `before` (string, optional): Message ID to get messages before
  - `after` (string, optional): Message ID to get messages after
- **Returns**: List of messages
- **Example Response**:

  ```json
  {
    "channel_id": "111222333444555666",
    "messages": [
      {
        "id": "111222333444555666",
        "author": {
          "id": "123456789012345678",
          "name": "Username"
        },
        "content": "Hello world!",
        "timestamp": "2023-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: View Channel, Read Message History

### `discord_reaction_analytics`

- **Description**: Analyze reactions to a specific message
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message_id` (string, required): Discord message ID
  - `include_users` (boolean, optional, default=true): Whether to include user details
- **Returns**: Reaction counts and users who reacted
- **Example Response**:

  ```json
  {
    "message_id": "111222333444555666",
    "total_reactions": 42,
    "reactions": [
      {
        "emoji": "👍",
        "count": 20,
        "users": [{ "id": "123456789012345678", "name": "Username" }]
      }
    ]
  }
  ```

- **Permissions**: View Channel, Read Message History

## Thread Tools

### `discord_list_threads`

- **Description**: List active threads in a channel or server
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `channel_id` (string, optional): Filter by parent channel ID
  - `include_private` (boolean, optional, default=false): Whether to include private threads
  - `include_archived` (boolean, optional, default=false): Whether to include archived threads
- **Returns**: List of threads with their details
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "threads": [
      {
        "id": "111222333444555666",
        "name": "Discussion Thread",
        "parent_id": "222333444555666777",
        "owner_id": "123456789012345678",
        "message_count": 42,
        "member_count": 5,
        "created_at": "2023-01-01T00:00:00Z",
        "archived": false,
        "auto_archive_duration": 1440
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: View Channels

### `discord_create_thread`

- **Description**: Create a new thread in a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `name` (string, required): Thread name
  - `message_id` (string, optional): Message ID to create thread from (for forum posts)
  - `auto_archive_duration` (integer, optional, default=1440): Minutes until auto-archive (60, 1440, 4320, 10080)
  - `type` (string, optional, default="public"): Thread type ("public", "private", "announcement")
  - `invitable` (boolean, optional, default=true): Whether non-moderators can invite others
- **Returns**: Thread details
- **Example Response**:

  ```json
  {
    "id": "111222333444555666",
    "name": "Discussion Thread",
    "parent_id": "222333444555666777",
    "owner_id": "123456789012345678",
    "created_at": "2023-01-01T00:00:00Z",
    "archived": false,
    "auto_archive_duration": 1440
  }
  ```

- **Permissions**: Create Public Threads or Create Private Threads

### `discord_add_user_to_thread`

- **Description**: Add a user to a thread
- **Parameters**:
  - `thread_id` (string, required): Discord thread ID
  - `user_id` (string, required): Discord user ID
- **Returns**: Confirmation of addition
- **Example Response**:

  ```json
  {
    "success": true,
    "thread_id": "111222333444555666",
    "user_id": "123456789012345678"
  }
  ```

- **Permissions**: Manage Threads or thread ownership

### `discord_close_thread`

- **Description**: Close (archive) a thread
- **Parameters**:
  - `thread_id` (string, required): Discord thread ID
  - `lock` (boolean, optional, default=false): Whether to lock the thread as well
  - `reason` (string, optional): Reason for closing the thread
- **Returns**: Confirmation of closure
- **Example Response**:

  ```json
  {
    "success": true,
    "thread_id": "111222333444555666",
    "archived": true,
    "locked": false
  }
  ```

- **Permissions**: Manage Threads or thread ownership
