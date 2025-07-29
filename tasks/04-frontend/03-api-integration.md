# Task: Complete API Integration

## Description
Complete the API integration between the React UI and the MCP server backend, including proper error handling and real-time updates.

## Acceptance Criteria
- [ ] API endpoints properly mapped
- [ ] Error handling for network failures
- [ ] Auto-refresh functionality working
- [ ] Read receipts updating in real-time
- [ ] Log viewer connected to backend

## Implementation Steps

1. Update backend to expose REST endpoints alongside MCP tools by creating `mcp_server/api/__init__.py`:
```python
from fastapi import APIRouter, HTTPException
from mcp_server.services import channel_service, agent_service, message_service
from typing import Optional

router = APIRouter()

# Channel endpoints
@router.get("/channels")
async def list_channels(limit: int = 20, offset: int = 0):
    try:
        return await channel_service.list_channels(limit, offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels")
async def create_channel(data: dict):
    try:
        return await channel_service.create_channel(
            name=data["name"],
            description=data.get("description"),
            max_agents=data.get("max_agents", 50)
        )
    except channel_service.ChannelError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Agent endpoints
@router.get("/channels/{channel_id}/agents")
async def list_agents(channel_id: str):
    try:
        agents = await agent_service.list_channel_agents(channel_id)
        return {"agents": agents}
    except agent_service.AgentError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Message endpoints
@router.get("/channels/{channel_id}/messages")
async def get_messages(
    channel_id: str, 
    agent_id: Optional[str] = None,
    limit: int = 50
):
    try:
        # For UI, we don't mark as read - just retrieve
        from mcp_server.models.database import get_db
        from mcp_server.utils.database import dict_from_row
        
        async with get_db() as db:
            cursor = await db.execute(
                """SELECT m.*, a.username as sender_username
                   FROM messages m
                   JOIN agents a ON m.agent_id = a.agent_id
                   WHERE m.channel_id = ?
                   ORDER BY m.sequence_number DESC
                   LIMIT ?""",
                (channel_id, limit)
            )
            
            messages = []
            async for row in cursor:
                message_dict = dict_from_row(row)
                
                # Get mentions
                mention_cursor = await db.execute(
                    "SELECT mentioned_username FROM message_mentions WHERE message_id = ?",
                    (message_dict['message_id'],)
                )
                mentions = [r['mentioned_username'] async for r in mention_cursor]
                
                # Get read_by info
                read_cursor = await db.execute(
                    """SELECT r.agent_id, a.username, r.read_at
                       FROM read_status r
                       JOIN agents a ON r.agent_id = a.agent_id
                       WHERE r.message_id = ?""",
                    (message_dict['message_id'],)
                )
                read_by = []
                async for r in read_cursor:
                    read_by.append({
                        "username": r['username'],
                        "read_at": r['read_at']
                    })
                
                messages.append({
                    "message_id": message_dict['message_id'],
                    "sender": {
                        "agent_id": message_dict['agent_id'],
                        "username": message_dict['sender_username']
                    },
                    "content": message_dict['content'],
                    "mentions": mentions,
                    "timestamp": message_dict['created_at'],
                    "sequence_number": message_dict['sequence_number'],
                    "read_by": read_by
                })
            
            messages.reverse()  # Return in chronological order
            return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Logs endpoint
@router.get("/logs")
async def get_logs(limit: int = 100):
    try:
        import os
        log_file = os.getenv('LOG_FILE_PATH', '/app/logs/chat-mcp.log')
        
        if not os.path.exists(log_file):
            return {"logs": []}
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Return last N lines
            return {"logs": lines[-limit:]}
    except Exception as e:
        return {"logs": [], "error": str(e)}
```

2. Update `mcp_server/server.py` to include REST routes:
```python
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

# Create the MCP server instance with stateless HTTP for better scalability
mcp = FastMCP("Multi-Agent Chat MCP Server", stateless_http=True)

# Import tool modules
from mcp_server.tools import channel, agent, messaging  # noqa: E402, F401

# Add REST API routes
from mcp_server.api import router
mcp.include_router(router, prefix="/api")

# Add CORS for UI
from fastapi.middleware.cors import CORSMiddleware
mcp.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@mcp.on_event("startup")
async def startup_event():
    from mcp_server.models.database import init_database
    from mcp_server.utils.logging import setup_logging
    
    setup_logging()
    await init_database()
    print(f"MAC-P Server started on port {os.getenv('MCP_PORT', 8000)}")

run = mcp.run

if __name__ == "__main__":
    mcp.run()
```

3. Create `ui/src/components/LogViewer.tsx`:
```tsx
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import './LogViewer.css';

interface Props {
  refreshInterval: number;
}

const LogViewer: React.FC<Props> = ({ refreshInterval }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);

  const loadLogs = async () => {
    try {
      const response = await api.get('/logs?limit=200');
      setLogs(response.data.logs || []);
    } catch (err) {
      console.error('Error loading logs:', err);
      setLogs(['Error loading logs']);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  useEffect(() => {
    if (autoScroll) {
      const element = document.getElementById('log-bottom');
      element?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  return (
    <div className="log-viewer">
      <div className="log-header">
        <h2>System Logs</h2>
        <label>
          <input
            type="checkbox"
            checked={autoScroll}
            onChange={(e) => setAutoScroll(e.target.checked)}
          />
          Auto-scroll
        </label>
      </div>
      
      <div className="log-content">
        {loading ? (
          <div className="loading">Loading logs...</div>
        ) : logs.length === 0 ? (
          <div className="no-logs">No logs available</div>
        ) : (
          <>
            {logs.map((log, index) => (
              <div key={index} className="log-line">
                {log}
              </div>
            ))}
            <div id="log-bottom" />
          </>
        )}
      </div>
    </div>
  );
};

export default LogViewer;
```

4. Update `ui/src/services/api.ts` to use /api prefix:
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add error interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Rest of the API methods remain the same...
```

## Dependencies
- UI components created
- Backend services implemented

## Estimated Time: 45 minutes