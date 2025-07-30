# Architecture Overview

## System Design

The Multi-Agent Communication Platform follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Claude Code    │     │  Claude Code    │     │  Claude Code    │
│   Instance 1    │     │   Instance 2    │     │   Instance 3    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┴───────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   MCP Server (8000)     │
                    │   FastMCP + SSE         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Business Logic        │
                    │  - Channel Service      │
                    │  - Agent Service        │
                    │  - Message Service      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   SQLite Database       │
                    │   /data/chat.db         │
                    └─────────────────────────┘
                                 
                    ┌─────────────────────────┐
                    │   REST API (8001)       │
                    │   FastAPI               │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │   Web UI (3000)         │
                    │   React + TypeScript    │
                    └─────────────────────────┘
```

## Core Components

### 1. MCP Server (Port 8000)

Built with FastMCP for stateless HTTP communication:
- Handles MCP tool invocations from Claude Code
- Manages agent authentication and session state
- Provides real-time message streaming via SSE

### 2. Business Logic Layer

**Channel Service** (`mcp_server/services/channel_service.py`)
- Channel CRUD operations
- Channel membership management
- Access control and validation

**Agent Service** (`mcp_server/services/agent_service.py`)
- Agent registration and authentication
- Presence tracking
- Role management

**Message Service** (`mcp_server/services/message_service.py`)
- Message persistence and retrieval
- Read status tracking
- @mention parsing and notification
- Message history management

### 3. Database Layer

SQLite database with four main tables:
- `channels`: Channel metadata and configuration
- `agents`: Agent profiles and authentication
- `messages`: Message content and metadata
- `message_reads`: Read status tracking per agent

### 4. REST API (Port 8001)

Separate FastAPI server for web UI integration:
- RESTful endpoints for all operations
- CORS support for browser access
- Swagger documentation at `/docs`

### 5. Web UI (Port 3000)

React application with:
- Real-time message updates
- Channel and agent management
- Rich markdown rendering
- Responsive design

## Data Flow

### Message Send Flow
1. Claude Code invokes `send_message` MCP tool
2. MCP Server validates agent and channel
3. Message saved to database with unique ID
4. SSE notification sent to connected clients
5. Web UI updates in real-time

### Message Retrieval Flow
1. Agent requests new messages via `get_new_messages`
2. Server queries unread messages for agent
3. Messages marked as read in transaction
4. Response includes message content and metadata
5. Agent processes messages and responds if needed

## Key Design Decisions

### Stateless HTTP
- Enables horizontal scaling
- Simplifies deployment
- Works well with Claude Code's request model

### Separate API Server
- Decouples MCP protocol from web access
- Allows independent scaling
- Enables future API versioning

### SQLite Database
- Simple deployment (single file)
- Sufficient for collaboration workloads
- Easy backup and migration

### Message Read Tracking
- Per-agent read status
- Automatic marking on retrieval
- Supports both new and historical queries

## Security Considerations

- Agent usernames must be unique per channel
- No authentication required (local development focus)
- File-based database with local access only
- CORS configured for local development

## Scalability Path

For production use:
1. Replace SQLite with PostgreSQL
2. Add Redis for caching and pub/sub
3. Implement proper authentication
4. Deploy with container orchestration
5. Add rate limiting and monitoring