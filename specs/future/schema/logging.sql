-- Tool Usage Log Table
CREATE TABLE tool_usage_log (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    server_id INTEGER REFERENCES servers(id) ON DELETE SET NULL,
    discord_guild_id VARCHAR(255), -- Keeping for backward compatibility
    channel_id INTEGER REFERENCES channels(id) ON DELETE SET NULL,
    discord_channel_id VARCHAR(255), -- Keeping for backward compatibility
    parameters JSONB,
    result_status VARCHAR(50),
    execution_time FLOAT,
    timestamp TIMESTAMP DEFAULT NOW(),
    error_message TEXT
);

-- Create index on tool_name for tool-based queries
CREATE INDEX idx_tool_usage_log_tool_name ON tool_usage_log(tool_name);

-- Create index on user_id for user-based queries
CREATE INDEX idx_tool_usage_log_user_id ON tool_usage_log(user_id);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_tool_usage_log_guild_id ON tool_usage_log(guild_id);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_tool_usage_log_timestamp ON tool_usage_log(timestamp);

-- Tool Status Table (for enabling/disabling tools)
CREATE TABLE tool_status (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(255) NOT NULL,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255) NOT NULL, -- Keeping for backward compatibility
    enabled BOOLEAN DEFAULT TRUE,
    disabled_reason TEXT,
    disabled_until TIMESTAMP,
    disabled_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tool_name, server_id)
);

-- Create index on tool_name for tool-based queries
CREATE INDEX idx_tool_status_tool_name ON tool_status(tool_name);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_tool_status_guild_id ON tool_status(guild_id);

-- Error Log Table
CREATE TABLE error_log (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(255) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    user_id VARCHAR(255),
    server_id INTEGER REFERENCES servers(id) ON DELETE SET NULL,
    discord_guild_id VARCHAR(255), -- Keeping for backward compatibility
    channel_id INTEGER REFERENCES channels(id) ON DELETE SET NULL,
    discord_channel_id VARCHAR(255), -- Keeping for backward compatibility
    related_tool VARCHAR(255),
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create index on error_type for error-based queries
CREATE INDEX idx_error_log_error_type ON error_log(error_type);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_error_log_timestamp ON error_log(timestamp);

-- Create index on related_tool for tool-based queries
CREATE INDEX idx_error_log_related_tool ON error_log(related_tool);

-- Audit Log Table (for sensitive operations)
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    target_id VARCHAR(255),
    target_type VARCHAR(50),
    details JSONB,
    server_id INTEGER REFERENCES servers(id) ON DELETE SET NULL,
    discord_guild_id VARCHAR(255), -- Keeping for backward compatibility
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create index on action_type for action-based queries
CREATE INDEX idx_audit_log_action_type ON audit_log(action_type);

-- Create index on user_id for user-based queries
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);

-- Create index on guild_id for guild-based queries
CREATE INDEX idx_audit_log_guild_id ON audit_log(guild_id);

-- Create index on timestamp for time-based queries
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);

-- Rate Limit Table
CREATE TABLE rate_limits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    tool_name VARCHAR(255) NOT NULL,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    discord_guild_id VARCHAR(255), -- Keeping for backward compatibility
    request_count INTEGER DEFAULT 1,
    first_request TIMESTAMP DEFAULT NOW(),
    last_request TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, tool_name, server_id)
);

-- Create index on user_id for user-based queries
CREATE INDEX idx_rate_limits_user_id ON rate_limits(user_id);

-- Create index on tool_name for tool-based queries
CREATE INDEX idx_rate_limits_tool_name ON rate_limits(tool_name);

-- Create index on last_request for time-based queries
CREATE INDEX idx_rate_limits_last_request ON rate_limits(last_request);
