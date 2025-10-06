# Database Schema (v0.1.0)

The Discord MCP server uses SQLite for persistent storage.

## Database Location

- **Environment Variable**: `MCP_DISCORD_DB_PATH`
- **Default**: `discord_mcp.db` (in current working directory)
- **Format**: SQLite 3

## Campaign System Tables

### campaigns

Stores reaction opt-in reminder campaigns.

```sql
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    channel_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    emoji TEXT NOT NULL,
    remind_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    UNIQUE(channel_id, message_id, emoji)
);
```

**Fields**:

- `id`: Auto-incrementing campaign ID
- `title`: Optional campaign title/description
- `channel_id`: Discord channel ID where announcement was posted
- `message_id`: Discord message ID to track reactions on
- `emoji`: Emoji to track (e.g., "✅", "👍")
- `remind_at`: Timestamp when reminder should be sent
- `created_at`: When campaign was created
- `status`: Campaign status ("active", "completed", "cancelled")

**Constraints**:

- Unique constraint on (channel_id, message_id, emoji) prevents duplicate campaigns

### opt_ins

Stores users who opted in to campaigns (via reactions).

```sql
CREATE TABLE IF NOT EXISTS opt_ins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT,
    tallied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
    UNIQUE(campaign_id, user_id)
);
```

**Fields**:

- `id`: Auto-incrementing opt-in ID
- `campaign_id`: Foreign key to campaigns table
- `user_id`: Discord user ID who opted in
- `username`: Discord username (for display)
- `tallied_at`: When this opt-in was recorded

**Constraints**:

- Foreign key to campaigns with CASCADE delete
- Unique constraint on (campaign_id, user_id) ensures no duplicates

**Indexes**:

```sql
CREATE INDEX IF NOT EXISTS idx_opt_ins_campaign ON opt_ins(campaign_id);
CREATE INDEX IF NOT EXISTS idx_opt_ins_user ON opt_ins(user_id);
```

### reminder_logs

Tracks sent reminders for audit and debugging.

```sql
CREATE TABLE IF NOT EXISTS reminder_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipient_count INTEGER NOT NULL,
    message_chunks INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);
```

**Fields**:

- `id`: Auto-incrementing log ID
- `campaign_id`: Foreign key to campaigns table
- `sent_at`: When reminder was sent
- `recipient_count`: Number of users reminded
- `message_chunks`: Number of Discord messages sent (due to chunking)
- `success`: Whether send was successful
- `error_message`: Error details if failed

**Constraints**:

- Foreign key to campaigns with CASCADE delete

## Legacy Server Registry Tables

These tables exist from the legacy server registry implementation but are not actively used in v0.1.0:

- `servers`: Discord server information
- `channels`: Discord channel information
- `roles`: Discord role information
- `context`: Conversation context tracking

**Note**: These will be refactored or removed in v0.2.0 depending on feature requirements.

## Migrations

Database schema is managed via [src/discord_mcp/database/migrations.py](../../src/discord_mcp/database/migrations.py).

On server startup:

1. Connection established to SQLite database
2. `run_migrations()` creates tables if they don't exist
3. Future versions will include migration versioning

## Repository Pattern

Data access is abstracted through repository classes in [src/discord_mcp/database/repositories.py](../../src/discord_mcp/database/repositories.py):

- `CampaignRepository`: CRUD operations for campaigns
- `OptInRepository`: CRUD operations for opt-ins
- `ReminderLogRepository`: CRUD operations for reminder logs

## Usage Example

```python
from discord_mcp.config import Config
from discord_mcp.database.repositories import CampaignRepository
from discord_mcp.database.models import DatabaseConnection
from datetime import datetime, timedelta

# Initialize
config = Config()
db = DatabaseConnection(config.database_path)
campaign_repo = CampaignRepository(db)

# Create campaign
campaign = campaign_repo.create(
    title="Weekly Meeting Reminder",
    channel_id="123456789",
    message_id="987654321",
    emoji="✅",
    remind_at=datetime.now() + timedelta(days=7)
)

# Get campaign
campaign = campaign_repo.get_by_id(campaign.id)

# List all active campaigns
active = campaign_repo.get_active_campaigns()
```

## Backup & Maintenance

**Backup**:

- Copy the SQLite file: `cp discord_mcp.db discord_mcp.db.backup`

**Cleanup**:

- Old completed campaigns can be deleted
- `DELETE FROM campaigns WHERE status = 'completed' AND remind_at < datetime('now', '-30 days')`

**Database Size**:

- Current schema is lightweight
- Expect ~1KB per campaign + 100 bytes per opt-in
- 1000 campaigns with 100 opt-ins each ≈ 11MB
