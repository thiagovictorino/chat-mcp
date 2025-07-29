import logging
import os
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE_PATH', '/app/logs/chat-mcp.log')
    
    # Create log directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging - only to file, not stdout
    # stdout/stderr must be reserved for MCP stdio communication
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file)
        ]
    )
    
    # Set specific loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('mcp').setLevel(logging.INFO)