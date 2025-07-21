-- Roles Table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    discord_id VARCHAR(255) NOT NULL UNIQUE,
    server_id INTEGER REFERENCES servers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    color INTEGER,
    position INTEGER,
    is_mentionable BOOLEAN DEFAULT FALSE,
    is_managed BOOLEAN DEFAULT FALSE, -- For roles managed by integrations
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on discord_id for faster lookups
CREATE INDEX idx_roles_discord_id ON roles(discord_id);

-- Create index on server_id for server-based queries
CREATE INDEX idx_roles_server_id ON roles(server_id);

-- Create index on name for name-based queries
CREATE INDEX idx_roles_name ON roles(name);

-- Role Permissions Table
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_name VARCHAR(255) NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(role_id, permission_name)
);

-- Create index on role_id for faster lookups
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);

-- Create index on permission_name for permission-based queries
CREATE INDEX idx_role_permissions_permission_name ON role_permissions(permission_name);