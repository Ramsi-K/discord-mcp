# Resources, Templates, and Prompts System

## Overview

This document defines the complete resource system for Discord MCP workflows, including message templates, LLM prompts for intent parsing, and reusable configurations. This system enables consistent messaging, automated intent understanding, and maintainable community management patterns.

---

## Table of Contents

1. [Resource Structure](#resource-structure)
2. [Message Templates](#message-templates)
3. [LLM Prompts](#llm-prompts)
4. [Configuration Files](#configuration-files)
5. [Template Variables Reference](#template-variables-reference)
6. [Usage Patterns](#usage-patterns)

---

## Resource Structure

```
src/discord_mcp/resources/
├── campaign/
│   ├── templates/
│   │   ├── reminder_default.txt.j2
│   │   ├── reminder_tournament.txt.j2
│   │   ├── reminder_event.txt.j2
│   │   ├── reminder_meeting.txt.j2
│   │   ├── campaign_summary.txt.j2
│   │   └── optin_list.txt.j2
│   └── prompts/
│       ├── campaign_intent.yaml
│       └── template_suggestion.yaml
│
├── message/
│   ├── templates/
│   │   ├── announcement.txt.j2
│   │   ├── welcome_new_member.txt.j2
│   │   ├── rule_reminder.txt.j2
│   │   ├── event_announcement.txt.j2
│   │   ├── poll_create.txt.j2
│   │   ├── moderator_alert.txt.j2
│   │   ├── birthday_announcement.txt.j2
│   │   └── server_update.txt.j2
│   └── prompts/
│       ├── message_intent.yaml
│       └── mention_suggestion.yaml
│
├── discovery/
│   └── prompts/
│       ├── discovery_intent.yaml
│       └── entity_resolution.yaml
│
├── diagnostics/
│   └── templates/
│       ├── health_report.txt.j2
│       ├── permission_report.txt.j2
│       └── alert.txt.j2
│
├── community/
│   ├── templates/
│   │   ├── weekly_digest.txt.j2
│   │   ├── member_spotlight.txt.j2
│   │   ├── achievement_announcement.txt.j2
│   │   ├── server_milestone.txt.j2
│   │   └── feedback_request.txt.j2
│   └── prompts/
│       ├── community_health.yaml
│       └── engagement_analysis.yaml
│
├── moderation/
│   ├── templates/
│   │   ├── warning_message.txt.j2
│   │   ├── mute_notification.txt.j2
│   │   ├── ban_notification.txt.j2
│   │   └── appeal_response.txt.j2
│   └── prompts/
│       └── moderation_decision.yaml
│
└── loader.py  # ResourceManager implementation
```

---

## Message Templates

### Campaign Templates

#### `campaign/templates/reminder_default.txt.j2`
**Purpose**: Generic reminder for any campaign type

```jinja2
📢 **Reminder: {{ campaign.title }}**

{{ mentions }}

{% if campaign.custom_message %}
{{ campaign.custom_message }}
{% else %}
Don't forget to check the original message and react if you haven't already!
{% endif %}

📅 Campaign created: {{ campaign.created_at | datetime }}
👥 Total participants: {{ total_optins }}
```

**Variables**: `campaign` (dict), `mentions` (string), `total_optins` (int)

---

#### `campaign/templates/reminder_tournament.txt.j2`
**Purpose**: Gaming tournament reminders

```jinja2
🎮 **{{ campaign.title }} - Tournament Reminder**

{{ mentions }}

⚔️ **The tournament starts soon!**

{% if tournament_time %}
🕐 **Start Time**: {{ tournament_time }}
{% endif %}

{% if tournament_rules_link %}
📋 **Rules**: {{ tournament_rules_link }}
{% endif %}

Make sure you're ready:
✅ Check your equipment
✅ Join the voice channel 10 minutes early
✅ Have your in-game name ready

{% if prize_info %}
🏆 **Prizes**: {{ prize_info }}
{% endif %}

Good luck! 🎯

---
👥 Registered participants: {{ total_optins }}
```

**Variables**: `campaign`, `mentions`, `total_optins`, `tournament_time`, `tournament_rules_link`, `prize_info`

---

#### `campaign/templates/reminder_event.txt.j2`
**Purpose**: Community events (movie night, game night, etc.)

```jinja2
🎉 **{{ campaign.title }} - Event Reminder**

{{ mentions }}

{% if event_description %}
**About**: {{ event_description }}
{% endif %}

📅 **When**: {{ event_time }}
📍 **Where**: {{ event_location }}

{% if event_requirements %}
**What to bring**:
{{ event_requirements }}
{% endif %}

{% if event_host %}
**Hosted by**: {{ event_host }}
{% endif %}

See you there! 🎊

---
👥 {{ total_optins }} people confirmed attendance
```

**Variables**: `campaign`, `mentions`, `total_optins`, `event_time`, `event_location`, `event_description`, `event_requirements`, `event_host`

---

#### `campaign/templates/reminder_meeting.txt.j2`
**Purpose**: Server meetings, admin discussions

```jinja2
📋 **{{ campaign.title }} - Meeting Reminder**

{{ mentions }}

**Meeting starts {{ meeting_time_relative }}**

{% if agenda_items %}
**Agenda**:
{% for item in agenda_items %}
{{ loop.index }}. {{ item }}
{% endfor %}
{% endif %}

{% if meeting_channel %}
📍 **Channel**: {{ meeting_channel }}
{% endif %}

{% if preparation_notes %}
**Please prepare**:
{{ preparation_notes }}
{% endif %}

{% if meeting_duration %}
⏱️ **Estimated duration**: {{ meeting_duration }}
{% endif %}

---
👥 {{ total_optins }} attendees expected
```

**Variables**: `campaign`, `mentions`, `total_optins`, `meeting_time_relative`, `agenda_items` (list), `meeting_channel`, `preparation_notes`, `meeting_duration`

---

### Message Templates

#### `message/templates/announcement.txt.j2`
**Purpose**: Standard server announcements

```jinja2
📣 **{{ title }}**

{{ content }}

{% if action_required %}
⚠️ **Action Required**: {{ action_required }}
{% endif %}

{% if deadline %}
⏰ **Deadline**: {{ deadline }}
{% endif %}

{% if contact_person %}
**Questions?** Contact {{ contact_person }}
{% endif %}

{% if related_links %}
**Related Links**:
{% for link_name, link_url in related_links.items() %}
• [{{ link_name }}]({{ link_url }})
{% endfor %}
{% endif %}

---
{% if footer_text %}
{{ footer_text }}
{% else %}
*Posted by {{ author_name }} on {{ timestamp | datetime }}*
{% endif %}
```

**Variables**: `title`, `content`, `action_required`, `deadline`, `contact_person`, `related_links` (dict), `footer_text`, `author_name`, `timestamp`

---

#### `message/templates/welcome_new_member.txt.j2`
**Purpose**: Welcome messages for new server members

```jinja2
👋 **Welcome to {{ server_name }}, {{ member_mention }}!**

We're excited to have you here! 🎉

{% if server_description %}
**About us**: {{ server_description }}
{% endif %}

**Get started**:
{% if intro_channel %}
• Introduce yourself in {{ intro_channel }}
{% endif %}
{% if rules_channel %}
• Read our rules in {{ rules_channel }}
{% endif %}
{% if roles_channel %}
• Get roles in {{ roles_channel }}
{% endif %}

{% if helpful_channels %}
**Helpful channels**:
{% for channel_name, channel_mention in helpful_channels.items() %}
• {{ channel_name }}: {{ channel_mention }}
{% endfor %}
{% endif %}

{% if community_links %}
**Community links**:
{% for link_name, link_url in community_links.items() %}
• [{{ link_name }}]({{ link_url }})
{% endfor %}
{% endif %}

{% if welcome_role %}
You've been given the {{ welcome_role }} role! {{ emoji_wave }}
{% endif %}

If you have questions, feel free to ask {% if mod_role %}{{ mod_role }}{% else %}our moderators{% endif %}!

Enjoy your stay! 🌟
```

**Variables**: `server_name`, `member_mention`, `server_description`, `intro_channel`, `rules_channel`, `roles_channel`, `helpful_channels` (dict), `community_links` (dict), `welcome_role`, `mod_role`, `emoji_wave`

---

#### `message/templates/rule_reminder.txt.j2`
**Purpose**: Gentle rule reminders in channels

```jinja2
{% if is_general_reminder %}
📌 **Friendly Reminder**

Hey everyone! Let's keep {{ channel_name }} a welcoming place:

{% for rule in rules %}
{{ loop.index }}. {{ rule }}
{% endfor %}

{% else %}
{% if mention_user %}
{{ mention_user }}
{% endif %}

📌 **Reminder**: {{ rule_text }}

{% if explanation %}
{{ explanation }}
{% endif %}

{% endif %}

{% if rules_link %}
📋 Full server rules: {{ rules_link }}
{% endif %}

Thanks for keeping our community awesome! 💙
```

**Variables**: `is_general_reminder` (bool), `channel_name`, `rules` (list), `mention_user`, `rule_text`, `explanation`, `rules_link`

---

#### `message/templates/event_announcement.txt.j2`
**Purpose**: Event announcements with RSVP

```jinja2
{% if emoji_header %}{{ emoji_header }}{% else %}🎊{% endif %} **{{ event_name }}** {% if emoji_header %}{{ emoji_header }}{% else %}🎊{% endif %}

{{ event_description }}

📅 **Date**: {{ event_date }}
🕐 **Time**: {{ event_time }}
{% if timezone %}({{ timezone }}){% endif %}
{% if duration %}⏱️ **Duration**: {{ duration }}{% endif %}

{% if event_location %}
📍 **Location**: {{ event_location }}
{% endif %}

{% if event_requirements %}
**Requirements**:
{% for req in event_requirements %}
• {{ req }}
{% endfor %}
{% endif %}

{% if max_participants %}
👥 **Spots available**: {{ max_participants }}
{% endif %}

{% if rsvp_emoji %}
**RSVP by reacting with {{ rsvp_emoji }}**
{% endif %}

{% if event_host %}
**Hosted by**: {{ event_host }}
{% endif %}

{% if additional_info %}
---
{{ additional_info }}
{% endif %}
```

**Variables**: `emoji_header`, `event_name`, `event_description`, `event_date`, `event_time`, `timezone`, `duration`, `event_location`, `event_requirements` (list), `max_participants`, `rsvp_emoji`, `event_host`, `additional_info`

---

#### `message/templates/poll_create.txt.j2`
**Purpose**: Create polls with reaction voting

```jinja2
📊 **Poll: {{ poll_question }}**

{% if poll_description %}
{{ poll_description }}
{% endif %}

**Vote by reacting**:
{% for option in poll_options %}
{{ option.emoji }} - {{ option.text }}
{% endfor %}

{% if poll_deadline %}
⏰ **Voting ends**: {{ poll_deadline }}
{% endif %}

{% if allow_multiple %}
✓ You can vote for multiple options
{% else %}
✓ One vote per person please!
{% endif %}

{% if poll_creator %}
---
*Poll created by {{ poll_creator }}*
{% endif %}
```

**Variables**: `poll_question`, `poll_description`, `poll_options` (list of dicts with `emoji` and `text`), `poll_deadline`, `allow_multiple` (bool), `poll_creator`

---

### Community Templates

#### `community/templates/weekly_digest.txt.j2`
**Purpose**: Weekly server activity summary

```jinja2
📰 **{{ server_name }} - Weekly Digest**
*{{ week_start }} to {{ week_end }}*

{% if highlights %}
✨ **This Week's Highlights**:
{% for highlight in highlights %}
• {{ highlight }}
{% endfor %}
{% endif %}

📊 **Server Stats**:
• {{ new_members_count }} new members joined
• {{ total_messages }} messages sent
• {{ active_members }} active members

{% if top_channels %}
🔥 **Most Active Channels**:
{% for channel in top_channels %}
{{ loop.index }}. {{ channel.name }} ({{ channel.message_count }} messages)
{% endfor %}
{% endif %}

{% if upcoming_events %}
📅 **Upcoming Events**:
{% for event in upcoming_events %}
• **{{ event.name }}** - {{ event.date }}
{% endfor %}
{% endif %}

{% if member_spotlight %}
⭐ **Member Spotlight**: {{ member_spotlight.name }}
{{ member_spotlight.description }}
{% endif %}

{% if achievements %}
🏆 **Community Achievements**:
{% for achievement in achievements %}
• {{ achievement }}
{% endfor %}
{% endif %}

{% if closing_message %}
---
{{ closing_message }}
{% endif %}
```

**Variables**: `server_name`, `week_start`, `week_end`, `highlights` (list), `new_members_count`, `total_messages`, `active_members`, `top_channels` (list), `upcoming_events` (list), `member_spotlight` (dict), `achievements` (list), `closing_message`

---

## LLM Prompts

### Discovery Prompts

#### `discovery/prompts/discovery_intent.yaml`
**Purpose**: Parse natural language discovery queries

```yaml
intent: "Entity Discovery"
description: "Parse user queries to find Discord entities (servers, channels, roles, members)"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.1

input_vars:
  - intent  # User's natural language query

output_format: |
  {
    "entity_type": "server" | "channel" | "role" | "member",
    "query": "search string",
    "guild_name": "optional server name context",
    "guild_id": "optional server ID",
    "scope": "global" | "guild",
    "detailed": true | false,
    "limit": number,
    "filters": {
      "channel_type": "text" | "voice" | "category" | null,
      "permissions_required": ["list of permissions"] | null
    }
  }

system_prompt: |
  You are a Discord entity discovery assistant. Parse user queries about finding Discord servers, channels, roles, or members.

  Extract:
  1. **entity_type**: What they're looking for (server, channel, role, member)
  2. **query**: The name or partial name to search for
  3. **scope**: Whether to search globally or within a specific server
  4. **guild_name** or **guild_id**: If they mention a server context
  5. **detailed**: Whether they want full details (default: true)
  6. **limit**: How many results (default: 5, max: 20)
  7. **filters**: Additional filtering criteria

  Examples:
  - "find channel general in MyServer" → entity_type=channel, query=general, guild_name=MyServer
  - "list all servers" → entity_type=server, query=*, scope=global
  - "show me moderator role" → entity_type=role, query=moderator
  - "get all voice channels in 123456" → entity_type=channel, guild_id=123456, filters={channel_type: voice}

template: |
  Parse the following Discord discovery query:

  Query: "{{ intent }}"

  Return ONLY valid JSON matching the output format. No explanation.
```

---

#### `discovery/prompts/entity_resolution.yaml`
**Purpose**: Resolve ambiguous entity references

```yaml
intent: "Entity Resolution"
description: "Disambiguate when multiple entities match a query"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.2

input_vars:
  - query        # Original search query
  - matches      # List of matched entities
  - context      # Conversation context

output_format: |
  {
    "best_match_id": "entity ID most likely intended",
    "confidence": 0.0-1.0,
    "reasoning": "why this match was chosen",
    "alternatives": ["list of other possible matches"],
    "needs_clarification": true | false
  }

system_prompt: |
  You are a Discord entity resolution assistant. When a search returns multiple results, determine which entity the user most likely meant based on context.

  Consider:
  1. **Exact matches** over partial matches
  2. **Recency** in conversation context
  3. **Common patterns** (e.g., "general" usually means main chat)
  4. **Activity level** (active channels over inactive)

  If confidence < 0.7, set needs_clarification=true

template: |
  Original query: "{{ query }}"

  Matched entities:
  {% for match in matches %}
  {{ loop.index }}. {{ match.name }} (ID: {{ match.id }}, type: {{ match.type }})
     {% if match.guild_name %}Server: {{ match.guild_name }}{% endif %}
  {% endfor %}

  {% if context %}
  Recent conversation context:
  {{ context }}
  {% endif %}

  Which entity did the user most likely intend? Return JSON only.
```

---

### Message Prompts

#### `message/prompts/message_intent.yaml`
**Purpose**: Parse message sending requests

```yaml
intent: "Message Composition"
description: "Parse natural language message requests into structured sends"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.3

input_vars:
  - intent         # User's message request
  - context        # Available channels, roles, etc.

output_format: |
  {
    "channel": "channel name or ID",
    "content": "message text",
    "mentions": {
      "users": ["user IDs"],
      "roles": ["role IDs"],
      "everyone": false,
      "here": false
    },
    "template": "template name if applicable" | null,
    "template_vars": {key: value} | null,
    "reply_to": "message ID" | null
  }

system_prompt: |
  You are a Discord message composition assistant. Parse natural language requests to send messages.

  Extract:
  1. **Target channel**: Where to send
  2. **Message content**: What to say
  3. **Mentions**: Who to ping (@user, @role, @everyone, @here)
  4. **Template usage**: If the request matches a common pattern, suggest a template
  5. **Reply context**: If responding to another message

  Common templates:
  - "announcement" → formal server announcement
  - "welcome" → new member welcome
  - "event" → event announcement
  - "poll" → poll creation
  - "rule_reminder" → rule enforcement

  Safety:
  - Default mentions.everyone = false
  - Default mentions.here = false
  - Only enable if explicitly requested

template: |
  User request: "{{ intent }}"

  Available context:
  {% if context.channels %}
  Channels: {% for ch in context.channels %}{{ ch.name }} {% endfor %}
  {% endif %}
  {% if context.roles %}
  Roles: {% for role in context.roles %}{{ role.name }} {% endfor %}
  {% endif %}

  Parse this into a structured message send. Return JSON only.
```

---

#### `message/prompts/mention_suggestion.yaml`
**Purpose**: Suggest who should be mentioned

```yaml
intent: "Mention Suggestion"
description: "Suggest appropriate mentions for message context"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.2

input_vars:
  - message_content  # The message being sent
  - channel_name     # Target channel
  - available_roles  # Roles in server

output_format: |
  {
    "suggested_mentions": {
      "roles": [
        {"role_id": "123", "role_name": "Moderators", "reason": "why suggest this"}
      ],
      "everyone": false,
      "here": false
    },
    "mention_reasoning": "overall explanation",
    "safety_warning": "warning if sensitive" | null
  }

system_prompt: |
  You are a Discord mention suggestion assistant. Based on message content and context, suggest appropriate mentions.

  Guidelines:
  1. **Be conservative**: Don't suggest @everyone/@here unless absolutely critical
  2. **Context-aware**: Match roles to message purpose
     - Moderator issues → @Moderators
     - Technical problems → @Tech Support
     - Event announcements → @Event Attendees
  3. **Safety first**: Warn about mentions that could be disruptive

  Examples:
  - "Server rules violation" → suggest @Moderators
  - "Tournament starting" → suggest @Tournament Participants
  - "Critical server downtime" → suggest @everyone with safety warning

template: |
  Message content: "{{ message_content }}"
  Channel: {{ channel_name }}

  Available roles:
  {% for role in available_roles %}
  - {{ role.name }} ({{ role.member_count }} members)
  {% endfor %}

  Who should be mentioned? Return JSON only.
```

---

### Campaign Prompts

#### `campaign/prompts/campaign_intent.yaml`
**Purpose**: Parse campaign creation requests

```yaml
intent: "Campaign Creation"
description: "Parse natural language campaign setup requests"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.2

input_vars:
  - intent           # User's campaign request
  - channel_context  # Recent messages for context

output_format: |
  {
    "campaign_type": "tournament" | "event" | "meeting" | "general",
    "title": "campaign title",
    "emoji": "reaction emoji to track",
    "remind_at": "ISO datetime",
    "template": "template name to use",
    "template_vars": {
      "key": "value"
    },
    "channel_id": "target channel" | null,
    "message_id": "message to track" | null
  }

system_prompt: |
  You are a Discord campaign creation assistant. Parse requests to create reaction-based opt-in campaigns.

  Extract:
  1. **Campaign type**: Infer from context (tournament, event, meeting, general)
  2. **Title**: Clear, descriptive campaign name
  3. **Emoji**: Default to 👍 unless specified
  4. **Timing**: When to send reminder
  5. **Template**: Match appropriate template
  6. **Variables**: Extract template-specific data

  Template selection:
  - "tournament" → includes prize info, rules, registration details
  - "event" → includes location, time, what to bring
  - "meeting" → includes agenda, duration, preparation
  - "general" → basic reminder

  Date parsing:
  - "tomorrow at 6pm" → calculate ISO datetime
  - "next Friday" → calculate ISO datetime
  - "in 2 days" → calculate ISO datetime

template: |
  Campaign request: "{{ intent }}"

  {% if channel_context %}
  Recent channel messages:
  {% for msg in channel_context %}
  - {{ msg.author }}: {{ msg.content[:100] }}
  {% endfor %}
  {% endif %}

  Parse this into a campaign creation. Return JSON only.
```

---

#### `campaign/prompts/template_suggestion.yaml`
**Purpose**: Suggest best template for campaign

```yaml
intent: "Template Suggestion"
description: "Recommend the best reminder template based on campaign details"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.1

input_vars:
  - campaign_title      # Title of campaign
  - campaign_message    # Original message content
  - campaign_context    # Channel, server context

output_format: |
  {
    "recommended_template": "template_name",
    "confidence": 0.0-1.0,
    "reasoning": "why this template",
    "template_variables": {
      "var_name": "suggested_value"
    },
    "alternatives": ["other possible templates"]
  }

system_prompt: |
  You are a Discord template recommendation assistant. Suggest the best reminder template based on campaign context.

  Available templates:
  1. **reminder_tournament**: Gaming tournaments, competitions
  2. **reminder_event**: Community events, social gatherings
  3. **reminder_meeting**: Server meetings, admin discussions
  4. **reminder_default**: Generic catch-all

  Match based on:
  - Keywords in title/message
  - Channel context
  - Common patterns

  Extract template variables from context when possible.

template: |
  Campaign title: "{{ campaign_title }}"

  {% if campaign_message %}
  Original message:
  {{ campaign_message }}
  {% endif %}

  {% if campaign_context %}
  Context:
  - Channel: {{ campaign_context.channel_name }}
  - Server: {{ campaign_context.server_name }}
  {% endif %}

  Which template is best? Return JSON only.
```

---

### Community Prompts

#### `community/prompts/community_health.yaml`
**Purpose**: Analyze community engagement

```yaml
intent: "Community Health Analysis"
description: "Analyze server activity and suggest improvements"
model: "claude-3-5-sonnet-20250929"
version: "1.0"
temperature: 0.3

input_vars:
  - server_stats    # Message counts, member activity, etc.
  - channel_activity  # Per-channel metrics
  - member_growth   # Join/leave trends

output_format: |
  {
    "health_score": 0-100,
    "strengths": ["positive observations"],
    "concerns": ["areas needing attention"],
    "recommendations": [
      {
        "action": "suggested action",
        "priority": "high" | "medium" | "low",
        "expected_impact": "description"
      }
    ],
    "engagement_trends": {
      "overall": "increasing" | "stable" | "decreasing",
      "top_channels": ["channel names"],
      "declining_channels": ["channel names"]
    }
  }

system_prompt: |
  You are a Discord community health analyst. Analyze server metrics and provide actionable insights.

  Consider:
  1. **Activity levels**: Message frequency, active users
  2. **Growth**: New members vs. churn rate
  3. **Engagement**: Channel usage distribution
  4. **Balance**: Avoid over-moderation or under-moderation

  Recommendations should be:
  - Specific and actionable
  - Prioritized by impact
  - Realistic for community size

template: |
  Server Statistics:
  {{ server_stats | tojson }}

  Channel Activity:
  {{ channel_activity | tojson }}

  Member Growth:
  {{ member_growth | tojson }}

  Analyze community health and provide recommendations. Return JSON only.
```

---

## Template Variables Reference

### Common Variables (All Templates)

```python
{
    "timestamp": datetime,           # Current time
    "server_name": str,              # Discord server name
    "server_id": str,                # Discord server ID
    "channel_name": str,             # Channel name
    "channel_id": str,               # Channel ID
    "author_name": str,              # Message author
    "author_id": str,                # Author ID
}
```

### Campaign-Specific Variables

```python
{
    "campaign": {
        "id": int,
        "title": str,
        "emoji": str,
        "remind_at": datetime,
        "created_at": datetime,
        "status": str,
        "custom_message": str | None
    },
    "mentions": str,                 # Pre-formatted @mention string
    "total_optins": int,             # Number of opted-in users
    "optin_users": [                 # List of opted-in users
        {"id": str, "username": str, "mention": str}
    ]
}
```

### Event-Specific Variables

```python
{
    "event_name": str,
    "event_description": str,
    "event_date": str,
    "event_time": str,
    "event_location": str,
    "event_host": str | None,
    "event_requirements": list[str],
    "max_participants": int | None,
    "rsvp_emoji": str,
    "timezone": str | None
}
```

---

## Usage Patterns

### Loading Templates

```python
# In a workflow
from discord_mcp.context import Context

async def send_announcement(ctx: Context, **kwargs):
    # Load template
    template = ctx.resources.get_template("message/templates/announcement.txt.j2")

    # Render with data
    content = template.render(
        title="Server Update",
        content="New features have been added!",
        author_name=ctx.user_name,
        timestamp=datetime.now()
    )

    # Send
    await discord_send_message(channel_id="123", content=content)
```

### Using Prompts

```python
# Parse intent
prompt_config = ctx.resources.get_prompt("discovery/prompts/discovery_intent.yaml")

# Build prompt from template
from jinja2 import Template
prompt_template = Template(prompt_config["template"])
prompt = prompt_template.render(intent="find general channel")

# Call LLM
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model=prompt_config["model"],
    messages=[{"role": "user", "content": prompt}],
    temperature=prompt_config["temperature"],
    max_tokens=500
)

# Parse JSON response
import json
parsed = json.loads(response.content[0].text)
```

---

## Why These Resources?

### Message Templates

**Discord community management patterns**:

1. **Announcements** - Every server makes announcements
2. **Welcome messages** - First impressions matter
3. **Event coordination** - Common community activity
4. **Polls** - Quick decision-making tool
5. **Rule reminders** - Gentle moderation
6. **Weekly digests** - Keep community engaged

### LLM Prompts

**Natural language understanding needs**:

1. **Discovery intent** - Users say "find general" not "entity_type=channel, query=general"
2. **Message composition** - Users say "announce tournament" not "use template X with vars Y"
3. **Mention suggestions** - Help users avoid ping-spamming
4. **Template matching** - Auto-select best template for context
5. **Community analysis** - Surface insights from metrics

### Campaign Templates

**Real-world use cases**:

1. **Tournaments** - Gaming servers run these constantly
2. **Events** - Movie nights, game sessions, meetups
3. **Meetings** - Admin meetings, team discussions
4. **General** - Catch-all for custom scenarios

---

## Extension Points

### Adding New Templates

```python
# 1. Create .txt.j2 file in appropriate directory
# 2. Document variables in docstring
# 3. Register in WORKFLOW_RESOURCES
# 4. Add usage example in workflow

# Example:
"""
Template: custom_template.txt.j2
Variables:
  - custom_var1: Description
  - custom_var2: Description
Usage:
  Used by workflow X for purpose Y
"""
```

### Adding New Prompts

```yaml
# 1. Create .yaml file with standard structure
# 2. Define input_vars and output_format
# 3. Write clear system_prompt with examples
# 4. Test with various inputs
# 5. Document in workflow docs
```

---

## Best Practices

1. **Keep templates simple**: Don't overcomplicate with logic
2. **Provide defaults**: Use `{% if var %}` to handle missing data
3. **Document variables**: Always list required variables
4. **Test with edge cases**: Empty lists, None values, long strings
5. **Version prompts**: Track prompt versions for reproducibility
6. **Monitor LLM costs**: Cache common prompt results
7. **Validate outputs**: Always validate JSON from LLM responses

---

## Future Enhancements

1. **Template versioning**: Support multiple template versions
2. **Localization**: Multi-language template support
3. **Dynamic templates**: User-customizable templates in database
4. **Template marketplace**: Share templates between servers
5. **A/B testing**: Test different templates for effectiveness
6. **Analytics**: Track which templates get most engagement
7. **Smart suggestions**: LLM suggests template improvements
