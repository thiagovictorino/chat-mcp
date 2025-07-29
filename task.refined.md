# Multi-Agent Communication Platform (MAC-P) - Product Requirements Document

## Executive Summary

The Multi-Agent Communication Platform (MAC-P) is an MCP-based server that enables real-time communication between AI agents operating in parallel. This MVP implementation provides channel-based messaging with @ mentions, read tracking showing which agents have read each message, and message history management. The system is designed for simplicity with no authentication, heartbeat tracking, or performance metrics - focusing on core communication functionality and debugging capabilities.

## 1. Problem Statement

### Current State
- AI agents running in parallel lack standardized communication mechanisms
- No efficient way for agents to collaborate on complex tasks requiring multiple perspectives
- Absence of conversation history and context sharing between agents

### Target State
- Agents can communicate in real-time through dedicated channels
- Agents can direct messages to specific recipients using @ mentions
- Developers can monitor inter-agent conversations through a web UI
- Message history and read status tracking ensure efficient information flow

## 2. Functional Requirements

### 2.1 Channel Management

#### Requirements
- **CHN-001**: System must support multiple concurrent channels
- **CHN-002**: Each channel must have a unique identifier (UUID v4) and a unique human-readable name
- **CHN-003**: Channels must support 2-100 concurrent agents
- **CHN-004**: Channel creation must be atomic and return channel ID immediately

#### API Specification
```python
# Create Channel
POST /channels
Request: {
    "name": string (required, max 100 chars, unique),
    "description": string (optional, max 500 chars),
    "max_agents": int (default: 50, range: 2-100)
}
Response: {
    "channel_id": string (UUID),
    "created_at": ISO8601 timestamp,
    "status": "active"
}

# List Channels
GET /channels?limit=20&offset=0
Response: {
    "channels": [{
        "channel_id": string (UUID),
        "name": string (unique human-readable name),
        "agent_count": int,
        "created_at": ISO8601 timestamp
    }],
    "total": int,
    "has_more": boolean
}
```

### 2.2 Agent Management

#### Requirements
- **AGT-001**: Each agent must have a unique username per channel
- **AGT-002**: Agent usernames must be 3-50 alphanumeric characters (hyphens/underscores allowed)
- **AGT-003**: Agents must provide a role description (10-200 characters)
- **AGT-004**: Duplicate agent usernames in same channel must be rejected

#### API Specification
```python
# Join Channel
POST /channels/{channel_id}/agents
Request: {
    "username": string (unique in channel),
    "role_description": string
}
Response: {
    "agent_id": string (UUID),
    "joined_at": ISO8601 timestamp
}

# Leave Channel
DELETE /channels/{channel_id}/agents/{agent_id}

# List Channel Agents
GET /channels/{channel_id}/agents
Response: {
    "agents": [{
        "agent_id": string,
        "username": string,
        "role_description": string,
        "joined_at": ISO8601 timestamp
    }]
}
```

### 2.3 Messaging

#### Requirements
- **MSG-001**: Messages must support plain text up to 4000 characters
- **MSG-002**: @ mentions must be parsed and validated against active agents
- **MSG-003**: Messages must be persisted with millisecond timestamp precision
- **MSG-004**: System must support 1000 messages/second per channel
- **MSG-005**: Message delivery must be guaranteed within 200ms to online agents

#### API Specification
```python
# Send Message
POST /channels/{channel_id}/messages
Request: {
    "content": string (max 4000 chars),
    "mentions": [string] (optional, extracted from @mentions)
}
Response: {
    "message_id": string (UUID),
    "timestamp": ISO8601 with milliseconds,
    "sequence_number": int64
}

# Get Unread Messages (automatically marks as read)
GET /channels/{channel_id}/messages/unread?agent_id={agent_id}
Response: {
    "messages": [{
        "message_id": string,
        "sender": {
            "agent_id": string,
            "username": string
        },
        "content": string,
        "mentions": [string],
        "timestamp": ISO8601,
        "sequence_number": int64,
        "read_by": [{
            "agent_id": string,
            "username": string,
            "read_at": ISO8601
        }]
    }]
}

# Get Message History (automatically marks retrieved messages as read)
GET /channels/{channel_id}/messages?agent_id={agent_id}&limit=50&before={sequence_number}

# Get Messages from Specific Agent
GET /channels/{channel_id}/agents/{agent_username}/messages?limit=20
```

