# Task: Implement Channel Service

## Description
Create the channel service layer that handles all channel-related business logic including creation, listing, and validation.

## Acceptance Criteria
- [ ] Create channel with unique name validation
- [ ] List channels with pagination
- [ ] Get channel by ID or name
- [ ] Validate channel constraints
- [ ] Handle all channel-related errors

## Implementation Steps

1. Create `mcp_server/services/channel_service.py`:
```python
from typing import List, Dict, Optional, Any
from mcp_server.models.database import get_db
from mcp_server.utils.database import generate_uuid, dict_from_row
import logging

logger = logging.getLogger(__name__)

class ChannelError(Exception):
    """Channel-related errors."""
    pass

async def create_channel(name: str, description: Optional[str] = None, 
                        max_agents: int = 50) -> Dict[str, Any]:
    """Create a new channel with unique name."""
    if not name or len(name) > 100:
        raise ChannelError("Channel name must be 1-100 characters")
    
    if max_agents < 2 or max_agents > 100:
        raise ChannelError("Max agents must be between 2 and 100")
    
    channel_id = generate_uuid()
    
    async with get_db() as db:
        try:
            await db.execute(
                """INSERT INTO channels (channel_id, name, description, max_agents)
                   VALUES (?, ?, ?, ?)""",
                (channel_id, name, description, max_agents)
            )
            await db.commit()
            
            logger.info(f"Created channel: {name} ({channel_id})")
            
            return {
                "channel_id": channel_id,
                "name": name,
                "description": description,
                "max_agents": max_agents,
                "created_at": None,  # Will be set by DB
                "is_active": True
            }
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ChannelError(f"Channel name '{name}' already exists")
            raise ChannelError(f"Failed to create channel: {str(e)}")

async def get_channel(channel_id: Optional[str] = None, 
                     name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get channel by ID or name."""
    if not channel_id and not name:
        raise ChannelError("Must provide channel_id or name")
    
    async with get_db() as db:
        if channel_id:
            cursor = await db.execute(
                "SELECT * FROM channels WHERE channel_id = ? AND is_active = 1",
                (channel_id,)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM channels WHERE name = ? AND is_active = 1",
                (name,)
            )
        
        row = await cursor.fetchone()
        return dict_from_row(row)

async def list_channels(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """List all active channels with pagination."""
    async with get_db() as db:
        # Get total count
        cursor = await db.execute(
            "SELECT COUNT(*) as total FROM channels WHERE is_active = 1"
        )
        total_row = await cursor.fetchone()
        total = total_row['total']
        
        # Get channels with agent count
        cursor = await db.execute(
            """SELECT c.*, COUNT(DISTINCT a.agent_id) as agent_count
               FROM channels c
               LEFT JOIN agents a ON c.channel_id = a.channel_id
               WHERE c.is_active = 1
               GROUP BY c.channel_id
               ORDER BY c.created_at DESC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        
        channels = []
        async for row in cursor:
            channels.append(dict_from_row(row))
        
        return {
            "channels": channels,
            "total": total,
            "has_more": offset + limit < total
        }

async def validate_channel_capacity(channel_id: str) -> None:
    """Check if channel has capacity for new agents."""
    channel = await get_channel(channel_id=channel_id)
    if not channel:
        raise ChannelError("Channel not found")
    
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) as count FROM agents WHERE channel_id = ?",
            (channel_id,)
        )
        row = await cursor.fetchone()
        current_agents = row['count']
        
        if current_agents >= channel['max_agents']:
            raise ChannelError(f"Channel has reached maximum capacity ({channel['max_agents']} agents)")
```

## Dependencies
- Database setup completed
- FastMCP server initialized

## Estimated Time: 45 minutes