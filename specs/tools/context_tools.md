# Context Cache Tools

This document specifies the context cache tools for the Discord MCP server, which help AI assistants maintain context across conversations.

## Context Management Tools

### `discord_set_context_note`

- **Description**: Store a context note for a channel or thread
- **Parameters**:
  - `channel_id` (string, required): Discord channel or thread ID
  - `note` (string, required): Context note to store
  - `expires_after` (integer, optional): Seconds until the note expires (0 for no expiration)
  - `category` (string, optional, default="general"): Category for the note
  - `visibility` (string, optional, default="ai_only"): Who can see the note ("ai_only", "moderators", "everyone")
- **Returns**: Confirmation of storage
- **Example Response**:

  ```json
  {
    "success": true,
    "channel_id": "111222333444555666",
    "note_id": "abc123",
    "expires_at": "2023-01-02T00:00:00Z",
    "category": "general",
    "visibility": "ai_only"
  }
  ```

- **Permissions**: Send Messages in the channel

### `discord_get_context_summary`

- **Description**: Get a summary of context notes for a channel or thread
- **Parameters**:
  - `channel_id` (string, required): Discord channel or thread ID
  - `include_expired` (boolean, optional, default=false): Whether to include expired notes
  - `categories` (array, optional): Filter by categories
- **Returns**: Context notes and summary
- **Example Response**:

  ```json
  {
    "channel_id": "111222333444555666",
    "channel_name": "general",
    "notes": [
      {
        "id": "abc123",
        "content": "The team is discussing the new website design",
        "created_at": "2023-01-01T00:00:00Z",
        "expires_at": "2023-01-02T00:00:00Z",
        "category": "discussion_topic",
        "created_by": "123456789012345678"
      }
    ],
    "summary": "This channel is currently focused on website design discussions. The team is evaluating color schemes and layout options."
  }
  ```

- **Permissions**: View Channel

### `discord_delete_context_note`

- **Description**: Delete a specific context note
- **Parameters**:
  - `note_id` (string, required): ID of the note to delete
- **Returns**: Confirmation of deletion
- **Example Response**:

  ```json
  {
    "success": true,
    "note_id": "abc123",
    "channel_id": "111222333444555666"
  }
  ```

- **Permissions**: Manage Messages or note creator

## Conversation Memory Tools

### `discord_get_conversation_memory`

- **Description**: Retrieve conversation memory for a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `limit` (integer, optional, default=10): Maximum number of memory entries to retrieve
  - `include_system_notes` (boolean, optional, default=true): Whether to include system-generated notes
- **Returns**: Conversation memory entries
- **Example Response**:

  ```json
  {
    "channel_id": "111222333444555666",
    "memory_entries": [
      {
        "id": "mem123",
        "content": "User asked about the project deadline",
        "timestamp": "2023-01-01T00:00:00Z",
        "type": "user_query"
      },
      {
        "id": "mem124",
        "content": "The team agreed on extending the deadline to Friday",
        "timestamp": "2023-01-01T00:05:00Z",
        "type": "decision"
      }
    ],
    "count": 2
  }
  ```

- **Permissions**: View Channel

### `discord_store_conversation_memory`

- **Description**: Store an important point from the conversation in memory
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `content` (string, required): Memory content to store
  - `type` (string, optional, default="general"): Memory type ("general", "decision", "action_item", "question")
  - `importance` (integer, optional, default=5): Importance level (1-10)
- **Returns**: Confirmation of storage
- **Example Response**:

  ```json
  {
    "success": true,
    "channel_id": "111222333444555666",
    "memory_id": "mem125",
    "type": "decision",
    "importance": 8
  }
  ```

- **Permissions**: Send Messages in the channel

## Channel Topic Tools

### `discord_get_channel_topic_history`

- **Description**: Get the history of topics discussed in a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `days` (integer, optional, default=7): Number of days of history to retrieve
- **Returns**: Topic history with timestamps
- **Example Response**:

  ```json
  {
    "channel_id": "111222333444555666",
    "channel_name": "general",
    "topics": [
      {
        "name": "Website Redesign",
        "first_mentioned": "2023-01-01T00:00:00Z",
        "last_mentioned": "2023-01-01T02:00:00Z",
        "message_count": 45,
        "participants": 5
      },
      {
        "name": "Project Timeline",
        "first_mentioned": "2023-01-01T01:30:00Z",
        "last_mentioned": "2023-01-01T03:00:00Z",
        "message_count": 23,
        "participants": 4
      }
    ],
    "count": 2
  }
  ```

- **Permissions**: View Channel

### `discord_set_channel_topic`

- **Description**: Update the current topic for a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `topic` (string, required): New channel topic
  - `notify_members` (boolean, optional, default=false): Whether to send a notification about the topic change
- **Returns**: Confirmation of update
- **Example Response**:

  ```json
  {
    "success": true,
    "channel_id": "111222333444555666",
    "previous_topic": "General Discussion",
    "new_topic": "Website Redesign Planning",
    "updated_at": "2023-01-01T00:00:00Z"
  }
  ```

- **Permissions**: Manage Channels
