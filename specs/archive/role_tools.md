# Role Management Tools

This document specifies the role management tools for the Discord MCP server.

## Role Information Tools

### `discord_list_roles`

- **Description**: List all roles in a server
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `include_permissions` (boolean, optional, default=true): Whether to include detailed permission information
  - `include_member_counts` (boolean, optional, default=true): Whether to include count of members with each role
- **Returns**: Array of role objects with IDs, names, and permissions
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "roles": [
      {
        "id": "111222333444555666",
        "name": "Admin",
        "color": 16711680,
        "position": 1,
        "permissions": ["ADMINISTRATOR"],
        "mentionable": true,
        "member_count": 5
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Manage Roles

## Role Creation Tools

### `discord_create_role`

- **Description**: Create a new role in a server
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `name` (string, required): Role name
  - `color` (integer, optional): Role color (RGB color integer)
  - `permissions` (array, optional): Array of permission strings
  - `mentionable` (boolean, optional, default=false): Whether the role is mentionable
  - `hoist` (boolean, optional, default=false): Whether the role is displayed separately in the member list
  - `position` (integer, optional): Position in the role hierarchy
- **Returns**: Created role details
- **Example Response**:

  ```json
  {
    "id": "111222333444555666",
    "name": "Moderator",
    "color": 3447003,
    "position": 2,
    "permissions": ["KICK_MEMBERS", "BAN_MEMBERS", "MANAGE_MESSAGES"],
    "mentionable": true,
    "hoist": true
  }
  ```

- **Permissions**: Manage Roles

## Role Assignment Tools

### `discord_assign_role`

- **Description**: Assign a role to a user
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `role_id` (string, required): Discord role ID
  - `reason` (string, optional): Reason for the role assignment
- **Returns**: Confirmation of assignment
- **Example Response**:

  ```json
  {
    "success": true,
    "guild_id": "111222333444555666",
    "user_id": "123456789012345678",
    "role_id": "111222333444555666",
    "role_name": "Moderator"
  }
  ```

- **Permissions**: Manage Roles

### `discord_assign_role_by_participation`

- **Description**: Assign a role to users who participated in a specific message or thread
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `role_id` (string, required): Discord role ID to assign
  - `participation_type` (string, required): Type of participation ("replied", "reacted", "posted")
  - `source` (object, required): Source of participation
    - `type` (string, required): Source type ("message", "thread")
    - `id` (string, required): Message ID or thread ID
    - `channel_id` (string, required for messages): Channel ID containing the message
    - `emoji` (string, optional): Specific emoji to filter by (for "reacted" type)
  - `dry_run` (boolean, optional, default=true): Whether to simulate the operation without making changes
  - `reason` (string, optional): Reason for the role assignment
- **Returns**: List of affected users and operation summary
- **Example Response**:

  ```json
  {
    "success": true,
    "guild_id": "111222333444555666",
    "role_id": "111222333444555666",
    "role_name": "Design Club",
    "participation_type": "reacted",
    "source": {
      "type": "message",
      "id": "111222333444555666",
      "channel_id": "111222333444555666",
      "emoji": "🎨"
    },
    "affected_users": [{ "id": "123456789012345678", "name": "Username" }],
    "count": 1,
    "dry_run": true
  }
  ```

- **Permissions**: Manage Roles

### `discord_bulk_assign_role_by_filter`

- **Description**: Assign a role to multiple users based on filter criteria
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `role_id` (string, required): Discord role ID
  - `filter` (object, required): Filter criteria
    - `has_roles` (array, optional): Array of role IDs users must have
    - `lacks_roles` (array, optional): Array of role IDs users must not have
    - `active_in_channel` (string, optional): Channel ID users must be active in
    - `joined_after` (string, optional): ISO timestamp for minimum join date
    - `joined_before` (string, optional): ISO timestamp for maximum join date
    - `reacted_to` (object, optional): Message reaction filter
      - `channel_id` (string, required): Channel ID containing the message
      - `message_id` (string, required): Message ID
      - `emoji` (string, required): Emoji to filter by
  - `dry_run` (boolean, optional, default=true): Whether to simulate the operation without making changes
  - `reason` (string, optional): Reason for the role assignment
- **Returns**: List of affected users and operation summary
- **Example Response**:

  ```json
  {
    "success": true,
    "guild_id": "111222333444555666",
    "role_id": "111222333444555666",
    "role_name": "Design Club",
    "affected_users": [{ "id": "123456789012345678", "name": "Username" }],
    "count": 1,
    "dry_run": true
  }
  ```

- **Permissions**: Manage Roles

### `discord_remove_role`

- **Description**: Remove a role from a user
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `role_id` (string, required): Discord role ID
  - `reason` (string, optional): Reason for the role removal
- **Returns**: Confirmation of removal
- **Example Response**:

  ```json
  {
    "success": true,
    "guild_id": "111222333444555666",
    "user_id": "123456789012345678",
    "role_id": "111222333444555666",
    "role_name": "Moderator"
  }
  ```

- **Permissions**: Manage Roles

### `discord_get_users_with_role`

- **Description**: Get all users with a specific role
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `role_id` (string, required): Discord role ID
  - `include_user_details` (boolean, optional, default=true): Whether to include detailed user information
- **Returns**: List of users with the role
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "role_id": "111222333444555666",
    "role_name": "Moderator",
    "users": [
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

- **Permissions**: Manage Roles
