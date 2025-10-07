-- Message Styles Table
CREATE TABLE message_styles (
    id SERIAL PRIMARY KEY,
    style_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tone VARCHAR(50), -- formal, casual, energetic, serious, etc.
    emoji_level VARCHAR(20), -- none, low, medium, high
    structure JSONB NOT NULL, -- Contains header, intro, body, sections, footer templates
    emoji_map JSONB, -- Maps concepts to emojis
    formatting_rules JSONB, -- Contains formatting preferences
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on style_id for faster lookups
CREATE INDEX idx_message_styles_style_id ON message_styles(style_id);

-- Create index on name for name-based queries
CREATE INDEX idx_message_styles_name ON message_styles(name);

-- Server Style Mappings Table
CREATE TABLE server_style_mappings (
    id SERIAL PRIMARY KEY,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    message_type VARCHAR(50), -- default, announcement, event, question, welcome, etc.
    style_id VARCHAR(255) REFERENCES message_styles(style_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(server_id, message_type)
);

-- Create index on server_id for server-based queries
CREATE INDEX idx_server_style_mappings_server_id ON server_style_mappings(server_id);

-- Create index on message_type for type-based queries
CREATE INDEX idx_server_style_mappings_message_type ON server_style_mappings(message_type);

-- Channel Style Mappings Table
CREATE TABLE channel_style_mappings (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER REFERENCES channels(id) ON DELETE CASCADE,
    style_id VARCHAR(255) REFERENCES message_styles(style_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(channel_id)
);

-- Create index on channel_id for channel-based queries
CREATE INDEX idx_channel_style_mappings_channel_id ON channel_style_mappings(channel_id);

-- Style Templates Table
CREATE TABLE style_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) NOT NULL, -- announcement, event, question, welcome, etc.
    content JSONB NOT NULL, -- The template structure with placeholders
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on template_id for faster lookups
CREATE INDEX idx_style_templates_template_id ON style_templates(template_id);

-- Create index on template_type for type-based queries
CREATE INDEX idx_style_templates_template_type ON style_templates(template_type);
