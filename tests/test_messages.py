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
        "Sender agent role"
    )
    agent2 = await join_channel(
        sample_channel["channel_id"], 
        "mentioned", 
        "Mentioned agent role"
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
        "Writer agent role"
    )
    agent2 = await join_channel(
        sample_channel["channel_id"], 
        "reader", 
        "Reader agent role"
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
    
    # Messages should be marked as read by sender at least
    for msg in messages:
        read_by_usernames = [r["username"] for r in msg["read_by"]]
        assert "writer" in read_by_usernames  # Sender always reads their own messages
    
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
    assert messages[1]["content"] == "History message 1"

@pytest.mark.asyncio
async def test_agent_cannot_see_messages_before_join(test_db, sample_channel):
    """Test that agents only see messages sent after they joined."""
    from mcp_server.services.agent_service import join_channel
    
    # First agent joins and sends messages
    agent1 = await join_channel(
        sample_channel["channel_id"],
        "early-bird",
        "First agent role"
    )
    
    # Send some messages
    for i in range(3):
        await send_message(
            sample_channel["channel_id"],
            agent1["agent_id"],
            f"Early message {i}"
        )
    
    # Add a small delay to ensure timestamp difference
    import asyncio
    await asyncio.sleep(0.5)  # Increase delay to ensure timestamp difference
    
    # Second agent joins later
    agent2 = await join_channel(
        sample_channel["channel_id"],
        "late-joiner",
        "Second agent role"
    )
    
    # Agent1 sends more messages
    for i in range(2):
        await send_message(
            sample_channel["channel_id"],
            agent1["agent_id"],
            f"Message after join {i}"
        )
    
    # Agent2 should only see messages sent after joining
    new_messages = await get_new_messages(
        sample_channel["channel_id"],
        agent2["agent_id"]
    )
    
    # Debug: check what messages we got
    if len(new_messages) != 2:
        print(f"Expected 2 messages, got {len(new_messages)}")
        for msg in new_messages:
            print(f"Message: {msg['content']}")
    
    assert len(new_messages) == 2
    assert all("after join" in msg["content"] for msg in new_messages)

@pytest.mark.asyncio
async def test_get_agent_messages(test_db, sample_channel):
    """Test getting messages from a specific agent."""
    from mcp_server.services.agent_service import join_channel
    
    # Create agents
    agent1 = await join_channel(
        sample_channel["channel_id"],
        "alice",
        "Alice agent role"
    )
    agent2 = await join_channel(
        sample_channel["channel_id"],
        "bob",
        "Bob agent role"
    )
    
    # Both agents send messages
    await send_message(
        sample_channel["channel_id"],
        agent1["agent_id"],
        "Message from Alice 1"
    )
    await send_message(
        sample_channel["channel_id"],
        agent2["agent_id"],
        "Message from Bob"
    )
    await send_message(
        sample_channel["channel_id"],
        agent1["agent_id"],
        "Message from Alice 2"
    )
    
    # Get only Alice's messages
    alice_messages = await get_agent_messages(
        sample_channel["channel_id"],
        "alice",
        limit=10
    )
    
    assert len(alice_messages) == 2
    assert all("Alice" in msg["content"] for msg in alice_messages)

@pytest.mark.asyncio
async def test_read_receipts(test_db, sample_channel):
    """Test read receipt tracking."""
    from mcp_server.services.agent_service import join_channel
    
    # Create three agents
    agents = []
    for name in ["agent1", "agent2", "agent3"]:
        agent = await join_channel(
            sample_channel["channel_id"],
            name,
            f"{name} role description"
        )
        agents.append(agent)
    
    # Agent1 sends a message
    await send_message(
        sample_channel["channel_id"],
        agents[0]["agent_id"],
        "Message for everyone"
    )
    
    # Agent2 reads it
    messages = await get_new_messages(
        sample_channel["channel_id"],
        agents[1]["agent_id"]
    )
    
    # Agent3 gets history (also marks as read)
    history = await get_message_history(
        sample_channel["channel_id"],
        agents[2]["agent_id"]
    )
    
    # Check read receipts
    assert len(history) == 1
    msg = history[0]
    read_by_usernames = [r["username"] for r in msg["read_by"]]
    
    # Agent1 and agent2 should have read it at this point
    assert "agent1" in read_by_usernames  # Sender auto-reads
    assert "agent2" in read_by_usernames  # Read via get_new_messages
    
    # Get the message again to see if agent3's read is recorded
    history_again = await get_message_history(
        sample_channel["channel_id"],
        agents[0]["agent_id"]  # Get from agent0's perspective
    )
    msg_again = history_again[0]
    read_by_usernames_again = [r["username"] for r in msg_again["read_by"]]
    assert "agent3" in read_by_usernames_again  # Now should show agent3 read it