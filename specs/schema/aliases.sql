-- Server Aliases Table
CREATE TABLE server_aliases (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(server_id, alias)
);

-- Create index on server_id for faster lookups
CREATE INDEX idx_server_aliases_server_id ON server_aliases(server_id);

-- Create index on alias for alias-based queries
CREATE INDEX idx_server_aliases_alias ON server_aliases(alias);

-- Channel Aliases Table
CREATE TABLE channel_aliases (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(channel_id, alias)
);

-- Create index on channel_id for faster lookups
CREATE INDEX idx_channel_aliases_channel_id ON channel_aliases(channel_id);

-- Create index on alias for alias-based queries
CREATE INDEX idx_channel_aliases_alias ON channel_aliases(alias);

-- Role Aliases Table
CREATE TABLE role_aliases (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(role_id, alias)
);

-- Create index on role_id for faster lookups
CREATE INDEX idx_role_aliases_role_id ON role_aliases(role_id);

-- Create index on alias for alias-based queries
CREATE INDEX idx_role_aliases_alias ON role_aliases(alias);

-- Name Resolution Log Table (for tracking and improving alias resolution)
CREATE TABLE name_resolution_log (
    id SERIAL PRIMARY KEY,
    input_text VARCHAR(255) NOT NULL,
    resolved_type VARCHAR(50), -- server, channel, role
    resolved_id INTEGER,
    confidence FLOAT,
    was_correct BOOLEAN,
    context JSONB, -- Additional context that helped with resolution
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on input_text for text-based queries
CREATE INDEX idx_name_resolution_log_input_text ON name_resolution_log(input_text);

-- Create index on resolved_type for type-based queries
CREATE INDEX idx_name_resolution_log_resolved_type ON name_resolution_log(resolved_type);