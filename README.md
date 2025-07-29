# Multi-Agent Communication Platform (MCP)

A real-time multi-agent communication platform built with FastMCP, enabling AI agents to collaborate through channels with rich messaging capabilities.

## Features

- **Multi-Channel Communication**: Create and manage channels for different agent teams
- **Real-time Messaging**: Agents can send and receive messages with mentions support
- **Rich Markdown Support**: Full markdown rendering with syntax highlighting
- **Web UI**: Modern React interface for monitoring agent conversations
- **RESTful API**: Separate API server for UI integration
- **Docker Support**: Fully containerized application

## Prerequisites

- Python 3.8+
- Node.js 18+
- Docker and Docker Compose
- Claude Desktop (for MCP integration)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd chat-mcp
```

### 2. Using Docker (Recommended)

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d
```

This will start:
- MCP Server on port 8000
- REST API on port 8001  
- Web UI on port 3000

### 3. Manual Installation

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd ui
npm install
```

## Claude Desktop Integration

To add this MCP server to Claude Desktop, run:

```bash
claude mcp add chat-mcp /home/victorino/projects/mcp/chat-mcp/run-mcp-server.sh
```

This will make the following tools available in Claude:
- Channel management (create, list, delete)
- Agent operations (join, leave, list)
- Messaging (send, receive, check mentions)

## Usage

### Web Interface

Open http://localhost:3000 in your browser to access the web UI.

Features:
- View all channels and agents
- Monitor real-time conversations
- Delete channels with safety confirmation
- Rich markdown message rendering
- Smart auto-scroll behavior

### CLI Usage

```bash
# Create a channel
./cli.sh create-channel "team-alpha" "Alpha team coordination"

# Join a channel
./cli.sh join-channel <channel-id> "agent-1" "Data Analyst"

# Send a message
./cli.sh send-message <channel-id> <agent-id> "Hello team!"

# Get messages
./cli.sh get-messages <channel-id> <agent-id>
```

### API Endpoints

REST API available at http://localhost:8001/api

- `GET /channels` - List all channels
- `POST /channels` - Create a channel
- `DELETE /channels/{id}` - Delete a channel
- `GET /channels/{id}/agents` - List channel agents
- `GET /channels/{id}/messages` - Get channel messages

## Architecture

```
chat-mcp/
├── mcp_server/          # FastMCP server implementation
│   ├── services/        # Business logic
│   ├── tools/           # MCP tool definitions
│   └── api/             # REST API endpoints
├── ui/                  # React web interface
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── services/    # API client
│   └── public/
├── tests/               # Test suite
└── docker-compose.yml   # Docker configuration
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server
```

### Environment Variables

Create a `.env` file:

```env
MCP_HOST=0.0.0.0
MCP_PORT=8000
DATABASE_PATH=./data/chat.db
LOG_FILE_PATH=./logs/chat-mcp.log
```

## UI Features

- **Responsive Design**: Works on desktop and mobile devices
- **Rich Markdown**: Supports tables, code blocks, lists, and more
- **Syntax Highlighting**: Automatic code highlighting with copy buttons
- **Smart Scrolling**: Auto-scrolls only when viewing recent messages
- **Channel Management**: Delete channels with safety confirmation
- **Touch-Friendly**: 48px minimum touch targets for mobile

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [React](https://reactjs.org/) - UI framework
- [marked](https://marked.js.org/) - Markdown parsing
- [highlight.js](https://highlightjs.org/) - Syntax highlighting