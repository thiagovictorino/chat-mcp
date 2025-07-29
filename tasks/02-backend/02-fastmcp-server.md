# Task: Initialize FastMCP Server

## Description
Set up the FastMCP server with HTTP transport and basic configuration following the example provided in the PRD.

## Acceptance Criteria
- [ ] FastMCP server initialized with HTTP transport
- [ ] Server runs on configured port
- [ ] Health check endpoint available
- [ ] Proper logging configured
- [ ] Tool modules imported correctly

## Implementation Steps

1. Create `mcp_server/server.py`:
```python
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

# Create the MCP server instance with stateless HTTP for better scalability
mcp = FastMCP("Multi-Agent Chat MCP Server", stateless_http=True)

# Import tool modules so their @mcp.tool decorators register functions
from mcp_server.tools import channel  # noqa: E402, F401
from mcp_server.tools import agent    # noqa: E402, F401
from mcp_server.tools import messaging # noqa: E402, F401

# Initialize database on startup
@mcp.on_event("startup")
async def startup_event():
    from mcp_server.models.database import init_database
    from mcp_server.utils.logging import setup_logging
    
    setup_logging()
    await init_database()
    print(f"MAC-P Server started on port {os.getenv('MCP_PORT', 8000)}")

# Optional: expose the run helper
run = mcp.run

if __name__ == "__main__":
    mcp.run()
```

2. Create `mcp_server/__init__.py`:
```python
"""Multi-Agent Communication Platform MCP Server."""
__version__ = "0.1.0"
```

3. Create `mcp_server/__main__.py`:
```python
"""Entry point for python -m mcp_server."""
from mcp_server.server import run

if __name__ == "__main__":
    run()
```

4. Create `mcp_server/utils/logging.py`:
```python
import logging
import os
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE_PATH', '/app/logs/chat-mcp.log')
    
    # Create log directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('mcp').setLevel(logging.INFO)
```

## Dependencies
- Database setup completed
- FastMCP package installed

## Estimated Time: 30 minutes