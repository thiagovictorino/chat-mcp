from fastapi import APIRouter, HTTPException
from mcp_server.services import channel_service, agent_service, message_service
from typing import Optional

router = APIRouter()

# Channel endpoints
@router.get("/channels")
async def list_channels(limit: int = 20, offset: int = 0):
    try:
        return await channel_service.list_channels(limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels")
async def create_channel(data: dict):
    try:
        return await channel_service.create_channel(
            name=data["name"],
            description=data.get("description"),
            max_agents=data.get("max_agents", 50)
        )
    except channel_service.ChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/channels/{channel_id}")
async def delete_channel(channel_id: str):
    try:
        # First check if channel exists
        from mcp_server.models.database import get_db
        async with get_db() as db:
            # Delete all related data in correct order
            await db.execute("DELETE FROM read_status WHERE message_id IN (SELECT message_id FROM messages WHERE channel_id = ?)", (channel_id,))
            await db.execute("DELETE FROM message_mentions WHERE message_id IN (SELECT message_id FROM messages WHERE channel_id = ?)", (channel_id,))
            await db.execute("DELETE FROM messages WHERE channel_id = ?", (channel_id,))
            await db.execute("DELETE FROM agents WHERE channel_id = ?", (channel_id,))
            result = await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            await db.commit()
            
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="Channel not found")
                
        return {"status": "success", "message": f"Channel {channel_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent endpoints
@router.get("/channels/{channel_id}/agents")
async def list_agents(channel_id: str):
    try:
        agents = await agent_service.list_channel_agents(channel_id)
        return {"agents": agents}
    except agent_service.AgentError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Message endpoints
@router.get("/channels/{channel_id}/messages")
async def get_messages(
    channel_id: str, 
    agent_id: Optional[str] = None,
    limit: int = 50
):
    try:
        # For UI, we don't mark as read - just retrieve
        from mcp_server.models.database import get_db
        from mcp_server.utils.database import dict_from_row
        
        async with get_db() as db:
            cursor = await db.execute(
                """SELECT m.*, a.username as sender_username
                   FROM messages m
                   JOIN agents a ON m.agent_id = a.agent_id
                   WHERE m.channel_id = ?
                   ORDER BY m.sequence_number DESC
                   LIMIT ?""",
                (channel_id, limit)
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
            
            messages.reverse()  # Return in chronological order
            return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Logs endpoint
@router.get("/logs")
async def get_logs(limit: int = 100):
    try:
        import os
        log_file = os.getenv('LOG_FILE_PATH', '/app/logs/chat-mcp.log')
        
        if not os.path.exists(log_file):
            return {"logs": []}
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Return last N lines
            return {"logs": lines[-limit:]}
    except Exception as e:
        return {"logs": [], "error": str(e)}