# Server Registry and Natural Language Command System

## Overview

The Server Registry and Natural Language Command System enables users to interact with Discord servers using natural language rather than rigid command formats. It maintains a registry of servers, channels, roles, and permissions that the bot has access to, allowing users to refer to these entities by friendly names rather than IDs.

## Use Cases

1. **Multi-Server Management**: Users can manage multiple Discord servers through a single interface
2. **Permission-Aware Operations**: The system respects the bot's permission level in each server
3. **Natural Language Commands**: Users can issue commands in natural language without memorizing syntax
4. **Context-Aware Interactions**: The system understands context from previous interactions
5. **Dynamic Updates**: The registry updates when changes occur in Discord servers

## Example Scenarios

### Scenario 1: Admin with Full Permissions

- User has a bot with admin permissions in "Coding Bootcamp" server
- User says: "Send an announcement in the bootcamp server that we're going live in 20 minutes"
- System identifies "bootcamp server" as "Coding Bootcamp"
- System identifies "announcement" should go to the #announcements channel
- System formats the message appropriately for an announcement
- System sends the message with proper formatting

### Scenario 2: Limited Permissions

- User has a bot with limited permissions in "Gaming Community" server
- User says: "Create a new role called 'Event Organizer' in the gaming server"
- System identifies "gaming server" as "Gaming Community"
- System checks permissions and finds the bot cannot create roles
- System informs the user that the bot lacks permission to create roles

### Scenario 3: Multiple Servers with Similar Channels

- User has a bot in both "Study Group" and "Book Club" servers, both with #general channels
- User says: "Send a message in the book club's general channel asking about the next meeting"
- System identifies "book club" as "Book Club" server
- System identifies "general channel" as the #general channel in that specific server
- System sends the message to the correct #general channel

### Scenario 4: Role Mentions

- User says: "Ping the Korean Study Group about today's session"
- System identifies "Korean Study Group" as a role
- System determines which server contains this role
- System sends a message mentioning the role in an appropriate channel

### Scenario 5: Dynamic Updates

- An admin adds a new channel to a server through Discord directly
- User says: "Update my server registry"
- System refreshes its knowledge of all servers, channels, and roles
- System confirms the update and mentions new entities discovered

## System Components

### 1. Server Registry

The Server Registry maintains information about all Discord servers the bot has access to, including:

- Server (Guild) information:

  - ID
  - Name
  - Aliases/friendly names
  - Description
  - Icon URL
  - Owner ID
  - Creation date

- Channel information for each server:

  - ID
  - Name
  - Type (text, voice, category, forum, etc.)
  - Topic
  - Position
  - Parent category
  - Permissions
  - Aliases/friendly names

- Role information for each server:

  - ID
  - Name
  - Color
  - Position
  - Permissions
  - Mentionable status
  - Aliases/friendly names

- Permission information for the bot:
  - Admin status
  - Channel-specific permissions
  - Role management permissions
  - Message management permissions
  - etc.

### 2. Natural Language Command Processor

The Natural Language Command Processor interprets user queries and extracts:

- Command intent (send message, get info, create role, etc.)
- Target server (by name, alias, or context)
- Target channel (by name, alias, or context)
- Target role (by name, alias, or context)
- Message content or other parameters
- Formatting preferences

### 3. Server Onboarding System

The Server Onboarding System initializes the registry when:

- The bot is first added to a server
- A manual refresh is requested
- Periodic automatic updates occur

During onboarding, the system:

1. Fetches all accessible servers
2. For each server:
   - Retrieves all channels and their details
   - Retrieves all roles and their details
   - Determines the bot's permissions
   - Generates aliases for servers, channels, and roles
   - Stores everything in the registry

### 4. Permission Checker

The Permission Checker verifies whether the bot has permission to perform requested actions:

- Checks server-wide permissions
- Checks channel-specific permissions
- Checks role hierarchy for role management
- Returns detailed permission information for error handling

### 5. Context Manager

The Context Manager maintains conversation context:

- Tracks recently mentioned servers, channels, and roles
- Resolves ambiguous references based on context
- Maintains conversation history for reference resolution
- Handles follow-up commands that rely on previous context

### 6. Message Style System

The Message Style System manages formatting preferences:

- Stores server-specific message styles
- Maintains templates for different message types
- Applies appropriate formatting based on context
- Learns from examples provided by users
- Adapts tone and style based on server culture

## Data Models

### Server Entry

