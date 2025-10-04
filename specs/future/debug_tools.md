# Debug and Control Tools

This document specifies the debugging and control tools for the Discord MCP server.

## Tool Control Tools

### `discord_enable_tool`

- **Description**: Enable a previously disabled tool
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `tool_name` (string, required): Name of the tool to enable
  - `reason` (string, optional): Reason for enabling
- **Returns**: Tool status
- **Example Response**:

  ```json
  {
    "success": true,
    "tool_name": "discord_send_message",
    "status": "enabled",
    "guild_id": "111222333444555666",
    "reason": "Feature testing complete"
  }
  ```

- **Permissions**: Administrator or Bot Owner

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

- **Permissions**: Administrator or Bot Owner

## Testing Tools

### `discord_test_tool`

- **Description**: Run a dry call and log output without executing
- **Parameters**:
  - `tool_name` (string, required): Name of the tool to test
  - `parameters` (object, required): Parameters to pass to the tool
  - `log_to_channel` (string, optional): Channel ID to log output to
  - `validate_only` (boolean, optional, default=true): Whether to only validate parameters without simulating execution
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
    "would_succeed": true,
    "permission_check": {
      "has_permission": true,
      "required_permissions": ["SEND_MESSAGES"]
    }
  }
  ```

- **Permissions**: Administrator or Bot Owner

### `discord_validate_permissions`

- **Description**: Validate if the bot has required permissions for a tool
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `tool_name` (string, required): Name of the tool to check
  - `channel_id` (string, optional): Channel ID to check permissions in
- **Returns**: Permission validation results
- **Example Response**:

  ```json
  {
    "tool_name": "discord_send_message",
    "guild_id": "111222333444555666",
    "channel_id": "111222333444555666",
    "has_permission": true,
    "required_permissions": ["SEND_MESSAGES"],
    "missing_permissions": []
  }
  ```

- **Permissions**: Administrator or Bot Owner

## Diagnostic Tools

### `discord_system_info`

- **Description**: Get detailed system information about the MCP server
- **Parameters**:
  - `include_memory` (boolean, optional, default=true): Whether to include memory usage
  - `include_tools` (boolean, optional, default=true): Whether to include tool statistics
  - `include_sessions` (boolean, optional, default=false): Whether to include active session information
- **Returns**: System information
- **Example Response**:

  ```json
  {
    "version": "1.0.0",
    "uptime": 86400,
    "platform": "Linux",
    "python_version": "3.10.4",
    "memory_usage": {
      "total": 512000000,
      "used": 128000000,
      "percent": 25.0
    },
    "tool_stats": {
      "total_tools": 25,
      "enabled_tools": 24,
      "disabled_tools": 1,
      "most_used": "discord_send_message"
    },
    "active_sessions": 5,
    "database_size": 1024000
  }
  ```

- **Permissions**: Bot Owner

### `discord_error_logs`

- **Description**: Get recent error logs from the MCP server
- **Parameters**:
  - `limit` (integer, optional, default=10): Maximum number of errors to retrieve
  - `include_stack_traces` (boolean, optional, default=false): Whether to include stack traces
  - `error_type` (string, optional): Filter by error type
- **Returns**: Error logs
- **Example Response**:

  ```json
  {
    "errors": [
      {
        "timestamp": "2023-01-01T00:00:00Z",
        "error_type": "PermissionError",
        "message": "Missing required permission: SEND_MESSAGES",
        "tool_name": "discord_send_message",
        "guild_id": "111222333444555666",
        "stack_trace": "..."
      }
    ],
    "count": 1
  }
  ```

- **Permissions**: Bot Owner
