import re
from typing import List, Dict, Optional, Any
from mcp_server.models.database import get_db
from mcp_server.utils.database import generate_uuid, dict_from_row
from mcp_server.services.channel_service import get_channel, validate_channel_capacity
import logging

logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Agent-related errors."""
    pass

# Username validation pattern
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')

async def join_channel(channel_id: str, username: str, 
                      role_description: str) -> Dict[str, Any]:
    """Join a channel with unique username."""
    # Validate inputs
    if not USERNAME_PATTERN.match(username):
        raise AgentError("Username must be 3-50 alphanumeric characters (hyphens/underscores allowed)")
    
    if not role_description or len(role_description) < 10 or len(role_description) > 200:
        raise AgentError("Role description must be 10-200 characters")
    
    # Validate channel exists and has capacity
    channel = await get_channel(channel_id=channel_id)
    if not channel:
        raise AgentError("Channel not found")
    
    await validate_channel_capacity(channel_id)
    
    agent_id = generate_uuid()
    
    async with get_db() as db:
        try:
            await db.execute(
                """INSERT INTO agents (agent_id, channel_id, username, role_description)
                   VALUES (?, ?, ?, ?)""",
                (agent_id, channel_id, username, role_description)
            )
            await db.commit()
            
            logger.info(f"Agent {username} ({agent_id}) joined channel {channel_id}")
            
            return {
                "agent_id": agent_id,
                "channel_id": channel_id,
                "username": username,
                "role_description": role_description,
                "joined_at": None  # Will be set by DB
            }
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise AgentError(f"Username '{username}' already exists in this channel")
            raise AgentError(f"Failed to join channel: {str(e)}")

async def leave_channel(channel_id: str, agent_id: str) -> None:
    """Leave a channel and cleanup agent presence."""
    async with get_db() as db:
        # Verify agent exists in channel
        cursor = await db.execute(
            "SELECT agent_id FROM agents WHERE agent_id = ? AND channel_id = ?",
            (agent_id, channel_id)
        )
        if not await cursor.fetchone():
            raise AgentError("Agent not found in channel")
        
        # Delete agent (cascading will clean up read status)
        await db.execute(
            "DELETE FROM agents WHERE agent_id = ? AND channel_id = ?",
            (agent_id, channel_id)
        )
        await db.commit()
        
        logger.info(f"Agent {agent_id} left channel {channel_id}")

async def get_agent(agent_id: str, channel_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get agent by ID, optionally filtered by channel."""
    async with get_db() as db:
        if channel_id:
            cursor = await db.execute(
                "SELECT * FROM agents WHERE agent_id = ? AND channel_id = ?",
                (agent_id, channel_id)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM agents WHERE agent_id = ?",
                (agent_id,)
            )
        
        row = await cursor.fetchone()
        return dict_from_row(row)

async def get_agent_by_username(channel_id: str, username: str) -> Optional[Dict[str, Any]]:
    """Get agent by username in a specific channel."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM agents WHERE channel_id = ? AND username = ?",
            (channel_id, username)
        )
        row = await cursor.fetchone()
        return dict_from_row(row)

async def list_channel_agents(channel_id: str) -> List[Dict[str, Any]]:
    """List all agents in a channel."""
    # Verify channel exists
    channel = await get_channel(channel_id=channel_id)
    if not channel:
        raise AgentError("Channel not found")
    
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT agent_id, username, role_description, joined_at
               FROM agents
               WHERE channel_id = ?
               ORDER BY joined_at ASC""",
            (channel_id,)
        )
        
        agents = []
        async for row in cursor:
            agents.append(dict_from_row(row))
        
        return agents

async def validate_agent_in_channel(agent_id: str, channel_id: str) -> Dict[str, Any]:
    """Validate agent exists in channel and return agent info."""
    agent = await get_agent(agent_id, channel_id)
    if not agent:
        raise AgentError("Agent not found in channel")
    return agent