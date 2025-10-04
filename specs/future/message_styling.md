# Message Style System

## Overview

The Message Style System allows users to define, store, and apply different message styles based on server, channel, or message type. This enables consistent formatting across messages while personalizing communication for different communities.

## Core Concepts

### Style Definitions

A style defines how messages should be formatted, including:

- **Structure**: Overall message layout (headings, sections, footers)
- **Tone**: Communication style (formal, casual, energetic, serious)
- **Formatting**: Use of markdown, emojis, and text decoration
- **Components**: Standard elements to include (timestamps, signatures, etc.)

### Style Contexts

Styles can be applied based on different contexts:

- **Server-specific**: Different styles for different Discord servers
- **Channel-specific**: Different styles for different channels within a server
- **Message-type**: Different styles for different types of messages (announcements, questions, etc.)
- **Role-specific**: Different styles when addressing specific roles

### Style Templates

Templates are pre-defined structures for common message types:

- **Announcement Template**: For important server announcements
- **Event Template**: For event notifications
- **Question Template**: For asking questions
- **Welcome Template**: For welcoming new members
- **Custom Templates**: User-defined templates for specific needs

## Data Model

### Style Definition

```json
{
  "style_id": "gaming_announcement",
  "name": "Gaming Server Announcement",
  "description": "Energetic style for gaming server announcements",
  "tone": "energetic",
  "emoji_level": "high",
  "structure": {
    "header": "# 🎮 {title} 🎮",
    "intro": "Hey @everyone! Get ready for {intro_text}!",
    "body": "{body}",
    "sections": ["## {section_title}", "{section_content}"],
    "footer": "**{call_to_action}** | Posted by {author}"
  },
  "emoji_map": {
    "time": "⏰",
    "location": "📍",
    "prize": "🏆",
    "info": "ℹ️",
    "warning": "⚠️"
  },
  "formatting_rules": {
    "use_bold_for_emphasis": true,
    "use_italics_for_quotes": true,
    "capitalize_headings": true,
    "use_code_blocks_for_commands": true
  }
}
```

### Style Context Mapping

```json
{
  "server_styles": {
    "123456789012345678": {
      "default": "professional_default",
      "announcements": "professional_announcement",
      "events": "professional_event"
    },
    "876543210987654321": {
      "default": "gaming_default",
      "announcements": "gaming_announcement",
      "events": "gaming_event"
    }
  },
  "channel_styles": {
    "111222333444555666": "professional_announcement",
    "222333444555666777": "casual_discussion"
  },
  "message_type_styles": {
    "announcement": "professional_announcement",
    "question": "helpful_question",
    "welcome": "friendly_welcome"
  }
}
```

## Features

### 1. Style Creation and Management

Users can create, edit, and delete styles:

```
User: Create a new announcement style for the Bootcamp server with a professional tone

System: I'll help you create a new announcement style. Let's define the key elements:

1. What would you like to name this style?

User: Bootcamp Professional Announcement

System: Great! Now let's define the structure:

1. How should the header look? (Use {title} as a placeholder for the announcement title)

User: # 📢 ANNOUNCEMENT: {title}

System: How about the introduction? (Use {intro_text} as a placeholder)

User: We're pleased to announce {intro_text}.

System: How should the main body be formatted?

User: {body}

System: Would you like to include any standard sections? (e.g., Details, Next Steps)

User: Yes, "Details" and "Next Steps"

System: How should the footer look?

User: If you have any questions, please ask in #help-desk.

System: I've created the "Bootcamp Professional Announcement" style with a professional tone. Here's a preview:

# 📢 ANNOUNCEMENT: {title}

We're pleased to announce {intro_text}.

{body}

## Details
{details}

## Next Steps
{next_steps}

If you have any questions, please ask in #help-desk.

Would you like to save this style?

User: Yes, save it

System: Style "Bootcamp Professional Announcement" has been saved and is now available for use in the Bootcamp server.
```

### 2. Style Application

Users can apply styles to their messages:

```
User: Send an announcement to the Bootcamp server about the new JavaScript course starting next week, use the professional style

System: I'll create an announcement using the "Bootcamp Professional Announcement" style. Please provide:

1. Announcement title:

User: JavaScript Fundamentals Course Launch

System: Introduction text:

User: our new JavaScript Fundamentals course will be starting next Monday

System: Main body content:

User: This 6-week course will cover all the basics of JavaScript programming, from variables and functions to DOM manipulation and async programming. The course is suitable for beginners with some prior programming experience.

System: Details:

User: Start date: Monday, July 28, 2025
Duration: 6 weeks
Schedule: Mon & Wed, 7-9pm EST
Instructor: Jane Smith

System: Next steps:

User: Register for the course by filling out the form in #registration by this Friday. Course materials will be distributed over the weekend.

System: I'll send the following announcement to the Bootcamp server using the professional style:

# 📢 ANNOUNCEMENT: JavaScript Fundamentals Course Launch

We're pleased to announce our new JavaScript Fundamentals course will be starting next Monday.

This 6-week course will cover all the basics of JavaScript programming, from variables and functions to DOM manipulation and async programming. The course is suitable for beginners with some prior programming experience.

## Details
Start date: Monday, July 28, 2025
Duration: 6 weeks
Schedule: Mon & Wed, 7-9pm EST
Instructor: Jane Smith

## Next Steps
Register for the course by filling out the form in #registration by this Friday. Course materials will be distributed over the weekend.

If you have any questions, please ask in #help-desk.

Which channel should I post this in?

User: #course-announcements

System: I've posted the announcement to #course-announcements in the Bootcamp server.
```

### 3. Style Inference

The system can infer the appropriate style based on context:

