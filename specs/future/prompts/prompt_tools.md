# Prompt Tools

This document specifies the prompt tools for the Discord MCP server.

## Channel Analysis Prompts

### `summarize_channel`

- **Description**: Generate a summary of recent channel activity
- **Parameters**:
  - `channel_id` (string, required): Discord channel ID
  - `timeframe` (string, required): Timeframe to summarize (e.g., "24h", "7d")
  - `focus` (string, optional): Focus area ("topics", "questions", "decisions", "all")
- **Returns**: Structured summary of discussions and key points
- **Example Usage**:

  ```python
  messages = await mcp_client.get_prompt(
      "summarize_channel",
      {"channel_id": "111222333444555666", "timeframe": "24h"}
  )
  ```

- **Example Response**:

  ```text
  # Channel Summary: #general (Last 24 hours)

  ## Main Topics
  - Project deadline discussion (most active, 45 messages)
  - New feature suggestions (15 messages)
  - Bug reports for the login system (10 messages)

  ## Key Points
  - Team agreed to extend the deadline to Friday
  - Three new feature ideas were proposed: dark mode, export functionality, and mobile notifications
  - Login bug appears to be related to the recent database migration

  ## Action Items
  - @username1 will create tickets for the new feature ideas
  - @username2 will investigate the login bug
  - Team meeting scheduled for tomorrow at 2pm to discuss progress

  ## Participation
  - 12 unique members participated
  - Most active: @username1 (23 messages), @username2 (15 messages)
  - Peak activity: 3-4pm (35 messages)
  ```

## Member Analysis Prompts

### `analyze_member_interests`

- **Description**: Analyze a member's interests based on their messages
- **Parameters**:
  - `user_id` (string, required): Discord user ID
  - `guild_id` (string, required): Discord server/guild ID
  - `days` (integer, optional, default=30): Number of days of history to analyze
- **Returns**: Analysis of topics and interests
- **Example Usage**:

  ```python
  messages = await mcp_client.get_prompt(
      "analyze_member_interests",
      {"user_id": "123456789012345678", "guild_id": "111222333444555666"}
  )
  ```

- **Example Response**:

  ```text
  # Member Interest Analysis: Username

  ## Primary Interests
  - Programming (high confidence)
    - Frequently discusses Python, JavaScript, and web development
    - Has shared code snippets in #coding channel
    - Mentioned working on a personal project using React

  - Gaming (medium confidence)
    - Participates in #gaming discussions, particularly about strategy games
    - Mentioned playing Civilization VI and Stellaris
    - Organized a community game night last month

  - Music (medium confidence)
    - Shares music recommendations in #music channel
    - Primarily interested in electronic and indie genres
    - Discussed attending a concert recently

  ## Engagement Pattern
  - Most active in #coding (45% of messages)
  - Regularly participates in #general and #gaming
  - Typically active on weekday evenings (7-10pm)
  - Often helps other members with technical questions

  ## Potential Connections
  - Strong overlap in interests with @username2 and @username3
  - Might be interested in the upcoming Python workshop
  - Could be a good candidate for the Code Reviewer role
  ```

## Welcome and Onboarding Prompts

### `generate_welcome_message`

- **Description**: Create a personalized welcome message for a new member
- **Parameters**:
  - `user_id` (string, required): Discord user ID
  - `guild_id` (string, required): Discord server/guild ID
  - `style` (string, optional, default="friendly"): Message style ("friendly", "formal", "brief")
- **Returns**: Customized welcome message based on server context
- **Example Usage**:

  ```python
  messages = await mcp_client.get_prompt(
      "generate_welcome_message",
      {"user_id": "123456789012345678", "guild_id": "111222333444555666"}
  )
  ```

- **Example Response**:

  ```text
  Welcome to our community, @Username! 👋

  We're excited to have you join us! Here's a quick guide to help you get started:

  🔹 Introduce yourself in #introductions
  🔹 Check out our rules in #server-info
  🔹 Get roles in #role-assignment

  Based on your profile, you might be interested in our #programming, #gaming, and #music channels.

  We have a community game night every Friday at 8pm UTC, and a coding workshop coming up next Tuesday!

  If you have any questions, feel free to ask in #help or tag our @Moderator team.

  Enjoy your time here! 😊
  ```

## Announcement Prompts

### `create_announcement`

- **Description**: Format an announcement with proper structure and emphasis
- **Parameters**:
  - `title` (string, required): Announcement title
  - `content` (string, required): Announcement content
  - `importance_level` (string, optional, default="medium"): Importance level ("low", "medium", "high")
  - `include_ping` (string, optional): Role to ping ("everyone", "here", or role name)
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

- **Example Response**:

  ```text
  # 📣 ANNOUNCEMENT: New Server Features

  @everyone

  ## 🚀 We've added several new features to the server!

  • **New Roles System**: Custom color roles are now available in #role-assignment
  • **Event Calendar**: Check out our new #events channel for upcoming community activities
  • **Improved Bots**: We've added several new utility bots to enhance your experience

  These changes are live now! Please report any issues to the mod team.

  ## 📅 Coming Soon

  We're also working on a new reputation system and community challenges for next month.

  ⭐ **Try out the new features and let us know what you think in #feedback!**
  ```

## Event Prompts

### `create_event_description`

- **Description**: Generate a formatted description for a server event
- **Parameters**:
  - `event_name` (string, required): Name of the event
  - `event_type` (string, required): Type of event ("gaming", "workshop", "discussion", "contest", "other")
  - `date_time` (string, required): Date and time of the event
  - `duration` (string, required): Duration of the event
  - `details` (string, required): Additional details about the event
- **Returns**: Formatted event description
- **Example Usage**:

  ```python
  messages = await mcp_client.get_prompt(
      "create_event_description",
      {
          "event_name": "Community Game Night",
          "event_type": "gaming",
          "date_time": "Friday, January 1, 2023 at 8:00 PM UTC",
          "duration": "2 hours",
          "details": "We'll be playing Among Us and Jackbox Party Pack games."
      }
  )
  ```

- **Example Response**:

  ```text
  # 🎮 Community Game Night

  **When**: Friday, January 1, 2023 at 8:00 PM UTC
  **Duration**: 2 hours
  **Where**: #gaming voice channel

  ## What to Expect

  Join us for a fun evening of games! We'll be playing:

  • Among Us (first hour)
  • Jackbox Party Pack games (second hour)

  ## How to Join

  1. Join the #gaming voice channel at the start time
  2. Make sure you have the games installed or can access Jackbox via stream
  3. React to this message with 🎮 if you plan to attend

  ## Requirements

  • Microphone recommended for Among Us
  • Mobile device or second screen helpful for Jackbox games
  • Good internet connection

  No experience necessary - we'll explain the rules before we start!

  See you there! 🎉
  ```
