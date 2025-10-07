-- Member Activity Table
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

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_activity_member_id ON member_activity(member_id);

-- Create index on date for date-based queries
CREATE INDEX idx_member_activity_date ON member_activity(date);

-- Channel Activity Table
CREATE TABLE channel_activity (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    discord_channel_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    unique_authors INTEGER DEFAULT 0,
    reaction_count INTEGER DEFAULT 0,
    UNIQUE(channel_id, date)
);

-- Create index on channel_id for faster lookups
CREATE INDEX idx_channel_activity_channel_id ON channel_activity(channel_id);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_channel_activity_guild_id ON channel_activity(guild_id);

-- Create index on date for date-based queries
CREATE INDEX idx_channel_activity_date ON channel_activity(date);

-- Member Channel Activity Table (for tracking which channels a member is active in)
CREATE TABLE member_channel_activity (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    channel_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    reaction_count INTEGER DEFAULT 0,
    UNIQUE(member_id, channel_id, date)
);

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_channel_activity_member_id ON member_channel_activity(member_id);

-- Create index on channel_id for channel-based queries
CREATE INDEX idx_member_channel_activity_channel_id ON member_channel_activity(channel_id);

-- Create index on date for date-based queries
CREATE INDEX idx_member_channel_activity_date ON member_channel_activity(date);

-- Hourly Activity Table (for tracking peak hours)
CREATE TABLE hourly_activity (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    discord_channel_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    date DATE NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour < 24),
    message_count INTEGER DEFAULT 0,
    unique_authors INTEGER DEFAULT 0,
    UNIQUE(server_id, channel_id, date, hour)
);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_hourly_activity_guild_id ON hourly_activity(guild_id);

-- Create index on channel_id for channel-based queries
CREATE INDEX idx_hourly_activity_channel_id ON hourly_activity(channel_id);

-- Create index on date and hour for time-based queries
CREATE INDEX idx_hourly_activity_time ON hourly_activity(date, hour);

-- Reaction Activity Table
CREATE TABLE reaction_activity (
    id SERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    discord_channel_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    emoji VARCHAR(255) NOT NULL,
    count INTEGER DEFAULT 0,
    first_added_at TIMESTAMP,
    UNIQUE(message_id, emoji)
);

-- Create index on message_id for faster lookups
CREATE INDEX idx_reaction_activity_message_id ON reaction_activity(message_id);

-- Create index on channel_id for channel-based queries
CREATE INDEX idx_reaction_activity_channel_id ON reaction_activity(channel_id);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_reaction_activity_guild_id ON reaction_activity(guild_id);

-- User Reaction Table (for tracking which users reacted to which messages)
CREATE TABLE user_reactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    emoji VARCHAR(255) NOT NULL,
    added_at TIMESTAMP,
    UNIQUE(user_id, message_id, emoji)
);

-- Create index on user_id for user-based queries
CREATE INDEX idx_user_reactions_user_id ON user_reactions(user_id);

-- Create index on message_id for message-based queries
CREATE INDEX idx_user_reactions_message_id ON user_reactions(message_id);
