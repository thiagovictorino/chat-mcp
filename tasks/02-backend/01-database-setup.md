# Task: Database Schema Implementation

## Description
Implement the SQLite database schema with all tables, indexes, and initial setup scripts.

## Acceptance Criteria
- [ ] All tables created as per PRD schema
- [ ] Proper indexes for performance
- [ ] Foreign key constraints enforced
- [ ] WAL mode enabled for concurrent access
- [ ] Migration script created

## Implementation Steps

1. Create `mcp_server/models/database.py`:
```python
import sqlite3
import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
import os

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/chat.db')

SCHEMA = """
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for concurrent access
PRAGMA journal_mode = WAL;

-- Channels Table
CREATE TABLE IF NOT EXISTS channels (
    channel_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    max_agents INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Agents Table
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    username TEXT NOT NULL,
    role_description TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    UNIQUE(channel_id, username)
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id) ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
);

-- Message Mentions Table
CREATE TABLE IF NOT EXISTS message_mentions (
    message_id TEXT NOT NULL,
    mentioned_username TEXT NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
    PRIMARY KEY (message_id, mentioned_username)
);

-- Read Status Table
CREATE TABLE IF NOT EXISTS read_status (
    agent_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON DELETE CASCADE,
    PRIMARY KEY (agent_id, message_id)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_messages_channel_sequence 
    ON messages(channel_id, sequence_number DESC);
CREATE INDEX IF NOT EXISTS idx_messages_agent 
    ON messages(agent_id);
CREATE INDEX IF NOT EXISTS idx_read_status_agent 
    ON read_status(agent_id);
CREATE INDEX IF NOT EXISTS idx_agents_channel 
    ON agents(channel_id);
CREATE INDEX IF NOT EXISTS idx_channels_name 
    ON channels(name);
"""

async def init_database():
    """Initialize database with schema."""
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()

@asynccontextmanager
async def get_db():
    """Get database connection."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
```

2. Create `mcp_server/utils/database.py`:
```python
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

def generate_uuid() -> str:
    """Generate a UUID v4."""
    return str(uuid.uuid4())

def dict_from_row(row) -> Dict[str, Any]:
    """Convert SQLite Row to dictionary."""
    if row is None:
        return None
    return dict(row)

async def get_next_sequence_number(db, channel_id: str) -> int:
    """Get next sequence number for a channel."""
    cursor = await db.execute(
        "SELECT COALESCE(MAX(sequence_number), 0) + 1 as next_seq FROM messages WHERE channel_id = ?",
        (channel_id,)
    )
    row = await cursor.fetchone()
    return row['next_seq']

def parse_mentions(content: str) -> List[str]:
    """Extract @mentions from message content."""
    import re
    pattern = r'@([a-zA-Z0-9_-]+)'
    return re.findall(pattern, content)
```

## Dependencies
- Infrastructure tasks completed
- aiosqlite package available

## Estimated Time: 45 minutes