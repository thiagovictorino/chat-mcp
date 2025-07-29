import pytest
import json
from mcp_server.tools import channel, agent, messaging

@pytest.mark.asyncio
async def test_channel_tools(test_db):
    """Test channel MCP tools."""
    # Create channel
    result = await channel.create_channel(
        name="mcp-tool-test",
        description="Testing MCP tools",
        max_agents=5
    )
    data = json.loads(result)
    assert data["status"] == "success"
    channel_id = data["channel"]["channel_id"]
    
    # List channels
    result = await channel.list_channels()
    data = json.loads(result)
    assert data["status"] == "success"
    assert any(ch["name"] == "mcp-tool-test" for ch in data["channels"])
    
    # Get channel info
    result = await channel.get_channel_info(channel_name="mcp-tool-test")
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["channel"]["name"] == "mcp-tool-test"

@pytest.mark.asyncio
async def test_agent_tools(test_db):
    """Test agent MCP tools."""
    # Create channel first
    channel_result = await channel.create_channel(name="agent-tool-test")
    channel_data = json.loads(channel_result)
    channel_id = channel_data["channel"]["channel_id"]
    
    # Join channel
    result = await agent.join_channel(
        channel_id=channel_id,
        username="test-agent",
        role_description="Testing agent tools"
    )
    data = json.loads(result)
    assert data["status"] == "success"
    agent_id = data["agent_id"]
    
    # List agents
    result = await agent.list_channel_agents(channel_id)
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["agent_count"] == 1
    
    # Get agent info
    result = await agent.get_my_agent_info(agent_id)
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["agent"]["username"] == "test-agent"
    
    # Leave channel
    result = await agent.leave_channel(channel_id, agent_id)
    data = json.loads(result)
    assert data["status"] == "success"

@pytest.mark.asyncio
async def test_messaging_tools(test_db):
    """Test messaging MCP tools."""
    # Setup channel and agents
    channel_result = await channel.create_channel(name="message-tool-test")
    channel_data = json.loads(channel_result)
    channel_id = channel_data["channel"]["channel_id"]
    
    # Create two agents
    agent1_result = await agent.join_channel(
        channel_id=channel_id,
        username="sender",
        role_description="Message sender agent"
    )
    agent1_data = json.loads(agent1_result)
    agent1_id = agent1_data["agent_id"]
    
    agent2_result = await agent.join_channel(
        channel_id=channel_id,
        username="receiver",
        role_description="Message receiver agent"
    )
    agent2_data = json.loads(agent2_result)
    agent2_id = agent2_data["agent_id"]
    
    # Send message
    result = await messaging.send_message(
        channel_id=channel_id,
        agent_id=agent1_id,
        content="Hello @receiver, this is a test!"
    )
    data = json.loads(result)
    assert data["status"] == "success"
    
    # Get new messages
    result = await messaging.get_new_messages(
        channel_id=channel_id,
        agent_id=agent2_id
    )
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["new_messages_count"] == 1
    assert "@receiver" in data["messages"][0]["content"]
    
    # Get message history
    result = await messaging.get_message_history(
        channel_id=channel_id,
        agent_id=agent1_id
    )
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["message_count"] == 1
    
    # Check mentions
    result = await messaging.check_mentions(
        channel_id=channel_id,
        agent_id=agent2_id
    )
    data = json.loads(result)
    assert data["status"] == "success"
    assert data["mentions_count"] == 1

@pytest.mark.asyncio
async def test_error_handling(test_db):
    """Test MCP tools error handling."""
    # Try to join non-existent channel
    result = await agent.join_channel(
        channel_id="non-existent",
        username="test",
        role_description="Test description"
    )
    data = json.loads(result)
    assert data["status"] == "error"
    assert "not found" in data["error"].lower()
    
    # Try to create channel with invalid name
    result = await channel.create_channel(name="")
    data = json.loads(result)
    assert data["status"] == "error"
    assert "1-100 characters" in data["error"]