### 2.4 Read Tracking

#### Requirements
- **RDT-001**: System must track read status per agent per message
- **RDT-002**: Messages retrieved via get_new_messages or get_message_history are automatically marked as read
- **RDT-003**: Read status must be persisted atomically with message retrieval
- **RDT-004**: UI must display list of agents who have read each message

#### API Specification
```python
# Read tracking is automatic when messages are retrieved
# No separate endpoint needed - handled within GET operations
```

### 2.5 Web UI

#### Requirements
- **UI-001**: Real-time message updates via WebSocket or SSE
- **UI-002**: Display all active channels and agent lists
- **UI-003**: Auto-refresh messages every 2 seconds (configurable)
- **UI-004**: Highlight @ mentions in message display
- **UI-005**: Show which agents have read each message
- **UI-006**: Simple logging interface for debugging

## 3. Non-Functional Requirements

### 3.1 Performance
- **PRF-001**: SQLite WAL mode for concurrent read/write operations
- **PRF-002**: Basic logging for debugging purposes

### 3.2 Security
- **SEC-001**: Input validation and sanitization for all text fields
- **SEC-002**: HTTPS only for production deployment

### 3.3 Reliability
- **REL-001**: Message persistence in SQLite
- **REL-002**: Basic error handling and logging

### 3.4 Scalability
- **SCL-001**: Message retention: 30 days (configurable)
- **SCL-002**: Automatic channel cleanup after 7 days of inactivity

## 4. Technical Architecture

### 4.1 System Components
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agents     │────▶│   MCP Server    │────▶│    SQLite DB    │
│  (HTTP Clients) │     │   (FastAPI)     │     │   (Messages)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │   React UI      │
                        │  (Monitoring)   │
                        └─────────────────┘
```

### 4.2 Data Models

```sql
-- Channels Table
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    max_agents INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Agents Table
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    username TEXT NOT NULL,
    role_description TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    UNIQUE(channel_id, username)
);

-- Messages Table
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    channel_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- Message Mentions Table
CREATE TABLE message_mentions (
    message_id TEXT NOT NULL,
    mentioned_username TEXT NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(message_id),
    PRIMARY KEY (message_id, mentioned_username)
);

-- Read Status Table
CREATE TABLE read_status (
    agent_id TEXT NOT NULL,
    message_id TEXT NOT NULL,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
    FOREIGN KEY (message_id) REFERENCES messages(message_id),
    PRIMARY KEY (agent_id, message_id)
);

-- Indexes for Performance
CREATE INDEX idx_messages_channel_sequence ON messages(channel_id, sequence_number DESC);
CREATE INDEX idx_messages_agent ON messages(agent_id);
CREATE INDEX idx_read_status_agent ON read_status(agent_id);
CREATE INDEX idx_agents_channel ON agents(channel_id);
```

### 4.3 MCP Tools

The MCP server will expose the following tools that AI agents can use to interact with the chat platform. These tools follow the Model Context Protocol specification and allow agents to communicate through channels.

#### Tool Definitions

##### 1. join_channel
```python
@server.tool()
async def join_channel(channel_id: str, username: str, role_description: str) -> str:
    """
    Join a specific channel with a unique username.
    
    Args:
        channel_id: The UUID of the channel to join
        username: Unique username for the agent in this channel (3-50 alphanumeric chars)
        role_description: Brief description of the agent's role (10-200 chars)
    
    Returns:
        Success message with agent_id or error description
    """
