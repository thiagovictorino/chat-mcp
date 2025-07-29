from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

# Create the MCP server instance
# Remove stateless_http for stdio mode
mcp = FastMCP("Multi-Agent Chat MCP Server")

# Import tool modules so their @mcp.tool decorators register functions
from mcp_server.tools import channel  # noqa: E402, F401
from mcp_server.tools import agent    # noqa: E402, F401
from mcp_server.tools import messaging # noqa: E402, F401

# Optional: expose the run helper
run = mcp.run

if __name__ == "__main__":
    mcp.run()