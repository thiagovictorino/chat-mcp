# Task: Create Unit Tests

## Description
Write unit tests for core backend services to ensure functionality works correctly.

## Acceptance Criteria
- [ ] Tests for channel service
- [ ] Tests for agent service  
- [ ] Tests for message service
- [ ] Tests for MCP tools
- [ ] All tests passing

## Implementation Steps

1. Update `requirements.txt` to include test dependencies:
```
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-mock==3.11.1
```

2. Create `tests/conftest.py`:
```python
import pytest
import asyncio
import tempfile
import os
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        test_db_path = tmp.name
    
    # Set test database path
    os.environ['DATABASE_PATH'] = test_db_path
    
    # Initialize database
    from mcp_server.models.database import init_database
    await init_database()
    
    yield test_db_path
    
    # Cleanup
    Path(test_db_path).unlink(missing_ok=True)

@pytest.fixture
async def sample_channel(test_db):
    """Create a sample channel for testing."""
    from mcp_server.services.channel_service import create_channel
    
    channel = await create_channel(
        name="test-channel",
        description="Test channel for unit tests",
        max_agents=10
    )
    return channel

@pytest.fixture
async def sample_agent(test_db, sample_channel):
    """Create a sample agent for testing."""
    from mcp_server.services.agent_service import join_channel
    
    agent = await join_channel(
        channel_id=sample_channel["channel_id"],
        username="test-agent",
        role_description="Test agent for unit tests"
    )
    return agent
```

3. Create `tests/test_channels.py`:
```python
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
```

4. Create `tests/test_agents.py`:
```python
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
            "Test agent"
        )
    
    # Too long
    with pytest.raises(AgentError, match="3-50 alphanumeric"):
        await join_channel(
            sample_channel["channel_id"], 
            "a" * 51, 
            "Test agent"
        )
    
    # Invalid characters
    with pytest.raises(AgentError, match="3-50 alphanumeric"):
        await join_channel(
            sample_channel["channel_id"], 
            "user@name", 
            "Test agent"
        )
    
    # Valid special chars
    agent = await join_channel(
        sample_channel["channel_id"], 
        "user_name-123", 
        "Test agent"
    )
    assert agent["username"] == "user_name-123"

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
            f"Test agent {i}"
        )
        agents.append(agent)
    
    # List agents
    agent_list = await list_channel_agents(sample_channel["channel_id"])
    assert len(agent_list) >= 3
    
    # Verify all agents are present
    usernames = [a["username"] for a in agent_list]
    for i in range(3):
        assert f"list-agent-{i}" in usernames
```

5. Create `tests/test_messages.py`:
```python
import pytest
from mcp_server.services.message_service import (
    send_message, get_new_messages, get_message_history,
    get_agent_messages, MessageError
)

@pytest.mark.asyncio
async def test_send_message(test_db, sample_channel, sample_agent):
    """Test sending a message."""
    result = await send_message(
        channel_id=sample_channel["channel_id"],
        agent_id=sample_agent["agent_id"],
        content="Hello, this is a test message!"
    )
    
    assert result["message_id"] is not None
    assert result["sequence_number"] == 1
    assert result["timestamp"] is not None

@pytest.mark.asyncio
async def test_message_validation(test_db, sample_channel, sample_agent):
    """Test message content validation."""
    # Empty message
    with pytest.raises(MessageError, match="1-4000 characters"):
        await send_message(
            sample_channel["channel_id"],
            sample_agent["agent_id"],
            ""
        )
    
    # Too long message
    with pytest.raises(MessageError, match="1-4000 characters"):
        await send_message(
            sample_channel["channel_id"],
            sample_agent["agent_id"],
            "a" * 4001
        )

@pytest.mark.asyncio
async def test_mentions(test_db, sample_channel):
    """Test @ mention functionality."""
    # Create agents
    from mcp_server.services.agent_service import join_channel
    
    agent1 = await join_channel(
        sample_channel["channel_id"], 
        "sender", 
        "Sender agent"
    )
    agent2 = await join_channel(
        sample_channel["channel_id"], 
        "mentioned", 
        "Mentioned agent"
    )
    
    # Send message with mention
    await send_message(
        sample_channel["channel_id"],
        agent1["agent_id"],
        "Hey @mentioned, check this out!"
    )
    
    # Test invalid mention
    with pytest.raises(MessageError, match="not found in channel"):
        await send_message(
            sample_channel["channel_id"],
            agent1["agent_id"],
            "Hey @nonexistent, hello!"
        )

@pytest.mark.asyncio
async def test_get_new_messages(test_db, sample_channel):
    """Test retrieving new messages and auto-read."""
    from mcp_server.services.agent_service import join_channel
    
    # Create two agents
    agent1 = await join_channel(
        sample_channel["channel_id"], 
        "writer", 
        "Writer agent"
    )
    agent2 = await join_channel(
        sample_channel["channel_id"], 
        "reader", 
        "Reader agent"
    )
    
    # Agent1 sends messages
    await send_message(
        sample_channel["channel_id"],
        agent1["agent_id"],
        "First message"
    )
    await send_message(
        sample_channel["channel_id"],
        agent1["agent_id"],
        "Second message @reader"
    )
    
    # Agent2 gets new messages
    messages = await get_new_messages(
        sample_channel["channel_id"],
        agent2["agent_id"]
    )
    
    assert len(messages) == 2
    assert messages[0]["content"] == "First message"
    assert messages[1]["content"] == "Second message @reader"
    assert "reader" in messages[1]["mentions"]
    
    # Messages should be marked as read
    for msg in messages:
        read_by_usernames = [r["username"] for r in msg["read_by"]]
        assert "reader" in read_by_usernames
    
    # Getting new messages again should return empty
    messages = await get_new_messages(
        sample_channel["channel_id"],
        agent2["agent_id"]
    )
    assert len(messages) == 0

@pytest.mark.asyncio
async def test_message_history(test_db, sample_channel, sample_agent):
    """Test message history with pagination."""
    # Send multiple messages
    for i in range(5):
        await send_message(
            sample_channel["channel_id"],
            sample_agent["agent_id"],
            f"History message {i}"
        )
    
    # Get history
    messages = await get_message_history(
        sample_channel["channel_id"],
        sample_agent["agent_id"],
        limit=3
    )
    
    assert len(messages) == 3
    assert messages[0]["content"] == "History message 2"
    assert messages[-1]["content"] == "History message 4"
    
    # Test pagination
    messages = await get_message_history(
        sample_channel["channel_id"],
        sample_agent["agent_id"],
        limit=2,
        before_sequence=3
    )
    
    assert len(messages) == 2
    assert messages[0]["content"] == "History message 0"
```

6. Create `tests/test_mcp_tools.py` to test MCP tool integrations...

## Dependencies
- All services implemented
- MCP tools created

## Estimated Time: 1.5 hours