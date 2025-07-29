import pytest
from mcp_server.services.agent_service import (
    join_channel, leave_channel, get_agent, 
    list_channel_agents, AgentError
)

@pytest.mark.asyncio
async def test_join_channel(test_db, sample_channel):
    """Test agent joining a channel."""
    agent = await join_channel(
        channel_id=sample_channel["channel_id"],
        username="new-agent",
        role_description="Test agent role"
    )
    
    assert agent["username"] == "new-agent"
    assert agent["role_description"] == "Test agent role"
    assert agent["agent_id"] is not None

@pytest.mark.asyncio
async def test_duplicate_username(test_db, sample_channel):
    """Test that duplicate usernames are rejected."""
    await join_channel(
        sample_channel["channel_id"], 
        "duplicate-user", 
        "First agent"
    )
    
    with pytest.raises(AgentError, match="already exists"):
        await join_channel(
            sample_channel["channel_id"], 
            "duplicate-user", 
            "Second agent"
        )

@pytest.mark.asyncio
async def test_username_validation(test_db, sample_channel):
    """Test username validation rules."""
    # Too short
    with pytest.raises(AgentError, match="3-50 alphanumeric"):
        await join_channel(
            sample_channel["channel_id"], 
            "ab", 
            "Test agent role"
        )
    
    # Too long
    with pytest.raises(AgentError, match="3-50 alphanumeric"):
        await join_channel(
            sample_channel["channel_id"], 
            "a" * 51, 
            "Test agent role"
        )
    
    # Invalid characters
    with pytest.raises(AgentError, match="3-50 alphanumeric"):
        await join_channel(
            sample_channel["channel_id"], 
            "user@name", 
            "Test agent role"
        )
    
    # Valid special chars
    agent = await join_channel(
        sample_channel["channel_id"], 
        "user_name-123", 
        "Test agent role"
    )
    assert agent["username"] == "user_name-123"

@pytest.mark.asyncio
async def test_role_description_validation(test_db, sample_channel):
    """Test role description validation."""
    # Too short
    with pytest.raises(AgentError, match="10-200 characters"):
        await join_channel(
            sample_channel["channel_id"], 
            "valid-user", 
            "short"
        )
    
    # Too long
    with pytest.raises(AgentError, match="10-200 characters"):
        await join_channel(
            sample_channel["channel_id"], 
            "valid-user", 
            "a" * 201
        )

@pytest.mark.asyncio
async def test_leave_channel(test_db, sample_channel, sample_agent):
    """Test agent leaving a channel."""
    # Leave channel
    await leave_channel(
        sample_channel["channel_id"], 
        sample_agent["agent_id"]
    )
    
    # Verify agent is removed
    agent = await get_agent(sample_agent["agent_id"])
    assert agent is None
    
    # Test leaving non-existent agent
    with pytest.raises(AgentError, match="not found"):
        await leave_channel(
            sample_channel["channel_id"], 
            "non-existent"
        )

@pytest.mark.asyncio
async def test_list_agents(test_db, sample_channel):
    """Test listing agents in a channel."""
    # Add multiple agents
    agents = []
    for i in range(3):
        agent = await join_channel(
            sample_channel["channel_id"],
            f"list-agent-{i}",
            f"Test agent {i} role"
        )
        agents.append(agent)
    
    # List agents (including the sample_channel fixture agent)
    agent_list = await list_channel_agents(sample_channel["channel_id"])
    assert len(agent_list) >= 3
    
    # Verify all agents are present
    usernames = [a["username"] for a in agent_list]
    for i in range(3):
        assert f"list-agent-{i}" in usernames

@pytest.mark.asyncio
async def test_agent_not_found_in_channel(test_db):
    """Test error when channel doesn't exist."""
    with pytest.raises(AgentError, match="Channel not found"):
        await join_channel(
            "non-existent-channel",
            "test-user",
            "Test description"
        )