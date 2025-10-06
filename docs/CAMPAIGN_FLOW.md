# Campaign Flow Documentation

## Overview

The campaign system enables automated reminder messaging based on Discord message reactions. Moderators can create campaigns that track user opt-ins via emoji reactions and send automated reminders to opted-in users at scheduled times.

## Use Case

**Scenario**: A gaming server wants to organize a tournament. Moderators post an announcement with reaction options (e.g., 👍 for "Attending", ❓ for "Maybe"). Days later, they want to automatically remind everyone who reacted with 👍.

## Campaign Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                      CAMPAIGN LIFECYCLE                      │
└─────────────────────────────────────────────────────────────┘

1. CREATE           → Campaign setup with message & emoji
2. TALLY            → Collect reactions (can run multiple times)
3. BUILD            → Generate reminder message with @mentions
4. SEND/SCHEDULE    → Send reminder immediately or schedule
5. MANAGE           → Update status, view details, delete
```

## Step-by-Step Workflow

### 1. Create a Campaign

**Tool**: `discord_create_campaign`

**When**: After posting your announcement message with reaction options

**Parameters**:
- `channel_id`: Where the announcement message is
- `message_id`: The announcement message ID to track
- `emoji`: Which emoji to track (e.g., "👍", "🎉", ":thumbsup:")
- `remind_at`: ISO datetime for automated reminder (e.g., "2025-10-15T18:00:00")
- `title`: Optional campaign name (e.g., "Tournament Signup Reminder")

**Example**:
```python
discord_create_campaign(
    channel_id="123456789012345678",
    message_id="987654321098765432",
    emoji="👍",
    remind_at="2025-10-15T18:00:00",
    title="Tournament Reminder"
)
```

**What happens**:
- Campaign record created in database with status `active`
- Linked to specific message and emoji
- Reminder scheduled for `remind_at` datetime

---

### 2. Tally Opt-Ins

**Tool**: `discord_tally_optins`

**When**:
- Anytime after campaign creation
- Before building/sending reminders
- Can run multiple times (idempotent - won't duplicate users)

**Parameters**:
- `campaign_id`: ID returned from `discord_create_campaign`

**Example**:
```python
discord_tally_optins(campaign_id=1)
```

**What happens**:
- Fetches ALL reactions on the message
- Filters for the specific emoji you're tracking
- Stores unique user IDs in `optins` table
- Skips bots and duplicates
- Returns counts: `total_optins`, `new_optins`, `existing_optins`

**Important**:
- Run this RIGHT BEFORE sending reminders to get latest opt-ins
- Safe to run multiple times - won't create duplicates
- Automatically refreshes who's opted in

---

### 3. List Campaigns

**Tool**: `discord_list_campaigns`

**When**: View all campaigns or filter by status

**Parameters**:
- `status`: Optional filter ("active", "completed", "cancelled")

**Example**:
```python
# List all active campaigns
discord_list_campaigns(status="active")

# List all campaigns
discord_list_campaigns()
```

**Returns**: Array of campaigns with details

---

### 4. Get Campaign Details

**Tool**: `discord_get_campaign`

**When**: Check specific campaign info

**Parameters**:
- `campaign_id`: The campaign ID

**Example**:
```python
discord_get_campaign(campaign_id=1)
```

**Returns**: Full campaign details including emoji, channel, status, remind_at

---

### 5. Build Reminder Message

**Tool**: `discord_build_reminder`

**When**: Preview the reminder message before sending

**Parameters**:
- `campaign_id`: The campaign ID
- `template`: Optional custom message template

**Example**:
```python
# Default template
discord_build_reminder(campaign_id=1)

# Custom template
discord_build_reminder(
    campaign_id=1,
    template="Hey {mentions}! Tournament starts tomorrow - don't forget!"
)
```

**What happens**:
- Fetches all opted-in users from database
- Creates `<@user_id>` mentions for each user
- Chunks mentions to stay under 2000 character Discord limit
- Returns array of message chunks ready to send

**Template Variables**:
- `{title}`: Campaign title
- `{mentions}`: Space-separated @mentions (auto-inserted)

---

### 6. Send Reminder

**Tool**: `discord_send_reminder`

**When**: Manually trigger reminder or run as scheduled automation

**Parameters**:
- `campaign_id`: The campaign ID
- `dry_run`: If True, don't actually send (default: True for safety)

**Example**:
```python
# Test run (doesn't actually send)
discord_send_reminder(campaign_id=1, dry_run=True)

# Actually send the reminder
discord_send_reminder(campaign_id=1, dry_run=False)
```

**What happens**:
1. Calls `discord_build_reminder` internally
2. Sends each message chunk to the campaign's channel
3. Rate limits (1 second between chunks)
4. Logs success/errors to `reminders_log` table
5. Updates campaign status to `completed` if successful

**Safety**: Always defaults to `dry_run=True` to prevent accidental sends

---

### 7. Automated Reminder Processing

**Tool**: `discord_run_due_reminders`

**When**: Run on a schedule (e.g., every 5 minutes via cron/task scheduler)

**Parameters**:
- `now`: Optional datetime override (for testing)

**Example**:
```python
# Check and send all due reminders
discord_run_due_reminders()
```

**What happens**:
1. Queries database for campaigns where `remind_at <= now` and `status = 'active'`
2. For each due campaign:
   - Runs `discord_tally_optins` to refresh opt-ins
   - Sends reminder via `discord_send_reminder`
   - Logs results
   - Updates campaign status
3. Rate limits between campaigns (2 seconds)

**Recommended**: Set up a cron job or scheduled task:
```bash
*/5 * * * * uv run python -c "import asyncio; from discord_mcp.tools.campaigns import discord_run_due_reminders; asyncio.run(discord_run_due_reminders())"
```

---

### 8. Update Campaign Status

**Tool**: `discord_update_campaign_status`

**When**: Cancel or manually complete a campaign

**Parameters**:
- `campaign_id`: The campaign ID
- `status`: New status ("active", "completed", "cancelled")

**Example**:
```python
# Cancel a campaign
discord_update_campaign_status(campaign_id=1, status="cancelled")

