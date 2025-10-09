-- Servers Table
CREATE TABLE servers (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_url TEXT,
    owner_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on discord_id for faster lookups
CREATE INDEX idx_servers_discord_id ON servers(discord_id);

-- Create index on name for name-based queries
CREATE INDEX idx_servers_name ON servers(name);

-- Bot Permissions Table (for tracking bot permissions in each server)
CREATE TABLE bot_permissions (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    is_admin BOOLEAN DEFAULT FALSE,
    can_manage_channels BOOLEAN DEFAULT FALSE,
    can_manage_roles BOOLEAN DEFAULT FALSE,
    can_manage_messages BOOLEAN DEFAULT FALSE,
    can_mention_everyone BOOLEAN DEFAULT FALSE,
    can_embed_links BOOLEAN DEFAULT TRUE,
    can_attach_files BOOLEAN DEFAULT TRUE,
    can_use_external_emojis BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(server_id)
);

-- Create index on server_id for faster lookups
CREATE INDEX idx_bot_permissions_server_id ON bot_permissions(server_id);
