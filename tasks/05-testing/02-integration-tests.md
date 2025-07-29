# Task: Create Integration Tests

## Description
Write integration tests to verify the complete flow of agents joining channels, sending messages, and reading messages.

## Acceptance Criteria
- [ ] Test complete agent workflow
- [ ] Test concurrent agent interactions
- [ ] Test message ordering
- [ ] Test read receipt accuracy
- [ ] All integration tests passing

## Implementation Steps

1. Create `tests/test_integration.py`:
```python
import pytest
import asyncio
from mcp_server.services import channel_service, agent_service, message_service

@pytest.mark.asyncio
async def test_complete_agent_workflow(test_db):
    """Test the complete workflow of agents communicating."""
    # Step 1: Create a channel
    channel = await channel_service.create_channel(
        name="integration-test-channel",
        description="Channel for integration testing",
        max_agents=5
    )
    
    # Step 2: Multiple agents join
    agents = []
    for i in range(3):
        agent = await agent_service.join_channel(
            channel_id=channel["channel_id"],
            username=f"agent-{i}",
            role_description=f"Integration test agent {i}"
        )
        agents.append(agent)
    
    # Step 3: Agents send messages with mentions
    # Agent 0 sends a message mentioning agent 1
    msg1 = await message_service.send_message(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"],
        content="Hello @agent-1, how are you?"
    )
    
    # Agent 1 responds mentioning both
    msg2 = await message_service.send_message(
        channel_id=channel["channel_id"],
        agent_id=agents[1]["agent_id"],
        content="I'm good @agent-0! Hey @agent-2, join us!"
    )
    
    # Agent 2 sends a general message
    msg3 = await message_service.send_message(
        channel_id=channel["channel_id"],
        agent_id=agents[2]["agent_id"],
        content="Hello everyone! Happy to be here."
    )
    
    # Step 4: Check new messages for each agent
    # Agent 0 should see 2 new messages (from agent 1 and 2)
    new_msgs_0 = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"]
    )
    assert len(new_msgs_0) == 2
    
    # Agent 1 should see 1 new message (from agent 2)
    new_msgs_1 = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agents[1]["agent_id"]
    )
    assert len(new_msgs_1) == 1
    assert new_msgs_1[0]["sender"]["username"] == "agent-2"
    
    # Agent 2 should see no new messages (all marked as read)
    new_msgs_2 = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agents[2]["agent_id"]
    )
    assert len(new_msgs_2) == 0
    
    # Step 5: Verify read receipts
    history = await message_service.get_message_history(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"],
        limit=10
    )
    
    # All messages should now be read by agent-0
    for msg in history:
        read_by_usernames = [r["username"] for r in msg["read_by"]]
        assert "agent-0" in read_by_usernames
    
    # Step 6: Agent leaves channel
    await agent_service.leave_channel(
        channel_id=channel["channel_id"],
        agent_id=agents[2]["agent_id"]
    )
    
    # Verify agent count
    remaining_agents = await agent_service.list_channel_agents(
        channel_id=channel["channel_id"]
    )
    assert len(remaining_agents) == 2

@pytest.mark.asyncio
async def test_concurrent_messaging(test_db):
    """Test multiple agents sending messages concurrently."""
    # Create channel
    channel = await channel_service.create_channel(
        name="concurrent-test",
        max_agents=10
    )
    
    # Create multiple agents
    agents = []
    for i in range(5):
        agent = await agent_service.join_channel(
            channel_id=channel["channel_id"],
            username=f"concurrent-{i}",
            role_description=f"Concurrent test agent {i}"
        )
        agents.append(agent)
    
    # Send messages concurrently
    async def send_messages(agent, count):
        messages = []
        for i in range(count):
            msg = await message_service.send_message(
                channel_id=channel["channel_id"],
                agent_id=agent["agent_id"],
                content=f"Message {i} from @{agent['username']}"
            )
            messages.append(msg)
        return messages
    
    # Each agent sends 3 messages concurrently
    tasks = [send_messages(agent, 3) for agent in agents]
    results = await asyncio.gather(*tasks)
    
    # Verify all messages were sent
    all_messages = [msg for agent_msgs in results for msg in agent_msgs]
    assert len(all_messages) == 15
    
    # Verify sequence numbers are unique
    sequence_numbers = [msg["sequence_number"] for msg in all_messages]
    assert len(set(sequence_numbers)) == 15
    
    # Get history and verify order
    history = await message_service.get_message_history(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"],
        limit=20
    )
    
    assert len(history) == 15
    # Verify messages are in sequence order
    for i in range(1, len(history)):
        assert history[i]["sequence_number"] > history[i-1]["sequence_number"]

@pytest.mark.asyncio
async def test_message_persistence_after_join(test_db):
    """Test that agents can only see messages after they joined."""
    # Create channel
    channel = await channel_service.create_channel(
        name="persistence-test"
    )
    
    # First agent joins and sends messages
    agent1 = await agent_service.join_channel(
        channel_id=channel["channel_id"],
        username="early-bird",
        role_description="First agent"
    )
    
    # Send some messages
    for i in range(3):
        await message_service.send_message(
            channel_id=channel["channel_id"],
            agent_id=agent1["agent_id"],
            content=f"Early message {i}"
        )
    
    # Second agent joins later
    agent2 = await agent_service.join_channel(
        channel_id=channel["channel_id"],
        username="late-joiner",
        role_description="Second agent"
    )
    
    # Agent1 sends more messages
    for i in range(2):
        await message_service.send_message(
            channel_id=channel["channel_id"],
            agent_id=agent1["agent_id"],
            content=f"Message after join {i}"
        )
    
    # Agent2 should only see messages sent after joining
    new_messages = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agent2["agent_id"]
    )
    
    assert len(new_messages) == 2
    assert all("after join" in msg["content"] for msg in new_messages)

@pytest.mark.asyncio
async def test_channel_capacity_limits(test_db):
    """Test channel capacity enforcement."""
    # Create small capacity channel
    channel = await channel_service.create_channel(
        name="capacity-limit-test",
        max_agents=3
    )
    
    # Add agents up to capacity
    agents = []
    for i in range(3):
        agent = await agent_service.join_channel(
            channel_id=channel["channel_id"],
            username=f"capacity-agent-{i}",
            role_description=f"Agent {i}"
        )
        agents.append(agent)
    
    # Try to add one more - should fail
    with pytest.raises(channel_service.ChannelError, match="maximum capacity"):
        await agent_service.join_channel(
            channel_id=channel["channel_id"],
            username="overflow-agent",
            role_description="Should not join"
        )
    
    # Remove one agent
    await agent_service.leave_channel(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"]
    )
    
    # Now should be able to add new agent
    new_agent = await agent_service.join_channel(
        channel_id=channel["channel_id"],
        username="replacement-agent",
        role_description="Replacement"
    )
    assert new_agent["username"] == "replacement-agent"

@pytest.mark.asyncio
async def test_mention_notifications(test_db):
    """Test that mentions work correctly across agents."""
    # Create channel and agents
    channel = await channel_service.create_channel(
        name="mention-test"
    )
    
    agents = []
    for name in ["alice", "bob", "charlie"]:
        agent = await agent_service.join_channel(
            channel_id=channel["channel_id"],
            username=name,
            role_description=f"{name.capitalize()} agent"
        )
        agents.append(agent)
    
    alice, bob, charlie = agents
    
    # Alice mentions Bob and Charlie
    await message_service.send_message(
        channel_id=channel["channel_id"],
        agent_id=alice["agent_id"],
        content="Hey @bob and @charlie, meeting at 3pm?"
    )
    
    # Bob responds mentioning only Charlie
    await message_service.send_message(
        channel_id=channel["channel_id"],
        agent_id=bob["agent_id"],
        content="Works for me! @charlie, are you free?"
    )
    
    # Check messages from Charlie's perspective
    from mcp_server.tools.messaging import check_mentions
    import json
    
    # Use the check_mentions tool
    mentions_result = await check_mentions(
        channel_id=channel["channel_id"],
        agent_id=charlie["agent_id"],
        limit=10
    )
    
    mentions_data = json.loads(mentions_result)
    assert mentions_data["status"] == "success"
    assert mentions_data["mentions_count"] == 2
    
    # Both messages should mention Charlie
    for msg in mentions_data["messages"]:
        assert "charlie" in msg["content"].lower()
```

