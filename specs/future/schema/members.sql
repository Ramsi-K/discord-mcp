-- Members Table
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    username VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    joined_at TIMESTAMP,
    avatar_url TEXT,
    is_bot BOOLEAN DEFAULT FALSE,
    last_active TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, server_id)
);

-- Member Interests Table
CREATE TABLE member_interests (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    topic VARCHAR(255) NOT NULL,
    confidence FLOAT NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(member_id, topic)
);

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_interests_member_id ON member_interests(member_id);

-- Create index on topic for interest-based queries
CREATE INDEX idx_member_interests_topic ON member_interests(topic);

-- Member Messages Table
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

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_messages_member_id ON member_messages(member_id);

-- Create index on channel_id for channel-based queries
CREATE INDEX idx_member_messages_channel_id ON member_messages(channel_id);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_member_messages_timestamp ON member_messages(timestamp);

-- Create index on is_introduction for finding introductions
CREATE INDEX idx_member_messages_is_introduction ON member_messages(is_introduction);

-- Member Tags Table
CREATE TABLE member_tags (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    tag VARCHAR(255) NOT NULL,
    added_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(member_id, tag)
);

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_tags_member_id ON member_tags(member_id);

-- Create index on tag for tag-based queries
CREATE INDEX idx_member_tags_tag ON member_tags(tag);

-- Member Notes Table
CREATE TABLE member_notes (
    id SERIAL PRIMARY KEY,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    added_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on member_id for faster lookups
CREATE INDEX idx_member_notes_member_id ON member_notes(member_id);