# Reactivate a campaign
discord_update_campaign_status(campaign_id=1, status="active")
```

---

### 9. Delete Campaign

**Tool**: `discord_delete_campaign`

**When**: Permanently remove a campaign and all opt-in data

**Parameters**:
- `campaign_id`: The campaign ID

**Example**:
```python
discord_delete_campaign(campaign_id=1)
```

**What happens**:
- Deletes all opt-ins associated with the campaign
- Marks campaign as `deleted` in database
- **Warning**: Cannot be undone!

---

### 10. List Campaign Opt-Ins

**Tool**: `discord_list_optins`

**When**: View who has opted in

**Parameters**:
- `campaign_id`: The campaign ID
- `limit`: Max results per page (default: 100)
- `after_user_id`: For pagination

**Example**:
```python
# Get first 100 opt-ins
discord_list_optins(campaign_id=1, limit=100)

# Get next page
discord_list_optins(campaign_id=1, limit=100, after_user_id="123456789")
```

---

## Database Schema

### Campaigns Table
```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    title TEXT,
    channel_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    emoji TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'  -- 'active', 'completed', 'cancelled', 'deleted'
);
```

### Opt-Ins Table
```sql
CREATE TABLE optins (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT,
    tallied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, user_id)  -- Prevents duplicates
);
```

### Reminders Log Table
```sql
CREATE TABLE reminders_log (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipient_count INTEGER,
    message_chunks INTEGER,
    success BOOLEAN,
    error_message TEXT
);
```

---

## Complete Example Workflow

```python
# 1. User posts tournament announcement in #announcements
# 2. Add reactions: 👍 (Attending), ❓ (Maybe), 👎 (Not Attending)

# 3. Create campaign to remind 👍 users
campaign = discord_create_campaign(
    channel_id="123456789012345678",
    message_id="987654321098765432",
    emoji="👍",
    remind_at="2025-10-15T18:00:00",
    title="Tournament Reminder - Day Before"
)
campaign_id = campaign["campaign"]["id"]  # e.g., 1

# 4. Wait for reactions to come in... (days pass)

# 5. Check current opt-ins
discord_tally_optins(campaign_id=1)
# Returns: {"total_optins": 42, "new_optins": 42, "existing_optins": 0}

# 6. Preview reminder message
preview = discord_build_reminder(campaign_id=1)
# Shows message chunks with @mentions

# 7. Automation handles the rest!
# At 2025-10-15T18:00:00, discord_run_due_reminders() automatically:
#   - Refreshes opt-ins
#   - Sends reminder
#   - Marks campaign complete

# OR send manually:
discord_send_reminder(campaign_id=1, dry_run=False)
```

---

## Multi-Emoji Support

**Q**: What if I want to track multiple emojis for one message?

**A**: Create separate campaigns for each emoji!

```python
# Campaign 1: Track 👍 reactions
campaign_yes = discord_create_campaign(
    channel_id="123456",
    message_id="789012",
    emoji="👍",
    remind_at="2025-10-15T18:00:00",
    title="Tournament - YES responses"
)

# Campaign 2: Track ❓ reactions
campaign_maybe = discord_create_campaign(
    channel_id="123456",
    message_id="789012",  # Same message!
    emoji="❓",
    remind_at="2025-10-14T18:00:00",  # Earlier reminder for maybes
    title="Tournament - MAYBE responses"
)
```

Each campaign independently tracks its emoji and can have different reminder times.

---

## Best Practices

1. **Always tally before sending**: Run `discord_tally_optins` right before `discord_send_reminder` to get the latest opt-ins

2. **Test with dry_run**: Always test with `dry_run=True` first

3. **Use descriptive titles**: Makes it easy to identify campaigns later

4. **Clean up old campaigns**: Delete completed campaigns you no longer need

5. **Monitor reminder logs**: Check `reminders_log` table for send failures

6. **Rate limit awareness**: The system auto-delays between message chunks (1s) and campaigns (2s)

7. **Timezone handling**: Use UTC times or include timezone info in ISO format

---

## Troubleshooting

**Campaign not sending reminders automatically?**
- Ensure `discord_run_due_reminders` is scheduled to run regularly
- Check campaign `status` is "active"
- Verify `remind_at` datetime is in the past

**No opt-ins being tallied?**
- Verify emoji matches exactly (case-sensitive for custom emojis)
- Check that message has reactions
- Ensure bot has permission to read message history

**Reminder message too long?**
- System automatically chunks messages under 2000 characters
- Each chunk sent separately with 1-second delay

**Users not getting mentioned?**
- Check bot has `mention_everyone` permission if using @everyone
- Individual user mentions don't require special permissions