2. Create `tests/test_mcp_integration.py`:
```python
import pytest
import json
from mcp_server.tools import channel, agent, messaging

@pytest.mark.asyncio
async def test_mcp_tools_workflow(test_db):
    """Test complete workflow using MCP tools."""
    # Create channel using MCP tool
    create_result = await channel.create_channel(
        name="mcp-integration-test",
        description="Testing MCP tools",
        max_agents=5
    )
    create_data = json.loads(create_result)
    assert create_data["status"] == "success"
    channel_id = create_data["channel"]["channel_id"]
    
    # List channels
    list_result = await channel.list_channels()
    list_data = json.loads(list_result)
    assert list_data["status"] == "success"
    assert any(ch["name"] == "mcp-integration-test" 
              for ch in list_data["channels"])
    
    # Join channel with multiple agents
    agent_ids = []
    for i in range(3):
        join_result = await agent.join_channel(
            channel_id=channel_id,
            username=f"mcp-agent-{i}",
            role_description=f"MCP test agent {i}"
        )
        join_data = json.loads(join_result)
        assert join_data["status"] == "success"
        agent_ids.append(join_data["agent_id"])
    
    # Send messages
    send_result = await messaging.send_message(
        channel_id=channel_id,
        agent_id=agent_ids[0],
        content="Hello from MCP tool! @mcp-agent-1 please respond"
    )
    send_data = json.loads(send_result)
    assert send_data["status"] == "success"
    
    # Get new messages for agent 1
    new_msg_result = await messaging.get_new_messages(
        channel_id=channel_id,
        agent_id=agent_ids[1],
        limit=10
    )
    new_msg_data = json.loads(new_msg_result)
    assert new_msg_data["status"] == "success"
    assert new_msg_data["new_messages_count"] == 1
    
    # Verify mention
    message = new_msg_data["messages"][0]
    assert "mcp-agent-1" in message["mentions"]
    
    # Leave channel
    leave_result = await agent.leave_channel(
        channel_id=channel_id,
        agent_id=agent_ids[2]
    )
    leave_data = json.loads(leave_result)
    assert leave_data["status"] == "success"
    
    # Verify agent count
    agents_result = await agent.list_channel_agents(channel_id)
    agents_data = json.loads(agents_result)
    assert agents_data["agent_count"] == 2
```

## Dependencies
- Unit tests completed
- All services implemented

## Estimated Time: 1 hour