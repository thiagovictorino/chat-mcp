from mcp_server.server import mcp
from mcp_server.services import message_service, agent_service
import json
from typing import Optional

@mcp.tool()
async def send_message(channel_id: str, agent_id: str, content: str) -> str:
    """
    Send a message to a channel. Supports @ mentions.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The sending agent's ID
        content: Message content (max 4000 chars). Use @username for mentions.
    
    Returns:
        Success confirmation with message_id and timestamp
    """
    try:
        result = await message_service.send_message(
            channel_id=channel_id,
            agent_id=agent_id,
            content=content
        )
        
        # Get agent info for better response
        agent = await agent_service.get_agent(agent_id)
        username = agent["username"] if agent else "unknown"
        
        return json.dumps({
            "status": "success",
            "message": f"Message sent by @{username}",
            "message_id": result["message_id"],
            "timestamp": result["timestamp"],
            "sequence_number": result["sequence_number"]
        }, indent=2)
    except message_service.MessageError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2)
    except agent_service.AgentError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }, indent=2)

@mcp.tool()
async def get_new_messages(channel_id: str, agent_id: str, limit: int = 50) -> str:
    """
    Retrieve unread messages from a channel. Retrieved messages are automatically 
    marked as read by the requesting agent.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The requesting agent's ID
        limit: Maximum number of messages to return (default: 50)
    
    Returns:
        List of unread messages with sender info, content, timestamps, and read status.
        Note: These messages are now marked as read by this agent.
    """
    try:
        messages = await message_service.get_new_messages(
            channel_id=channel_id,
            agent_id=agent_id,
            limit=limit
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": msg["message_id"],
                "sender": {
                    "agent_id": msg["sender"]["agent_id"],
                    "username": msg["sender"]["username"]
                },
                "content": msg["content"],
                "mentions": msg["mentions"],
                "timestamp": msg["timestamp"],
                "sequence_number": msg["sequence_number"],
                "read_by": [
                    {
                        "username": reader["username"],
                        "read_at": reader["read_at"]
                    }
                    for reader in msg["read_by"]
                ]
            })
        
        # Get agent info
        agent = await agent_service.get_agent(agent_id)
        username = agent["username"] if agent else "unknown"
        
        return json.dumps({
            "status": "success",
            "agent": f"@{username}",
            "new_messages_count": len(messages),
            "messages": formatted_messages,
            "note": f"All {len(messages)} messages have been marked as read"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to get new messages: {str(e)}"
        }, indent=2)

@mcp.tool()
async def get_message_history(
    channel_id: str, 
    agent_id: str, 
    limit: int = 50, 
    before_sequence: Optional[int] = None
) -> str:
    """
    Retrieve message history from a channel. Any unread messages in the 
    retrieved set are automatically marked as read by the requesting agent.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The requesting agent's ID
        limit: Maximum number of messages to return
        before_sequence: Get messages before this sequence number (for pagination)
    
    Returns:
        List of historical messages ordered by timestamp.
        Note: Any previously unread messages are now marked as read by this agent.
    """
    try:
        messages = await message_service.get_message_history(
            channel_id=channel_id,
            agent_id=agent_id,
            limit=limit,
            before_sequence=before_sequence
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": msg["message_id"],
                "sender": {
                    "agent_id": msg["sender"]["agent_id"],
                    "username": msg["sender"]["username"]
                },
                "content": msg["content"],
                "mentions": msg["mentions"],
                "timestamp": msg["timestamp"],
                "sequence_number": msg["sequence_number"],
                "read_by": [
                    {
                        "username": reader["username"],
                        "read_at": reader["read_at"]
                    }
                    for reader in msg["read_by"]
                ]
            })
        
        # Pagination info
        pagination_info = {
            "returned": len(messages),
            "limit": limit
        }
        if before_sequence:
            pagination_info["before_sequence"] = before_sequence
        if messages:
            pagination_info["oldest_sequence"] = messages[0]["sequence_number"]
            pagination_info["newest_sequence"] = messages[-1]["sequence_number"]
        
        return json.dumps({
            "status": "success",
            "message_count": len(messages),
            "messages": formatted_messages,
            "pagination": pagination_info,
            "note": "Any previously unread messages have been marked as read"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to get message history: {str(e)}"
        }, indent=2)

@mcp.tool()
async def get_agent_messages(channel_id: str, agent_username: str, limit: int = 20) -> str:
    """
    Get recent messages from a specific agent in a channel.
    
    Args:
        channel_id: The UUID of the channel
        agent_username: The username of the agent whose messages to retrieve
        limit: Maximum number of messages to return (default: 20)
    
    Returns:
        List of messages from the specified agent
    """
    try:
        messages = await message_service.get_agent_messages(
            channel_id=channel_id,
            target_username=agent_username,
            limit=limit
        )
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": msg["message_id"],
                "content": msg["content"],
                "mentions": msg["mentions"],
                "timestamp": msg["timestamp"],
                "sequence_number": msg["sequence_number"]
            })
        
        return json.dumps({
            "status": "success",
            "agent": f"@{agent_username}",
            "message_count": len(messages),
            "messages": formatted_messages
        }, indent=2)
    except message_service.MessageError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to get agent messages: {str(e)}"
        }, indent=2)

@mcp.tool()
async def check_mentions(channel_id: str, agent_id: str, limit: int = 20) -> str:
    """
    Check for messages where the agent was mentioned.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The agent's ID
        limit: Maximum number of messages to return
    
    Returns:
        List of messages that mention this agent
    """
    try:
        # Get agent info to get username
        agent = await agent_service.get_agent(agent_id)
        if not agent:
            return json.dumps({
                "status": "error",
                "error": "Agent not found"
            }, indent=2)
        
        username = agent["username"]
        
        # Get recent messages and filter for mentions
        messages = await message_service.get_message_history(
            channel_id=channel_id,
            agent_id=agent_id,
            limit=limit * 2  # Get more to filter
        )
        
        # Filter messages that mention this agent
        mentioned_messages = []
        for msg in messages:
            if username in msg["mentions"]:
                mentioned_messages.append({
                    "message_id": msg["message_id"],
                    "sender": {
                        "agent_id": msg["sender"]["agent_id"],
                        "username": msg["sender"]["username"]
                    },
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "read_by": [
                        {
                            "username": reader["username"],
                            "read_at": reader["read_at"]
                        }
                        for reader in msg["read_by"]
                    ]
                })
        
        # Limit results
        mentioned_messages = mentioned_messages[:limit]
        
        return json.dumps({
            "status": "success",
            "agent": f"@{username}",
            "mentions_count": len(mentioned_messages),
            "messages": mentioned_messages,
            "note": "Messages have been marked as read"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to check mentions: {str(e)}"
        }, indent=2)