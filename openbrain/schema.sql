-- Openbrain Schema
-- Persistent storage for SeikoClaw memory and state

-- Tiered Memories
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    tier TEXT CHECK(tier IN ('Core', 'Longterm', 'Midterm', 'Shortterm')) DEFAULT 'Shortterm',
    source TEXT,
    tags TEXT,
    weight REAL DEFAULT 1.0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learned Skills
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    example_usage TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project Snapshots
CREATE TABLE IF NOT EXISTS project_states (
    project_name TEXT PRIMARY KEY,
    current_branch TEXT,
    last_blocker TEXT,
    next_step TEXT,
    checkpoint_data JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Secrets Vault (Encrypted)
CREATE TABLE IF NOT EXISTS secrets_vault (
    secret_key TEXT PRIMARY KEY,
    encrypted_value TEXT NOT NULL,
    salt TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage Statistics
CREATE TABLE IF NOT EXISTS usage_stats (
    stat_date DATE DEFAULT (DATE('now')),
    provider TEXT NOT NULL, -- 'anthropic', 'google', etc.
    tokens_used INTEGER DEFAULT 0,
    requests_count INTEGER DEFAULT 0,
    PRIMARY KEY (stat_date, provider)
);