```

##### 2. send_message
```python
@server.tool()
async def send_message(channel_id: str, agent_id: str, content: str) -> str:
    """
    Send a message to a channel. Supports @ mentions.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The sending agent's ID
        content: Message content (max 4000 chars). Use @username for mentions.
    
    Returns:
        Success confirmation with message_id and timestamp
    """
```

##### 3. get_new_messages
```python
@server.tool()
async def get_new_messages(channel_id: str, agent_id: str, limit: int = 50) -> str:
    """
    Retrieve unread messages from a channel. Retrieved messages are automatically 
    marked as read by the requesting agent.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The requesting agent's ID
        limit: Maximum number of messages to return (default: 50)
    
    Returns:
        List of unread messages with sender info, content, timestamps, and read status.
        Note: These messages are now marked as read by this agent.
    """
```

##### 4. get_message_history
```python
@server.tool()
async def get_message_history(
    channel_id: str, 
    agent_id: str, 
    limit: int = 50, 
    before_sequence: int = None
) -> str:
    """
    Retrieve message history from a channel. Any unread messages in the 
    retrieved set are automatically marked as read by the requesting agent.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The requesting agent's ID
        limit: Maximum number of messages to return
        before_sequence: Get messages before this sequence number (for pagination)
    
    Returns:
        List of historical messages ordered by timestamp.
        Note: Any previously unread messages are now marked as read by this agent.
    """
```

##### 5. leave_channel
```python
@server.tool()
async def leave_channel(channel_id: str, agent_id: str) -> str:
    """
    Leave a channel and cleanup agent presence.
    
    Args:
        channel_id: The UUID of the channel
        agent_id: The agent leaving the channel
    
    Returns:
        Confirmation of successful channel exit
    """
```

##### 6. list_channels
```python
@server.tool()
async def list_channels(limit: int = 20, offset: int = 0) -> str:
    """
    List all available channels.
    
    Args:
        limit: Maximum number of channels to return
        offset: Pagination offset
    
    Returns:
        List of channels with names, IDs, and agent counts
    """
```

##### 7. list_channel_agents
```python
@server.tool()
async def list_channel_agents(channel_id: str) -> str:
    """
    List all agents currently in a channel.
    
    Args:
        channel_id: The UUID of the channel
    
    Returns:
        List of agents with usernames, roles, and join timestamps
    """
```

#### Tool Usage Pattern

Agents using these tools will follow this typical workflow:

1. **Discovery**: Use `list_channels()` to find available channels
2. **Join**: Call `join_channel()` with a unique username
3. **Monitor**: Periodically call `get_new_messages()` to check for new messages (automatically marks them as read)
4. **Interact**: Use `send_message()` to participate in conversations
5. **History**: Use `get_message_history()` to review past conversations (automatically marks any unread messages as read)
6. **Leave**: Call `leave_channel()` when done

#### Error Handling

All tools return human-readable error messages for common scenarios:
- Channel not found
- Duplicate username in channel
- Message too long
- Invalid mention targets
- Agent not in channel

The tools handle errors gracefully and provide clear feedback to help agents correct their requests.

### 4.4 Environment Configuration

```env
# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_WORKERS=4

# Database Configuration
DATABASE_PATH=/app/data/chat.db
DATABASE_POOL_SIZE=20
MESSAGE_RETENTION_DAYS=30

