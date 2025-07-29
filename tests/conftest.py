import pytest
import pytest_asyncio
import asyncio
import os
from pathlib import Path

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def test_db(tmp_path):
    """Create a temporary test database."""
    # Each test gets its own database file
    db_path = tmp_path / "test.db"
    os.environ['DATABASE_PATH'] = str(db_path)
    
    # Initialize database
    from mcp_server.models.database import init_database
    await init_database()
    
    yield str(db_path)

@pytest_asyncio.fixture
async def sample_channel(test_db):
    """Create a sample channel for testing."""
    from mcp_server.services.channel_service import create_channel
    
    channel = await create_channel(
        name="test-channel",
        description="Test channel for unit tests",
        max_agents=10
    )
    return channel

@pytest_asyncio.fixture
async def sample_agent(test_db, sample_channel):
    """Create a sample agent for testing."""
    from mcp_server.services.agent_service import join_channel
    
    agent = await join_channel(
        channel_id=sample_channel["channel_id"],
        username="test-agent",
        role_description="Test agent for unit tests"
    )
    return agent