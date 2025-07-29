from mcp_server.server import mcp
from mcp_server.services import channel_service
import json

@mcp.tool()
async def create_channel(name: str, description: str = "", max_agents: int = 50) -> str:
    """
    Create a new channel for agent communication.
    
    Args:
        name: Unique channel name (1-100 characters)
        description: Optional channel description (max 500 characters)
        max_agents: Maximum number of agents allowed (2-100, default: 50)
    
    Returns:
        Success message with channel details or error description
    """
    try:
        channel = await channel_service.create_channel(
            name=name,
            description=description,
            max_agents=max_agents
        )
        return json.dumps({
            "status": "success",
            "message": f"Channel '{name}' created successfully",
            "channel": {
                "channel_id": channel["channel_id"],
                "name": channel["name"],
                "description": channel["description"],
                "max_agents": channel["max_agents"]
            }
        }, indent=2)
    except channel_service.ChannelError as e:
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
async def list_channels(limit: int = 20, offset: int = 0) -> str:
    """
    List all available channels.
    
    Args:
        limit: Maximum number of channels to return (default: 20)
        offset: Pagination offset (default: 0)
    
    Returns:
        List of channels with names, IDs, and agent counts
    """
    try:
        result = await channel_service.list_channels(limit=limit, offset=offset)
        
        # Format channel list
        channels_info = []
        for channel in result["channels"]:
            channels_info.append({
                "channel_id": channel["channel_id"],
                "name": channel["name"],
                "description": channel.get("description", ""),
                "agent_count": channel["agent_count"],
                "max_agents": channel["max_agents"],
                "created_at": channel["created_at"]
            })
        
        return json.dumps({
            "status": "success",
            "channels": channels_info,
            "total": result["total"],
            "has_more": result["has_more"],
            "showing": f"{offset + 1}-{min(offset + limit, result['total'])} of {result['total']}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to list channels: {str(e)}"
        }, indent=2)

@mcp.tool()
async def get_channel_info(channel_name: str = None, channel_id: str = None) -> str:
    """
    Get detailed information about a specific channel.
    
    Args:
        channel_name: Channel name (provide either name or ID)
        channel_id: Channel ID (provide either name or ID)
    
    Returns:
        Channel details including current agents
    """
    try:
        if not channel_name and not channel_id:
            return json.dumps({
                "status": "error",
                "error": "Must provide either channel_name or channel_id"
            }, indent=2)
        
        # Get channel info
        channel = await channel_service.get_channel(
            channel_id=channel_id,
            name=channel_name
        )
        
        if not channel:
            return json.dumps({
                "status": "error",
                "error": "Channel not found"
            }, indent=2)
        
        # Get agents in channel
        from mcp_server.services.agent_service import list_channel_agents
        agents = await list_channel_agents(channel["channel_id"])
        
        return json.dumps({
            "status": "success",
            "channel": {
                "channel_id": channel["channel_id"],
                "name": channel["name"],
                "description": channel.get("description", ""),
                "max_agents": channel["max_agents"],
                "current_agents": len(agents),
                "created_at": channel["created_at"],
                "agents": [
                    {
                        "username": agent["username"],
                        "role": agent["role_description"],
                        "joined_at": agent["joined_at"]
                    }
                    for agent in agents
                ]
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to get channel info: {str(e)}"
        }, indent=2)