# Member Management Tools

This document specifies the member management tools for the Discord MCP server.

## Member Information Tools

### `discord_export_members`

- **Description**: Export server members with filtering options
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `include_roles` (boolean, optional, default=true): Whether to include role information
  - `format` (string, optional, default="json"): Output format ("json" or "csv")
  - `filter` (object, optional): Filter criteria for members
    - `role_id` (string, optional): Filter by role ID
    - `joined_after` (string, optional): ISO timestamp to filter by join date
    - `joined_before` (string, optional): ISO timestamp to filter by join date
    - `has_introduction` (boolean, optional): Filter to members who posted introductions
- **Returns**: List of members with their details
- **Example Response**:

  ```json
  {
    "format": "json",
    "data": [
      {
        "id": "123456789012345678",
        "name": "Username",
        "display_name": "Display Name",
        "joined_at": "2023-01-01T00:00:00Z",
        "bot": false,
        "roles": [{ "id": "987654321098765432", "name": "Role Name" }]
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Manage Server or Manage Roles

### `discord_member_analysis`

- **Description**: Analyze a specific member's activity and interests
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `days_to_analyze` (integer, optional, default=30): Number of days of history to analyze
  - `include_messages` (boolean, optional, default=false): Whether to include message samples
- **Returns**: Topics of interest, activity patterns, engagement metrics
- **Example Response**:

  ```json
  {
    "user_id": "123456789012345678",
    "username": "Username",
    "topics_of_interest": ["programming", "gaming", "music"],
    "active_channels": [
      {
        "channel_id": "111222333444555666",
        "name": "general",
        "message_count": 42
      }
    ],
    "activity_pattern": {
      "most_active_days": ["Monday", "Wednesday"],
      "most_active_hours": ["18:00-20:00 UTC"]
    },
    "engagement_metrics": {
      "messages_per_day": 5.2,
      "reactions_given": 15,
      "reactions_received": 30
    }
  }
  ```

- **Permissions**: Manage Server or Manage Roles

### `discord_new_members`

- **Description**: Get list of recently joined members
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `days` (integer, optional, default=7): Timeframe in days
  - `include_messages` (boolean, optional, default=false): Whether to include intro messages
  - `sort_by` (string, optional, default="joined_at"): Sort field ("joined_at", "username")
  - `sort_order` (string, optional, default="desc"): Sort order ("asc", "desc")
- **Returns**: New members with join dates and optional intro messages
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "timeframe_days": 7,
    "new_members": [
      {
        "id": "123456789012345678",
        "name": "Username",
        "joined_at": "2023-01-01T00:00:00Z",
        "intro_message": "Hello everyone! Excited to be here!"
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Manage Server or Manage Roles

## Member Database Tools

### `discord_sync_members`

- **Description**: Synchronize server members with the database (admin only)
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `intro_channel_id` (string, optional): Channel ID where introductions are posted
  - `days_to_scan` (integer, optional, default=30): Number of days of history to scan for introductions
  - `force_update` (boolean, optional, default=false): Whether to force update existing records
- **Returns**: Summary of sync operation
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "members_added": 42,
    "members_updated": 15,
    "intros_found": 28,
    "success": true
  }
  ```

- **Permissions**: Administrator

### `discord_store_member_info`

- **Description**: Store or update information about a specific member
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `interests` (array, optional): Array of interest topics
    - Each item is an object with `topic` (string) and `confidence` (float, 0-1)
  - `notes` (string, optional): Additional notes about the member
  - `tags` (array, optional): Array of tags to associate with the member
- **Returns**: Confirmation of storage
- **Example Response**:

  ```json
  {
    "success": true,
    "user_id": "123456789012345678",
    "stored_interests": ["programming", "gaming", "music"],
    "updated_at": "2023-01-01T00:00:00Z"
  }
  ```

- **Permissions**: Manage Roles

### `discord_get_member_info`

- **Description**: Retrieve stored information about a specific member
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `include_messages` (boolean, optional, default=false): Whether to include message samples
  - `include_activity` (boolean, optional, default=true): Whether to include activity metrics
- **Returns**: Member information from database
- **Example Response**:

  ```json
  {
    "user_id": "123456789012345678",
    "username": "Username",
    "display_name": "Display Name",
    "joined_at": "2023-01-01T00:00:00Z",
    "interests": [
      { "topic": "programming", "confidence": 0.95 },
      { "topic": "gaming", "confidence": 0.85 },
      { "topic": "music", "confidence": 0.75 }
    ],
    "intro_message": "Hello everyone! I'm a developer who loves gaming and music.",
    "last_active": "2023-01-10T00:00:00Z",
    "activity_summary": {
      "messages_last_30d": 125,
      "reactions_given_30d": 45,
      "reactions_received_30d": 67
    }
  }
  ```

- **Permissions**: Manage Roles

### `discord_clean_inactive_members`

- **Description**: Identify or tag inactive members for review
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `days_inactive` (integer, optional, default=30): Number of days of inactivity
  - `action` (string, optional, default="report"): Action to take ("report", "tag", "remove")
  - `exclude_roles` (array, optional): Array of role IDs to exclude from cleaning
- **Returns**: List of inactive members and actions taken
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "inactive_members": [
      {
        "id": "123456789012345678",
        "name": "Username",
        "last_active": "2023-01-01T00:00:00Z",
        "days_inactive": 45,
        "action_taken": "tagged"
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Administrator
