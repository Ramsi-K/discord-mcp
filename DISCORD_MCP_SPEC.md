# Discord MCP Server Specification

This document outlines the complete specification for the Discord MCP server implementation, including all tools, resources, and prompts.

## Overview

The Discord MCP server provides AI-assisted Discord server management capabilities through the Model Context Protocol (MCP). It allows AI assistants like Claude to interact with Discord servers through a set of well-defined tools, resources, and prompts.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│  Discord    │◄────┤  MCP Server │◄────┤  AI Client  │
│  Bot        │     │  (FastMCP)  │     │  (Claude)   │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

- **Discord Bot**: Interfaces with Discord API, has access to servers where it's been invited
- **MCP Server**: Implements the MCP protocol, provides tools, resources, and prompts
- **AI Client**: Consumes the MCP server's capabilities (Claude via Kiro IDE or other interfaces)

## Database Schema

### Member Database

The Discord MCP server maintains a database of server members and their information to enable persistent analysis and tracking.

#### Members Table

```sql
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    guild_id VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    joined_at TIMESTAMP,
    avatar_url TEXT,
    is_bot BOOLEAN DEFAULT FALSE,
    last_active TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, guild_id)
);
```

#### Member Interests Table

```sql
CREATE TABLE member_interests (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(member_id, topic)
);
```

#### Member Messages Table

```sql
CREATE TABLE member_messages (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    channel_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    content TEXT,
    timestamp TIMESTAMP NOT NULL,
    is_introduction BOOLEAN DEFAULT FALSE,
    analyzed BOOLEAN DEFAULT FALSE,
    UNIQUE(message_id)
);
```

#### Member Activity Table

```sql
CREATE TABLE member_activity (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    messages_sent INTEGER DEFAULT 0,
    reactions_given INTEGER DEFAULT 0,
    reactions_received INTEGER DEFAULT 0,
    channels_active INTEGER DEFAULT 0,
    UNIQUE(member_id, date)
);
```

## MCP Tools

### Member Management Tools

#### `discord_export_members`

- **Description**: Export server members with filtering options
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `include_roles` (boolean, optional, default=true): Whether to include role information
  - `format` (string, optional, default="json"): Output format ("json" or "csv")
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

#### `discord_member_analysis`

- **Description**: Analyze a specific member's activity and interests
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `days_to_analyze` (integer, optional, default=30): Number of days of history to analyze
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

#### `discord_new_members`

- **Description**: Get list of recently joined members
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `days` (integer, optional, default=7): Timeframe in days
  - `include_messages` (boolean, optional, default=false): Whether to include intro messages
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

#### `discord_sync_members`

- **Description**: Synchronize server members with the database (admin only)
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `intro_channel_id` (string, optional): Channel ID where introductions are posted
  - `days_to_scan` (integer, optional, default=30): Number of days of history to scan for introductions
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

#### `discord_store_member_info`

- **Description**: Store or update information about a specific member
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
  - `interests` (array, optional): Array of interest topics
  - `notes` (string, optional): Additional notes about the member
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

#### `discord_get_member_info`

- **Description**: Retrieve stored information about a specific member
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `user_id` (string, required): Discord user ID
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

### Channel Management Tools

#### `discord_channel_stats`

- **Description**: Get activity statistics for a channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `days` (integer, optional, default=7): Timeframe in days
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

#### `discord_send_message`

- **Description**: Send a message to a specific channel
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message` (string, required): Message content
  - `mention_everyone` (boolean, optional, default=false): Whether to mention @everyone
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

#### `discord_reaction_analytics`

- **Description**: Analyze reactions to a specific message
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `message_id` (string, required): Discord message ID
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

### Server Management Tools

#### `discord_server_stats`

- **Description**: Get overall server statistics
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `include_growth` (boolean, optional, default=false): Whether to include growth metrics
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

#### `discord_create_event`

- **Description**: Create a server event
- **Parameters**:
  - `guild_id` (string, required): Discord server/guild ID
  - `name` (string, required): Event name
  - `description` (string, required): Event description
  - `start_time` (string, required): Start time in ISO format
  - `end_time` (string, optional): End time in ISO format
  - `channel_id` (string, optional): Associated channel ID
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

## MCP Resources

### `discord://servers`

- **Description**: List all servers the bot has access to
- **MIME Type**: application/json
- **Returns**: Array of server objects with IDs and names
- **Example Response**:
  ```json
  [
    {
      "id": "111222333444555666",
      "name": "Server Name",
      "member_count": 1000,
      "icon_url": "https://cdn.discordapp.com/icons/111222333444555666/abcdef.png"
    }
  ]
  ```

### `discord://servers/{guild_id}`

