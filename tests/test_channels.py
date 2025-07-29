import pytest
from mcp_server.services.channel_service import (
    create_channel, get_channel, list_channels, 
    validate_channel_capacity, ChannelError
)

@pytest.mark.asyncio
async def test_create_channel(test_db):
    """Test channel creation."""
    channel = await create_channel(
        name="unit-test-channel",
        description="Test description",
        max_agents=25
    )
    
    assert channel["name"] == "unit-test-channel"
    assert channel["description"] == "Test description"
    assert channel["max_agents"] == 25
    assert channel["channel_id"] is not None

@pytest.mark.asyncio
async def test_create_duplicate_channel(test_db):
    """Test that duplicate channel names are rejected."""
    await create_channel(name="duplicate-test")
    
    with pytest.raises(ChannelError, match="already exists"):
        await create_channel(name="duplicate-test")

@pytest.mark.asyncio
async def test_channel_validation(test_db):
    """Test channel validation rules."""
    # Test name length
    with pytest.raises(ChannelError, match="1-100 characters"):
        await create_channel(name="", max_agents=10)
    
    with pytest.raises(ChannelError, match="1-100 characters"):
        await create_channel(name="a" * 101, max_agents=10)
    
    # Test max_agents range
    with pytest.raises(ChannelError, match="between 2 and 100"):
        await create_channel(name="test", max_agents=1)
    
    with pytest.raises(ChannelError, match="between 2 and 100"):
        await create_channel(name="test", max_agents=101)

@pytest.mark.asyncio
async def test_get_channel(test_db, sample_channel):
    """Test getting channel by ID and name."""
    # Get by ID
    channel = await get_channel(channel_id=sample_channel["channel_id"])
    assert channel["name"] == sample_channel["name"]
    
    # Get by name
    channel = await get_channel(name=sample_channel["name"])
    assert channel["channel_id"] == sample_channel["channel_id"]
    
    # Test not found
    channel = await get_channel(channel_id="non-existent")
    assert channel is None

@pytest.mark.asyncio
async def test_list_channels(test_db):
    """Test listing channels with pagination."""
    # Create multiple channels
    for i in range(5):
        await create_channel(name=f"list-test-{i}")
    
    # Test listing
    result = await list_channels(limit=3, offset=0)
    assert len(result["channels"]) == 3
    assert result["total"] >= 5
    assert result["has_more"] is True
    
    # Test pagination
    result = await list_channels(limit=10, offset=0)
    assert result["has_more"] is False

@pytest.mark.asyncio
async def test_channel_capacity(test_db):
    """Test channel capacity validation."""
    channel = await create_channel(name="capacity-test", max_agents=2)
    
    # Should not raise
    await validate_channel_capacity(channel["channel_id"])
    
    # Add agents to reach capacity
    from mcp_server.services.agent_service import join_channel
    await join_channel(channel["channel_id"], "agent1", "Test agent 1")
    await join_channel(channel["channel_id"], "agent2", "Test agent 2")
    
    # Should now raise
    with pytest.raises(ChannelError, match="maximum capacity"):
        await validate_channel_capacity(channel["channel_id"])