"""ASGI application for the MCP server."""
import asyncio
from fastapi import FastAPI
from mcp_server.server import mcp
from mcp_server.models.database import init_database
from mcp_server.utils.logging import setup_logging

# Create FastAPI app
app = FastAPI(title="MAC-P Server")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    setup_logging()
    await init_database()
    print("MAC-P Server initialized")

# Mount the MCP endpoints
app.mount("/", mcp)