- **Description**: Get detailed information about a specific server
- **MIME Type**: application/json
- **Returns**: Server details including channels, roles, etc.
- **Example Response**:
  ```json
  {
    "id": "111222333444555666",
    "name": "Server Name",
    "description": "Server Description",
    "member_count": 1000,
    "owner_id": "123456789012345678",
    "created_at": "2023-01-01T00:00:00Z",
    "icon_url": "https://cdn.discordapp.com/icons/111222333444555666/abcdef.png",
    "features": ["COMMUNITY", "NEWS"]
  }
  ```

### `discord://servers/{guild_id}/channels`

- **Description**: List all channels in a server
- **MIME Type**: application/json
- **Returns**: Array of channel objects with IDs and names
- **Example Response**:
  ```json
  [
    {
      "id": "111222333444555666",
      "name": "general",
      "type": "text",
      "topic": "General discussion",
      "position": 0,
      "parent_id": null
    }
  ]
  ```

### `discord://servers/{guild_id}/roles`

- **Description**: List all roles in a server
- **MIME Type**: application/json
- **Returns**: Array of role objects with IDs, names, and permissions
- **Example Response**:
  ```json
  [
    {
      "id": "111222333444555666",
      "name": "Admin",
      "color": 16711680,
      "position": 1,
      "permissions": ["ADMINISTRATOR"],
      "mentionable": true
    }
  ]
  ```

### `discord://servers/{guild_id}/members/{user_id}`

- **Description**: Get detailed information about a specific member
- **MIME Type**: application/json
- **Returns**: Member details including roles, join date, etc.
- **Example Response**:
  ```json
  {
    "id": "123456789012345678",
    "name": "Username",
    "display_name": "Display Name",
    "joined_at": "2023-01-01T00:00:00Z",
    "roles": [{ "id": "111222333444555666", "name": "Role Name" }],
    "avatar_url": "https://cdn.discordapp.com/avatars/123456789012345678/abcdef.png"
  }
  ```

## MCP Prompts

### `summarize_channel`

- **Description**: Generate a summary of recent channel activity
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `timeframe` (string, required): Timeframe to summarize (e.g., "24h", "7d")
- **Returns**: Structured summary of discussions and key points
- **Example Usage**:
  ```python
  messages = await mcp_client.get_prompt(
      "summarize_channel",
      {"channel_id": "111222333444555666", "timeframe": "24h"}
  )
  ```

### `analyze_member_interests`

- **Description**: Analyze a member's interests based on their messages
- **Parameters**:
  - `user_id` (string, required): Discord user ID
  - `guild_id` (string, required): Discord server/guild ID
- **Returns**: Analysis of topics and interests
- **Example Usage**:
  ```python
  messages = await mcp_client.get_prompt(
      "analyze_member_interests",
      {"user_id": "123456789012345678", "guild_id": "111222333444555666"}
  )
  ```

### `generate_welcome_message`

- **Description**: Create a personalized welcome message for a new member
- **Parameters**:
  - `user_id` (string, required): Discord user ID
  - `guild_id` (string, required): Discord server/guild ID
- **Returns**: Customized welcome message based on server context
- **Example Usage**:
  ```python
  messages = await mcp_client.get_prompt(
      "generate_welcome_message",
      {"user_id": "123456789012345678", "guild_id": "111222333444555666"}
  )
  ```

### `create_announcement`

- **Description**: Format an announcement with proper structure and emphasis
- **Parameters**:
  - `title` (string, required): Announcement title
  - `content` (string, required): Announcement content
  - `importance_level` (string, optional, default="medium"): Importance level ("low", "medium", "high")
- **Returns**: Formatted announcement ready to be posted
- **Example Usage**:
  ```python
  messages = await mcp_client.get_prompt(
      "create_announcement",
      {
          "title": "New Server Features",
          "content": "We've added several new features...",
          "importance_level": "high"
      }
  )
  ```

## Implementation Details

### Authentication & Security

- Bot-based authentication (users must invite the bot to their servers)
- Permission checking in each tool implementation
- Rate limiting to prevent abuse
- Audit logging of all tool usage

### Technical Architecture

- FastMCP server implementation
- Discord.py for Discord API interaction
- Async/await patterns for efficient processing
- Error handling and graceful degradation

### Deployment Strategy

- Packaged as a Python module for easy installation
- Configuration via environment variables
- Documentation for setup and usage

## Development Roadmap

1. **Phase 1: Core Infrastructure**

   - Set up FastMCP server
   - Implement Discord bot integration
   - Create basic server and channel tools

2. **Phase 2: Member Management**

   - Implement member export and analysis tools
   - Add new member tracking functionality

3. **Phase 3: Advanced Features**

   - Add event creation and management
   - Implement reaction analytics
   - Create prompts for content generation

4. **Phase 4: Security & Optimization**

   - Add comprehensive permission checking
   - Implement rate limiting
   - Optimize for performance

5. **Phase 5: Documentation & Distribution**
   - Complete user documentation
   - Package for distribution
   - Create setup guides
