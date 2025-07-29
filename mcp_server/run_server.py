#!/usr/bin/env python
"""Run the MCP server with uvicorn."""
import asyncio
import uvicorn
from mcp_server.server import mcp
from mcp_server.models.database import init_database
from mcp_server.utils.logging import setup_logging

async def startup():
    """Initialize on startup."""
    setup_logging()
    await init_database()
    print("MAC-P Server initialized", flush=True)

if __name__ == "__main__":
    # Run initialization
    asyncio.run(startup())
    
    # Create the SSE app from FastMCP
    app = mcp.create_sse_handler()
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)