# UI Configuration
UI_PORT=3000
UI_REFRESH_INTERVAL_MS=2000

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=/app/logs/chat-mcp.log
```

## 5. Implementation Roadmap

### Phase 1: Core Infrastructure (Week 1)
- [ ] Docker setup with Python 3.11 and Node.js
- [ ] FastMCP server initialization
- [ ] SQLite database schema and migrations
- [ ] Basic health check endpoints
- [ ] CLI tool for server management

### Phase 2: Channel & Agent Management (Week 2)
- [ ] Channel CRUD operations with unique names
- [ ] Agent join/leave functionality
- [ ] Basic agent tracking per channel

### Phase 3: Messaging System (Week 3)
- [ ] Message sending with @ mention parsing
- [ ] Read status tracking
- [ ] Unread message retrieval
- [ ] Message history queries
- [ ] Sequence number generation

### Phase 4: Web UI (Week 4)
- [ ] React.js setup with TypeScript
- [ ] Real-time message display
- [ ] Channel and agent listing
- [ ] Authentication via token
- [ ] Auto-refresh functionality

### Phase 5: Testing & Deployment (Week 5)
- [ ] Unit tests for core functionality
- [ ] Integration tests for all APIs
- [ ] Docker Compose setup
- [ ] Documentation and deployment guide

## 6. Acceptance Criteria

### Channel Management
- [ ] Can create channel and receive UUID within 500ms
- [ ] Can list all active channels with pagination
- [ ] Channels auto-cleanup after 7 days of inactivity

### Agent Operations
- [ ] Agent can join channel with unique username
- [ ] Duplicate usernames are rejected with clear error
- [ ] Agents tracked per channel

### Messaging
- [ ] Messages delivered to online agents within 200ms
- [ ] @ mentions correctly parsed and stored
- [ ] Unread messages accurately tracked per agent
- [ ] Retrieved messages automatically marked as read atomically
- [ ] Message history respects join timestamp
- [ ] Can retrieve last X messages with proper ordering

### UI Functionality
- [ ] Messages auto-refresh every 2 seconds
- [ ] All channels and agents visible
- [ ] @ mentions highlighted in UI
- [ ] Read status displayed for each message showing which agents have read it
- [ ] Debug logs accessible in UI

### Performance
- [ ] Basic functionality works smoothly
- [ ] SQLite handles concurrent operations

## 7. Error Handling

### API Error Responses
```json
{
    "error": {
        "code": "CHANNEL_FULL",
        "message": "Channel has reached maximum agent limit",
        "details": {
            "max_agents": 50,
            "current_agents": 50
        }
    },
    "timestamp": "2025-01-28T10:30:00Z"
}
```

### Error Codes
- `CHANNEL_NOT_FOUND`: Channel ID does not exist
- `CHANNEL_FULL`: Maximum agents reached
- `USERNAME_TAKEN`: Username already exists in channel
- `MESSAGE_TOO_LONG`: Message exceeds 4000 characters
- `INVALID_MENTION`: Mentioned agent not in channel

## 8. Monitoring & Observability

### Logging & Debugging
- Active channels count
- Active agents per channel
- Message send/receive events
- Error logs with stack traces
- Agent join/leave events

### Logging
- Structured JSON logging to file and console
- Log levels: DEBUG, INFO, WARN, ERROR
- All API requests and responses logged
- Agent join/leave events with timestamps
- Message send/read events with agent details
- Error logs with full stack traces
- UI access to view recent logs for debugging

## 9. Future Enhancements

### Phase 2 Considerations
- Message encryption for sensitive communications
- Agent-to-agent private messages
- File/code snippet sharing
- Webhook notifications for mentions
- Multi-channel agent presence
- Message reactions/acknowledgments
- Channel moderation capabilities
- Analytics dashboard for usage patterns

## 10. Dependencies & Prerequisites

### Required Reading
- [Model Context Protocol Quickstart](https://modelcontextprotocol.io/quickstart/server)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- FastAPI documentation for async handling
- SQLite WAL mode documentation

### External Dependencies
- Python 3.11+
- FastAPI 0.110.2
- MCP SDK 1.9.1
- SQLite 3.35+
- React 18+
- Docker 24+
- Docker Compose 2.20+

### Development Tools
- Python virtual environment
- Node.js 18+ and npm
- SQLite browser for debugging
- Postman/Insomnia for API testing
- Jest/Pytest for testing