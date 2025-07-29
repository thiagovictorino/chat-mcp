"""ASGI app for uvicorn."""
import asyncio
from mcp_server.server import mcp
from mcp_server.models.database import init_database
from mcp_server.utils.logging import setup_logging

# Initialize on module load
setup_logging()

# Create event to track initialization
initialized = False

async def lifespan(app):
    """Lifespan handler for initialization."""
    global initialized
    if not initialized:
        await init_database()
        initialized = True
    yield

# The mcp object itself is the ASGI app when stateless_http=True
app = mcp