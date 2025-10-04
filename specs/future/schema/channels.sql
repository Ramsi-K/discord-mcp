-- Channels Table
CREATE TABLE channels (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255) NOT NULL UNIQUE,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- text, voice, category, forum, etc.
    topic TEXT,
    position INTEGER,
    parent_id VARCHAR(255), -- For channels under categories
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on discord_id for faster lookups
CREATE INDEX idx_channels_discord_id ON channels(discord_id);

-- Create index on server_id for server-based queries
CREATE INDEX idx_channels_server_id ON channels(server_id);

-- Create index on name for name-based queries
CREATE INDEX idx_channels_name ON channels(name);

-- Create index on parent_id for category-based queries
CREATE INDEX idx_channels_parent_id ON channels(parent_id);

-- Channel Permissions Table (for tracking bot permissions in each channel)
CREATE TABLE channel_permissions (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT TRUE,
    can_send BOOLEAN DEFAULT TRUE,
    can_embed BOOLEAN DEFAULT TRUE,
    can_attach BOOLEAN DEFAULT TRUE,
    can_mention_everyone BOOLEAN DEFAULT FALSE,
    can_manage BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(channel_id)
);

-- Create index on channel_id for faster lookups
CREATE INDEX idx_channel_permissions_channel_id ON channel_permissions(channel_id);