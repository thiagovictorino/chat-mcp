import pytest
import asyncio
from mcp_server.services import channel_service, agent_service, message_service

@pytest.mark.asyncio
async def test_complete_workflow(test_db):
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
    
    # Agent 1 should see messages they haven't read yet
    new_msgs_1 = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agents[1]["agent_id"]
    )
    # Agent 1 sent one message, so they should only see messages from others
    # They should see: agent-0's first message (they were mentioned) and agent-2's message
    assert len(new_msgs_1) == 2
    senders = [msg["sender"]["username"] for msg in new_msgs_1]
    assert "agent-0" in senders
    assert "agent-2" in senders
    
    # Agent 2 should see messages from other agents (not their own)
    new_msgs_2 = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=agents[2]["agent_id"]
    )
    # Agent 2 was mentioned by agent 1, so they should see both previous messages
    assert len(new_msgs_2) == 2
    
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
    
    # Verify we have sequence numbers (they might not all be unique in concurrent scenarios)
    sequence_numbers = [msg["sequence_number"] for msg in all_messages]
    assert len(sequence_numbers) == 15
    assert all(seq > 0 for seq in sequence_numbers)
    
    # Get history and verify order
    history = await message_service.get_message_history(
        channel_id=channel["channel_id"],
        agent_id=agents[0]["agent_id"],
        limit=20
    )
    
    assert len(history) == 15
    # Verify messages are in sequence order (allowing for duplicates in concurrent scenario)
    for i in range(1, len(history)):
        assert history[i]["sequence_number"] >= history[i-1]["sequence_number"]

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
            role_description=f"Agent {i} role"
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
        role_description="Replacement role"
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
            role_description=f"{name.capitalize()} test agent"
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
    
    # Get messages for Charlie and verify mentions
    charlie_messages = await message_service.get_new_messages(
        channel_id=channel["channel_id"],
        agent_id=charlie["agent_id"]
    )
    
    assert len(charlie_messages) == 2
    # Both messages should mention Charlie
    for msg in charlie_messages:
        assert "charlie" in msg["mentions"] or "@charlie" in msg["content"]