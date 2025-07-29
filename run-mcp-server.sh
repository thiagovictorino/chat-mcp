#!/bin/bash
# Run the MCP server with proper volume mounts
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
mkdir -p "$SCRIPT_DIR/data" "$SCRIPT_DIR/logs"

exec docker run --rm -i \
  -v "$SCRIPT_DIR/data:/app/data" \
  -v "$SCRIPT_DIR/logs:/app/logs" \
  -e PYTHONUNBUFFERED=1 \
  chat-mcp-mcp-server