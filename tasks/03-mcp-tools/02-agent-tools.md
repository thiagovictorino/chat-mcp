# Task: Implement Agent MCP Tools

## Description
Create MCP tools for agent operations: joining channels, leaving channels, and listing agents in channels.

## Acceptance Criteria
- [ ] Tool to join a channel with unique username
- [ ] Tool to leave a channel
- [ ] Tool to list agents in a channel
- [ ] Return agent_id on successful join
- [ ] Proper error messages for duplicate usernames

## Implementation Steps

1. Create `mcp_server/tools/agent.py`:
```python
from mcp_server.server import mcp
from mcp_server.services import agent_service, channel_service
import json

# Store agent sessions (in production, use proper session management)
agent_sessions = {}

@mcp.tool()
async def join_channel(channel_id: str, username: str, role_description: str) -> str:
    """
    Join a specific channel with a unique username.
    
    Args:
        channel_id: The UUID of the channel to join
        username: Unique username for the agent in this channel (3-50 alphanumeric chars)
        role_description: Brief description of the agent's role (10-200 chars)
    
    Returns:
        Success message with agent_id or error description
    """
    try:
        agent = await agent_service.join_channel(
            channel_id=channel_id,
            username=username,
            role_description=role_description
        )
        
        # Store session info
        agent_sessions[agent["agent_id"]] = {
            "channel_id": channel_id,
            "username": username
        }
        
        return json.dumps({
            "status": "success",
            "message": f"Successfully joined channel as @{username}",
            "agent_id": agent["agent_id"],
            "channel_id": agent["channel_id"],
            "username": agent["username"],
            "role": agent["role_description"]
        }, indent=2)
    except agent_service.AgentError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
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
async def leave_channel(channel_id: str, agent_id: str) -> str:
    """
    Leave a channel and cleanup agent presence.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The agent leaving the channel
    
    Returns:
        Confirmation of successful channel exit
    """
    try:
        await agent_service.leave_channel(
            channel_id=channel_id,
            agent_id=agent_id
        )
        
        # Clean up session
        if agent_id in agent_sessions:
            username = agent_sessions[agent_id].get("username", "unknown")
            del agent_sessions[agent_id]
        else:
            username = "unknown"
        
        return json.dumps({
            "status": "success",
            "message": f"Agent @{username} successfully left the channel"
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
async def list_channel_agents(channel_id: str) -> str:
    """
    List all agents currently in a channel.
    
    Args:
        channel_id: The UUID of the channel
    
    Returns:
        List of agents with usernames, roles, and join timestamps
    """
    try:
        agents = await agent_service.list_channel_agents(channel_id)
        
        # Format agent list
        agents_info = []
        for agent in agents:
            agents_info.append({
                "agent_id": agent["agent_id"],
                "username": agent["username"],
                "role": agent["role_description"],
                "joined_at": agent["joined_at"]
            })
        
        # Get channel info for context
        channel = await channel_service.get_channel(channel_id=channel_id)
        channel_name = channel["name"] if channel else "Unknown"
        
        return json.dumps({
            "status": "success",
            "channel_name": channel_name,
            "channel_id": channel_id,
            "agent_count": len(agents),
            "agents": agents_info
        }, indent=2)
    except agent_service.AgentError as e:
        return json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to list agents: {str(e)}"
        }, indent=2)

@mcp.tool()
async def get_my_agent_info(agent_id: str) -> str:
    """
    Get information about a specific agent.
    
    Args:
        agent_id: The agent's ID
    
    Returns:
        Agent details including channel membership
    """
    try:
        agent = await agent_service.get_agent(agent_id)
        
        if not agent:
            return json.dumps({
                "status": "error",
                "error": "Agent not found"
            }, indent=2)
        
        # Get channel info
        channel = await channel_service.get_channel(channel_id=agent["channel_id"])
        
        return json.dumps({
            "status": "success",
            "agent": {
                "agent_id": agent["agent_id"],
                "username": agent["username"],
                "role": agent["role_description"],
                "channel": {
                    "channel_id": agent["channel_id"],
                    "name": channel["name"] if channel else "Unknown"
                },
                "joined_at": agent["joined_at"]
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to get agent info: {str(e)}"
        }, indent=2)
```

## Dependencies
- Agent service implemented
- Channel tools completed

## Notes
- The agent_sessions dictionary is a simple in-memory store. In production, use proper session management.
- Agent IDs are returned to agents so they can use them in subsequent operations.

## Estimated Time: 30 minutes