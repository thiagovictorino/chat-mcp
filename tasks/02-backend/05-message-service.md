# Task: Implement Message Service

## Description
Create the message service layer that handles sending messages, retrieving unread messages, message history, and automatic read tracking.

## Acceptance Criteria
- [ ] Send messages with @ mention parsing
- [ ] Retrieve unread messages (auto-marks as read)
- [ ] Get message history with pagination (auto-marks as read)
- [ ] Parse and validate mentions
- [ ] Track read status automatically
- [ ] Support message content up to 4000 chars

## Implementation Steps

1. Create `mcp_server/services/message_service.py`:
```python
from typing import List, Dict, Optional, Any
from datetime import datetime
from mcp_server.models.database import get_db
from mcp_server.utils.database import generate_uuid, dict_from_row, get_next_sequence_number, parse_mentions
from mcp_server.services.agent_service import validate_agent_in_channel, get_agent_by_username
import logging

logger = logging.getLogger(__name__)

class MessageError(Exception):
    """Message-related errors."""
    pass

async def send_message(channel_id: str, agent_id: str, content: str) -> Dict[str, Any]:
    """Send a message to a channel with @ mention support."""
    # Validate content length
    if not content or len(content) > 4000:
        raise MessageError("Message content must be 1-4000 characters")
    
    # Validate agent is in channel
    agent = await validate_agent_in_channel(agent_id, channel_id)
    
    # Parse mentions
    mentions = parse_mentions(content)
    
    async with get_db() as db:
        # Validate mentioned users exist in channel
        for username in mentions:
            mentioned_agent = await get_agent_by_username(channel_id, username)
            if not mentioned_agent:
                raise MessageError(f"Mentioned user @{username} not found in channel")
        
        # Get next sequence number
        sequence_number = await get_next_sequence_number(db, channel_id)
        message_id = generate_uuid()
        
        # Insert message
        await db.execute(
            """INSERT INTO messages (message_id, channel_id, agent_id, content, sequence_number)
               VALUES (?, ?, ?, ?, ?)""",
            (message_id, channel_id, agent_id, content, sequence_number)
        )
        
        # Insert mentions
        for username in mentions:
            await db.execute(
                """INSERT INTO message_mentions (message_id, mentioned_username)
                   VALUES (?, ?)""",
                (message_id, username)
            )
        
        # Mark as read by sender
        await db.execute(
            """INSERT INTO read_status (agent_id, message_id)
               VALUES (?, ?)""",
            (agent_id, message_id)
        )
        
        await db.commit()
        
        logger.info(f"Message {message_id} sent by {agent['username']} in channel {channel_id}")
        
        return {
            "message_id": message_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "sequence_number": sequence_number
        }

async def get_new_messages(channel_id: str, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve unread messages and automatically mark them as read."""
    # Validate agent is in channel
    agent = await validate_agent_in_channel(agent_id, channel_id)
    
    async with get_db() as db:
        # Get unread messages
        cursor = await db.execute(
            """SELECT m.*, a.username as sender_username
               FROM messages m
               JOIN agents a ON m.agent_id = a.agent_id
               WHERE m.channel_id = ?
               AND m.message_id NOT IN (
                   SELECT message_id FROM read_status WHERE agent_id = ?
               )
               AND m.created_at >= (
                   SELECT joined_at FROM agents WHERE agent_id = ?
               )
               ORDER BY m.sequence_number ASC
               LIMIT ?""",
            (channel_id, agent_id, agent_id, limit)
        )
        
        messages = []
        message_ids = []
        
        async for row in cursor:
            message_dict = dict_from_row(row)
            message_ids.append(message_dict['message_id'])
            
            # Get mentions
            mention_cursor = await db.execute(
                "SELECT mentioned_username FROM message_mentions WHERE message_id = ?",
                (message_dict['message_id'],)
            )
            mentions = [r['mentioned_username'] async for r in mention_cursor]
            
            # Get read_by info
            read_cursor = await db.execute(
                """SELECT r.agent_id, a.username, r.read_at
                   FROM read_status r
                   JOIN agents a ON r.agent_id = a.agent_id
                   WHERE r.message_id = ?""",
                (message_dict['message_id'],)
            )
            read_by = []
            async for r in read_cursor:
                read_by.append({
                    "agent_id": r['agent_id'],
                    "username": r['username'],
                    "read_at": r['read_at']
                })
            
            messages.append({
                "message_id": message_dict['message_id'],
                "sender": {
                    "agent_id": message_dict['agent_id'],
                    "username": message_dict['sender_username']
                },
                "content": message_dict['content'],
                "mentions": mentions,
                "timestamp": message_dict['created_at'],
                "sequence_number": message_dict['sequence_number'],
                "read_by": read_by
            })
        
        # Mark messages as read atomically
        if message_ids:
            placeholders = ','.join(['?'] * len(message_ids))
            await db.executemany(
                "INSERT OR IGNORE INTO read_status (agent_id, message_id) VALUES (?, ?)",
                [(agent_id, mid) for mid in message_ids]
            )
            await db.commit()
            logger.info(f"Marked {len(message_ids)} messages as read for agent {agent_id}")
        
        return messages

async def get_message_history(channel_id: str, agent_id: str, 
                            limit: int = 50, before_sequence: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieve message history and mark any unread messages as read."""
    # Validate agent is in channel
    agent = await validate_agent_in_channel(agent_id, channel_id)
    
    async with get_db() as db:
        # Build query based on before_sequence
        if before_sequence:
            query = """SELECT m.*, a.username as sender_username
                      FROM messages m
                      JOIN agents a ON m.agent_id = a.agent_id
                      WHERE m.channel_id = ?
                      AND m.sequence_number < ?
                      ORDER BY m.sequence_number DESC
                      LIMIT ?"""
            params = (channel_id, before_sequence, limit)
        else:
            query = """SELECT m.*, a.username as sender_username
                      FROM messages m
                      JOIN agents a ON m.agent_id = a.agent_id
                      WHERE m.channel_id = ?
                      ORDER BY m.sequence_number DESC
                      LIMIT ?"""
            params = (channel_id, limit)
        
        cursor = await db.execute(query, params)
        
        messages = []
        unread_message_ids = []
        
        async for row in cursor:
            message_dict = dict_from_row(row)
            
            # Check if unread
            read_check = await db.execute(
                "SELECT 1 FROM read_status WHERE agent_id = ? AND message_id = ?",
                (agent_id, message_dict['message_id'])
            )
            if not await read_check.fetchone():
                unread_message_ids.append(message_dict['message_id'])
            
            # Get mentions
            mention_cursor = await db.execute(
                "SELECT mentioned_username FROM message_mentions WHERE message_id = ?",
                (message_dict['message_id'],)
            )
            mentions = [r['mentioned_username'] async for r in mention_cursor]
            
            # Get read_by info
            read_cursor = await db.execute(
                """SELECT r.agent_id, a.username, r.read_at
                   FROM read_status r
                   JOIN agents a ON r.agent_id = a.agent_id
                   WHERE r.message_id = ?""",
                (message_dict['message_id'],)
            )
            read_by = []
            async for r in read_cursor:
                read_by.append({
                    "agent_id": r['agent_id'],
                    "username": r['username'],
                    "read_at": r['read_at']
                })
            
            messages.append({
                "message_id": message_dict['message_id'],
                "sender": {
                    "agent_id": message_dict['agent_id'],
                    "username": message_dict['sender_username']
                },
                "content": message_dict['content'],
                "mentions": mentions,
                "timestamp": message_dict['created_at'],
                "sequence_number": message_dict['sequence_number'],
                "read_by": read_by
            })
        
        # Mark unread messages as read
        if unread_message_ids:
            await db.executemany(
                "INSERT OR IGNORE INTO read_status (agent_id, message_id) VALUES (?, ?)",
                [(agent_id, mid) for mid in unread_message_ids]
            )
            await db.commit()
            logger.info(f"Marked {len(unread_message_ids)} historical messages as read for agent {agent_id}")
        
        # Reverse to get chronological order
        messages.reverse()
        return messages

async def get_agent_messages(channel_id: str, target_username: str, 
                           limit: int = 20) -> List[Dict[str, Any]]:
    """Get messages from a specific agent."""
    # Get target agent
    target_agent = await get_agent_by_username(channel_id, target_username)
    if not target_agent:
        raise MessageError(f"Agent @{target_username} not found in channel")
    
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT m.*, a.username as sender_username
               FROM messages m
               JOIN agents a ON m.agent_id = a.agent_id
               WHERE m.channel_id = ? AND m.agent_id = ?
               ORDER BY m.sequence_number DESC
               LIMIT ?""",
            (channel_id, target_agent['agent_id'], limit)
        )
        
        messages = []
        async for row in cursor:
            message_dict = dict_from_row(row)
            
            # Get mentions
            mention_cursor = await db.execute(
                "SELECT mentioned_username FROM message_mentions WHERE message_id = ?",
                (message_dict['message_id'],)
            )
            mentions = [r['mentioned_username'] async for r in mention_cursor]
            
            messages.append({
                "message_id": message_dict['message_id'],
                "sender": {
                    "agent_id": message_dict['agent_id'],
                    "username": message_dict['sender_username']
                },
                "content": message_dict['content'],
                "mentions": mentions,
                "timestamp": message_dict['created_at'],
                "sequence_number": message_dict['sequence_number']
            })
        
        messages.reverse()
        return messages
```

## Dependencies
- Agent service completed
- Database utilities ready

## Estimated Time: 1 hour