```json
{
  "id": "123456789012345678",
  "name": "Coding Bootcamp",
  "aliases": ["bootcamp", "coding bootcamp", "bootcamp server"],
  "description": "A community for coding bootcamp students",
  "icon_url": "https://cdn.discordapp.com/icons/123456789012345678/abcdef.png",
  "owner_id": "876543210987654321",
  "created_at": "2023-01-01T00:00:00Z",
  "channels": {
    "111222333444555666": {
      "id": "111222333444555666",
      "name": "announcements",
      "aliases": ["announcement", "announcements channel", "announce"],
      "type": "text",
      "topic": "Important announcements for the bootcamp",
      "position": 0,
      "parent_id": null,
      "permissions": {
        "can_view": true,
        "can_send": true,
        "can_embed": true,
        "can_attach": true,
        "can_mention_everyone": false
      }
    }
  },
  "roles": {
    "222333444555666777": {
      "id": "222333444555666777",
      "name": "Instructor",
      "aliases": ["teacher", "instructor role", "teachers"],
      "color": 16711680,
      "position": 5,
      "permissions": ["ADMINISTRATOR"],
      "mentionable": true
    }
  },
  "bot_permissions": {
    "is_admin": false,
    "can_manage_channels": true,
    "can_manage_roles": false,
    "can_manage_messages": true,
    "can_mention_everyone": false
  },
  "styles": {
    "default": "professional_default",
    "announcements": "professional_announcement",
    "events": "professional_event",
    "welcome": "friendly_welcome",
    "channels": {
      "111222333444555666": "professional_announcement"
    }
  }
}
```

## Implementation Considerations

### Storage Options

1. **In-Memory Storage**:

   - Fast access
   - Lost on restart
   - Suitable for development or small-scale use

2. **JSON File Storage**:

   - Persistent across restarts
   - Easy to inspect and modify
   - Suitable for medium-scale use

3. **Database Storage**:
   - Fully persistent
   - Scalable to many servers
   - Suitable for production use

### Alias Generation

The system should generate aliases automatically:

1. **Server Aliases**:

   - Original name
   - Name without "server" suffix (if present)
   - Name with "server" suffix (if not present)
   - Common abbreviations (e.g., "CS" for "Computer Science")

2. **Channel Aliases**:

   - Original name
   - Name without "channel" suffix (if present)
   - Name with "channel" suffix (if not present)
   - Purpose-based aliases (e.g., "announce" for "announcements")

3. **Role Aliases**:
   - Original name
   - Name without "role" suffix (if present)
   - Name with "role" suffix (if not present)
   - Plural forms (e.g., "moderators" for "moderator")

### Update Mechanisms

1. **Manual Updates**:

   - User command: "Update server registry"
   - User command: "Refresh server info"

2. **Event-Based Updates**:

   - Discord events (channel created, role added, etc.)
   - Periodic background refresh (every 24 hours)
   - On-demand refresh when a command fails due to outdated info

3. **Partial Updates**:
   - Update only changed entities
   - Minimize API calls to Discord

### Error Handling

1. **Permission Errors**:

   - Clear explanation of missing permissions
   - Suggestions for alternative approaches

2. **Ambiguity Resolution**:

   - Ask for clarification when names are ambiguous
   - Provide options for the user to choose from

3. **Not Found Errors**:
   - Suggest similar names that do exist
   - Offer to refresh the registry

## Example Interactions

### Example 1: Sending a Message

```
User: Send a message in the announcements channel of the coding bootcamp saying "Workshop starts in 30 minutes!"

System: [Internally processes]
- Intent: send_message
- Server: "coding bootcamp" → Guild ID 123456789012345678
- Channel: "announcements" → Channel ID 111222333444555666
- Message: "Workshop starts in 30 minutes!"
- Permissions: Can send messages to this channel? Yes

System: I've sent your message to the #announcements channel in Coding Bootcamp server.
```

### Example 2: Permission Error

```
User: Create a new role called "Workshop Participant" in the gaming server

System: [Internally processes]
- Intent: create_role
- Server: "gaming server" → Guild ID 444555666777888999
- Role name: "Workshop Participant"
- Permissions: Can manage roles? No

System: I don't have permission to create roles in the Gaming Community server. You'll need to give the bot the "Manage Roles" permission or ask a server administrator to create this role.
```

### Example 3: Ambiguity Resolution

```
User: Send a message in general

System: [Internally processes]
- Intent: send_message
- Server: Not specified, user is in multiple servers
- Channel: "general" exists in multiple servers

System: I found #general channels in multiple servers. Which server would you like to send the message to?
1. Coding Bootcamp
2. Gaming Community
3. Book Club

User: Book Club

System: What message would you like to send to #general in the Book Club server?

User: Has anyone finished reading chapter 5?

System: I've sent your message to #general in the Book Club server.
```

## Next Steps

1. Implement the Server Registry data structure
2. Create the Server Onboarding System
3. Develop the Natural Language Command Processor
4. Build the Permission Checker
5. Implement the Context Manager
6. Integrate with existing Discord bot functionality
7. Add error handling and ambiguity resolution
8. Test with various scenarios and permission levels