```
User: Announce the weekend gaming tournament in the Gaming Community server

System: [Internally processes]
- Intent: send_announcement
- Server: "Gaming Community"
- Content: "weekend gaming tournament"
- Style: Infers "gaming_announcement" style based on server and message type

System: I'll create an announcement about the weekend gaming tournament using the energetic style for the Gaming Community server. Please provide:

1. Tournament title:

User: ULTIMATE WEEKEND SHOWDOWN

System: Introduction text:

User: our biggest tournament of the month with awesome prizes

System: [Continues collecting information and applies the gaming_announcement style]
```

### 4. Style Sharing and Import/Export

Users can share styles between servers or export/import them:

````
User: Export my Bootcamp announcement style

System: Here's the exported style for "Bootcamp Professional Announcement":

```json
{
  "style_id": "bootcamp_professional_announcement",
  "name": "Bootcamp Professional Announcement",
  "description": "Professional style for bootcamp announcements",
  "tone": "professional",
  "emoji_level": "medium",
  "structure": {
    "header": "# 📢 ANNOUNCEMENT: {title}",
    "intro": "We're pleased to announce {intro_text}.",
    "body": "{body}",
    "sections": [
      "## Details",
      "{details}",
      "## Next Steps",
      "{next_steps}"
    ],
    "footer": "If you have any questions, please ask in #help-desk."
  },
  "emoji_map": {
    "time": "🕒",
    "location": "📍",
    "info": "ℹ️",
    "warning": "⚠️"
  },
  "formatting_rules": {
    "use_bold_for_emphasis": true,
    "use_italics_for_quotes": true,
    "capitalize_headings": true,
    "use_code_blocks_for_code": true
  }
}
``

You can save this JSON and import it into another server or share it with others.

User: Import this style to my Friend Group server

System: I've imported the "Bootcamp Professional Announcement" style to your Friend Group server. Would you like to rename it for this server?

User: Yes, call it "Friend Group Announcement"

System: The style has been renamed to "Friend Group Announcement" and is now available for use in the Friend Group server.

````

### 5. Style Learning

The system can learn from examples:

```

User: Learn a new announcement style from this example:

# 🌟 NEW FEATURE ALERT 🌟

Hey team!

We've just launched an AMAZING new feature that you're going to LOVE:

## What's New

- Feature point 1
- Feature point 2
- Feature point 3

## How to Use It

1. Step one
2. Step two
3. Step three

Give it a try and let us know what you think in #feedback!

System: I've analyzed this example and created a new style. What would you like to name it?

User: Product Update Style

System: I've created "Product Update Style" with the following characteristics:

- Tone: Enthusiastic and energetic
- Structure: Title with star emojis, friendly intro, "What's New" section with bullet points, "How to Use It" section with numbered steps, call to action at the end
- Emoji usage: Medium-high
- Formatting: All caps for emphasis words, bullet points for features, numbered steps for instructions

Would you like to associate this style with a specific server or message type?

User: Associate it with the Project Team server for product updates

System: I've associated the "Product Update Style" with the Project Team server for product update announcements. You can now use it by saying something like "Send a product update about the new search feature to the Project Team server."

```

## Integration with Server Registry

The Message Style System integrates with the Server Registry:

1. **Style Storage**: Styles are stored in the registry alongside server information
2. **Context Mapping**: Styles are mapped to servers, channels, and message types
3. **Permission Awareness**: Style application respects the bot's formatting permissions
4. **Dynamic Updates**: Styles are updated when the registry is refreshed

## Implementation Considerations

### Storage Options

1. **In-Registry Storage**:

   - Store styles directly in the Server Registry
   - Efficient for server-specific styles
   - Limited by registry size

2. **Separate Style Repository**:
   - Store styles in a dedicated repository
   - Better for sharing styles across servers
   - More complex implementation

### Style Application Process

1. **Template Filling**:

   - Replace placeholders with actual content
   - Apply formatting rules
   - Add appropriate emojis

2. **Permission Checking**:

   - Verify the bot can use rich text formatting
   - Fall back to simpler formatting if needed

3. **Preview Generation**:
   - Show users how their message will look before sending
   - Allow for last-minute adjustments

### Style Selection Algorithm

1. **Priority Order**:

   - Check for explicit style request
   - Check channel-specific style
   - Check message-type style for the server
   - Check server default style
   - Fall back to global default style

2. **Context Awareness**:
   - Consider recent style usage
   - Consider message content and purpose
   - Consider target audience

## Example Styles

### Professional Announcement Style

```

# 📢 ANNOUNCEMENT: {title}

We're pleased to announce {intro_text}.

{body}

## Details

{details}

## Next Steps

{next_steps}

If you have any questions, please contact {contact_person}.

```

### Energetic Gaming Announcement Style

```

# 🎮 {title} 🎮

HEY @everyone! GET HYPED FOR {intro_text}!!

{body}

## 🏆 DETAILS 🏆

{details}

## 🚀 JOIN IN 🚀

{join_instructions}

LET'S GOOOOO! 🔥🔥🔥

```

### Friendly Welcome Style

```

# 👋 Welcome to {server_name}, {new_member}!

We're so happy to have you join our community!

## 📚 About Us

{server_description}

## 🧭 Getting Started

{getting_started}

## 🤝 Community Guidelines

{guidelines}

If you have any questions, feel free to ask in {help_channel}!

```

### Minimalist Update Style

```

**Update: {title}**

{body}

---

Posted: {timestamp}

```

## Next Steps

1. Implement the Style Definition data structure
2. Create the Style Context Mapping system
3. Develop the Style Application process
4. Build the Style Management interface
5. Integrate with the Server Registry
6. Add Style Learning capabilities

---
