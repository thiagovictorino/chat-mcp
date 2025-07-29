"""Entry point for python -m mcp_server."""
import asyncio
import sys
import os

# Ensure unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

from mcp_server.server import mcp
from mcp_server.models.database import init_database
from mcp_server.utils.logging import setup_logging

async def initialize():
    """Initialize the application."""
    setup_logging()
    await init_database()

# Initialize before running
asyncio.run(initialize())

# Run the MCP server
mcp.run()