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