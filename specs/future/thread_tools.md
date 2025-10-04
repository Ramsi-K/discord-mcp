# Thread Management Tools

This document specifies the thread management tools for the Discord MCP server.

## Thread Creation and Management

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

### `discord_add_to_thread`

- **Description**: Add users to a thread
- **Parameters**:
  - `thread_id` (string, required): Discord thread ID
  - `user_ids` (array, required): Array of Discord user IDs to add
- **Returns**: Confirmation of addition
- **Example Response**:

  ```json
  {
    "success": true,
    "thread_id": "111222333444555666",
    "added_users": [
      { "id": "123456789012345678", "name": "Username1" },
      { "id": "234567890123456789", "name": "Username2" }
    ],
    "failed_users": []
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

## Thread Listing and Information

### `discord_list_threads`

- **Description**: List active threads in a channel or server
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `channel_id` (string, optional): Filter by parent channel ID
  - `include_private` (boolean, optional, default=false): Whether to include private threads
  - `include_archived` (boolean, optional, default=false): Whether to include archived threads
  - `sort_by` (string, optional, default="activity"): Sort method ("activity", "creation_date", "name")
  - `filter` (object, optional): Additional filters
    - `created_after` (string, optional): ISO timestamp to filter by creation date
    - `created_by` (string, optional): Filter by creator user ID
    - `has_member` (string, optional): Filter to threads with specific member
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
        "parent_name": "general",
        "owner_id": "123456789012345678",
        "message_count": 42,
        "member_count": 5,
        "created_at": "2023-01-01T00:00:00Z",
        "last_message_at": "2023-01-02T00:00:00Z",
        "archived": false,
        "auto_archive_duration": 1440
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: View Channels

### `discord_get_thread_members`

- **Description**: Get list of members in a thread
- **Parameters**:
  - `thread_id` (string, required): Discord thread ID
- **Returns**: List of members in the thread
- **Example Response**:

  ```json
  {
    "thread_id": "111222333444555666",
    "thread_name": "Discussion Thread",
    "members": [
      {
        "id": "123456789012345678",
        "name": "Username",
        "display_name": "Display Name",
        "joined_at": "2023-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: View Channels

### `discord_get_thread_activity`

- **Description**: Get activity statistics for a thread
- **Parameters**:
  - `thread_id` (string, required): Discord thread ID
  - `include_message_count` (boolean, optional, default=true): Whether to include message counts by user
- **Returns**: Thread activity statistics
- **Example Response**:

  ```json
  {
    "thread_id": "111222333444555666",
    "thread_name": "Discussion Thread",
    "created_at": "2023-01-01T00:00:00Z",
    "message_count": 42,
    "unique_authors": 5,
    "last_active": "2023-01-02T00:00:00Z",
    "top_contributors": [
      { "id": "123456789012345678", "name": "Username", "messages": 15 }
    ],
    "activity_by_day": {
      "2023-01-01": 20,
      "2023-01-02": 22
    }
  }
  ```

- **Permissions**: View Channels
