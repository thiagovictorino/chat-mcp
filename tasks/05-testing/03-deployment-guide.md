# Task: Create Deployment Guide

## Description
Create comprehensive documentation for deploying and running the Multi-Agent Communication Platform.

## Acceptance Criteria
- [ ] README.md with project overview
- [ ] Installation instructions
- [ ] Usage examples
- [ ] API documentation
- [ ] Troubleshooting guide

## Implementation Steps

1. Create `README.md`:
```markdown
# Multi-Agent Communication Platform (MAC-P)

A Model Context Protocol (MCP) server that enables real-time communication between AI agents through channel-based messaging with @ mentions and read tracking.

## Features

- **Channel Management**: Create and manage communication channels with unique names
- **Agent Communication**: Agents join channels with unique usernames and roles
- **@ Mentions**: Direct messages to specific agents using @username syntax
- **Read Receipts**: Track which agents have read each message
- **Message History**: Retrieve messages with automatic read marking
- **Web UI**: Monitor all agent conversations in real-time
- **MCP Tools**: Complete set of tools for agent integration

## Quick Start

### Prerequisites

- Docker 24+
- Docker Compose 2.20+

### Installation

1. Clone the repository:
\`\`\`bash
git clone https://github.com/your-org/chat-mcp.git
cd chat-mcp
\`\`\`

2. Create environment file:
\`\`\`bash
cp .env.example .env
\`\`\`

3. Start the services:
\`\`\`bash
./cli.sh start
\`\`\`

The MCP server will be available at `http://localhost:8000` and the UI at `http://localhost:3000`.

## Usage

### CLI Commands

\`\`\`bash
./cli.sh start    # Start all services
./cli.sh stop     # Stop all services
./cli.sh logs     # View logs
./cli.sh shell    # Access server shell
./cli.sh db       # Access SQLite database
./cli.sh test     # Run tests
\`\`\`

### Using MCP Tools

The server exposes the following MCP tools:

#### Channel Operations
- `create_channel(name, description, max_agents)` - Create a new channel
- `list_channels(limit, offset)` - List available channels
- `get_channel_info(channel_name, channel_id)` - Get channel details

#### Agent Operations
- `join_channel(channel_id, username, role_description)` - Join a channel
- `leave_channel(channel_id, agent_id)` - Leave a channel
- `list_channel_agents(channel_id)` - List agents in channel

#### Messaging Operations
- `send_message(channel_id, agent_id, content)` - Send a message
- `get_new_messages(channel_id, agent_id, limit)` - Get unread messages
- `get_message_history(channel_id, agent_id, limit, before_sequence)` - Get message history
- `check_mentions(channel_id, agent_id, limit)` - Check for mentions

### Example Agent Workflow

\`\`\`python
# 1. Create a channel
channel = create_channel(
    name="project-discussion",
    description="Discuss project implementation"
)

# 2. Join the channel
agent = join_channel(
    channel_id=channel["channel_id"],
    username="backend-dev",
    role_description="Backend development specialist"
)

# 3. Send a message
send_message(
    channel_id=channel["channel_id"],
    agent_id=agent["agent_id"],
    content="Hello team! @frontend-dev, shall we discuss the API?"
)

# 4. Check for new messages
messages = get_new_messages(
    channel_id=channel["channel_id"],
    agent_id=agent["agent_id"]
)

# 5. Leave when done
leave_channel(
    channel_id=channel["channel_id"],
    agent_id=agent["agent_id"]
)
\`\`\`

## API Documentation

### REST API Endpoints

The server also exposes REST endpoints for the UI:

- `GET /api/channels` - List channels
- `POST /api/channels` - Create channel
- `GET /api/channels/{id}/agents` - List agents
- `GET /api/channels/{id}/messages` - Get messages
- `GET /api/logs` - Get system logs

### Message Format

Messages support @ mentions which are automatically parsed:
\`\`\`
"Hey @alice, can you review the code? @bob might have insights too."
\`\`\`

## Configuration

Edit `.env` file to configure:

\`\`\`env
# Server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Database
DATABASE_PATH=/app/data/chat.db
MESSAGE_RETENTION_DAYS=30

# UI
UI_PORT=3000
UI_REFRESH_INTERVAL_MS=2000

# Logging
LOG_LEVEL=INFO
\`\`\`

## Development

### Running Tests

\`\`\`bash
./cli.sh test
\`\`\`

### Project Structure

\`\`\`
chat-mcp/
├── mcp_server/          # MCP server implementation
│   ├── tools/           # MCP tool definitions
│   ├── services/        # Business logic
│   └── models/          # Database models
├── ui/                  # React monitoring UI
├── tests/               # Test suite
└── tasks/               # Development task breakdown
\`\`\`

## Troubleshooting

### Common Issues

1. **Port already in use**
   \`\`\`bash
   ./cli.sh stop
   docker-compose down -v
   ./cli.sh start
   \`\`\`

2. **Database locked**
   - Ensure only one instance is running
   - Check SQLite WAL mode is enabled

3. **UI not updating**
   - Check browser console for errors
   - Verify API URL in environment

### Debugging

View logs:
\`\`\`bash
./cli.sh logs mcp-server
./cli.sh logs ui
\`\`\`

Access database:
\`\`\`bash
./cli.sh db
.tables
SELECT * FROM channels;
\`\`\`

## License

MIT

## Contributing

See CONTRIBUTING.md for guidelines.
```

2. Create `CONTRIBUTING.md`:
```markdown
# Contributing to MAC-P

## Development Setup

1. Fork and clone the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./cli.sh test`
5. Submit a pull request

## Code Style

- Python: Follow PEP 8
- TypeScript: Use ESLint configuration
- Write tests for new features
- Update documentation

## Commit Messages

Use conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
```

3. Create `docs/API.md` for detailed API documentation...

## Dependencies
- All implementation completed
- Tests passing

## Estimated Time: 45 minutes