# Infrastructure and Admin Tools

This document specifies the infrastructure and admin tools for the Discord MCP server.

## Server Management Tools

### `discord_server_stats`

- **Description**: Get overall server statistics
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `include_growth` (boolean, optional, default=false): Whether to include growth metrics
  - `days_for_growth` (integer, optional, default=30): Number of days for growth calculation
- **Returns**: Member count, channel count, activity metrics
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "name": "Server Name",
    "member_count": 1000,
    "channel_count": 50,
    "role_count": 10,
    "created_at": "2023-01-01T00:00:00Z",
    "growth_metrics": {
      "members_joined_7d": 42,
      "members_left_7d": 5,
      "growth_rate": 3.7
    }
  }
  ```

- **Permissions**: View Server Insights

### `discord_create_event`

- **Description**: Create a server event
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `name` (string, required): Event name
  - `description` (string, required): Event description
  - `start_time` (string, required): Start time in ISO format
  - `end_time` (string, optional): End time in ISO format
  - `channel_id` (string, optional): Associated channel ID
  - `location` (string, optional): Event location
  - `image_url` (string, optional): URL to event image
- **Returns**: Event ID and link
- **Example Response**:

  ```json
  {
    "success": true,
    "event_id": "111222333444555666",
    "name": "Community Game Night",
    "start_time": "2023-01-01T18:00:00Z",
    "end_time": "2023-01-01T20:00:00Z",
    "url": "https://discord.gg/events/111222333444555666"
  }
  ```

- **Permissions**: Manage Events

## Logging and Monitoring Tools

### `discord_ping`

- **Description**: Health check for the MCP server and Discord connection
- **Parameters**:
  - `include_details` (boolean, optional, default=false): Whether to include detailed diagnostics
- **Returns**: Connection status and latency information
- **Example Response**:

  ```json
  {
    "status": "healthy",
    "discord_api_latency": 42,
    "mcp_server_uptime": 86400,
    "active_sessions": 5,
    "timestamp": "2023-01-01T00:00:00Z"
  }
  ```

- **Permissions**: None

### `discord_log_tool_usage`

- **Description**: Logs every tool call to a mod channel and DB (audit log style)
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `log_channel_id` (string, required): Channel ID to send logs to
  - `enabled` (boolean, optional, default=true): Whether to enable logging
  - `log_level` (string, optional, default="info"): Log level ("debug", "info", "warn", "error")
- **Returns**: Logging configuration status
- **Example Response**:

  ```json
  {
    "success": true,
    "guild_id": "111222333444555666",
    "log_channel_id": "111222333444555666",
    "enabled": true,
    "log_level": "info"
  }
  ```

- **Permissions**: Administrator

### `discord_get_tool_usage_logs`

- **Description**: Retrieve logs of tool usage
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `tool_name` (string, optional): Filter by tool name
  - `user_id` (string, optional): Filter by user ID
  - `start_time` (string, optional): Start time in ISO format
  - `end_time` (string, optional): End time in ISO format
  - `limit` (integer, optional, default=100): Maximum number of logs to retrieve
- **Returns**: Tool usage logs
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "logs": [
      {
        "id": "1",
        "tool_name": "discord_send_message",
        "user_id": "123456789012345678",
        "username": "Username",
        "channel_id": "111222333444555666",
        "parameters": {
          "channel_id": "111222333444555666",
          "message": "Hello world!"
        },
        "result_status": "success",
        "execution_time": 0.42,
        "timestamp": "2023-01-01T00:00:00Z"
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Administrator

## Tool Management Tools

### `discord_disable_tool`

- **Description**: Disable a specific tool
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `tool_name` (string, required): Name of the tool to disable
  - `reason` (string, optional): Reason for disabling
  - `duration` (integer, optional): Duration in seconds (0 for permanent)
- **Returns**: Tool status
- **Example Response**:

  ```json
  {
    "success": true,
    "tool_name": "discord_send_message",
    "status": "disabled",
    "guild_id": "111222333444555666",
    "disabled_until": "2023-01-02T00:00:00Z",
    "reason": "Maintenance"
  }
  ```

- **Permissions**: Administrator

### `discord_enable_tool`

- **Description**: Enable a previously disabled tool
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `tool_name` (string, required): Name of the tool to enable
- **Returns**: Tool status
- **Example Response**:

  ```json
  {
    "success": true,
    "tool_name": "discord_send_message",
    "status": "enabled",
    "guild_id": "111222333444555666"
  }
  ```

- **Permissions**: Administrator

### `discord_list_tools`

- **Description**: List all available tools and their status
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `category` (string, optional): Filter by tool category
  - `include_disabled` (boolean, optional, default=true): Whether to include disabled tools
- **Returns**: List of tools with their status
- **Example Response**:

  ```json
  {
    "guild_id": "111222333444555666",
    "tools": [
      {
        "name": "discord_send_message",
        "category": "channel",
        "description": "Send a message to a specific channel",
        "status": "enabled",
        "required_permissions": ["SEND_MESSAGES"]
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: None

## Debugging Tools

### `discord_test_tool_output`

- **Description**: Run a dry call and log output without executing
- **Parameters**:
  - `tool_name` (string, required): Name of the tool to test
  - `parameters` (object, required): Parameters to pass to the tool
  - `log_to_channel` (string, optional): Channel ID to log output to
- **Returns**: Simulated tool output
- **Example Response**:

  ```json
  {
    "tool_name": "discord_send_message",
    "parameters": {
      "channel_id": "111222333444555666",
      "message": "Hello world!"
    },
    "simulated_output": {
      "success": true,
      "message_id": "simulated_id",
      "channel_id": "111222333444555666",
      "timestamp": "2023-01-01T00:00:00Z"
    },
    "execution_time": 0.42,
    "would_succeed": true
  }
  ```

- **Permissions**: Administrator
