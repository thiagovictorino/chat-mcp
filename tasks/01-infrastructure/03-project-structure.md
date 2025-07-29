# Task: Create Project Directory Structure

## Description
Set up the complete project directory structure for the MCP server and UI components.

## Acceptance Criteria
- [ ] All necessary directories created
- [ ] Python package structure properly initialized
- [ ] Configuration files in place
- [ ] Git ignore patterns set up

## Implementation Steps

1. Create directory structure:
```bash
chat-mcp/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py          # FastMCP server initialization
│   ├── tools/             # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── channel.py     # Channel management tools
│   │   ├── agent.py       # Agent management tools
│   │   └── messaging.py   # Messaging tools
│   ├── models/            # Data models
│   │   ├── __init__.py
│   │   └── database.py    # SQLAlchemy models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── channel_service.py
│   │   ├── agent_service.py
│   │   └── message_service.py
│   └── utils/             # Utilities
│       ├── __init__.py
│       ├── database.py    # DB connection
│       └── logging.py     # Logging setup
├── ui/                    # React frontend
│   ├── Dockerfile
│   ├── package.json
│   ├── public/
│   └── src/
├── data/                  # SQLite database (git ignored)
├── logs/                  # Log files (git ignored)
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_channels.py
│   ├── test_agents.py
│   └── test_messages.py
├── .env.example           # Environment template
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── cli.sh
└── README.md
```

2. Create `.gitignore`:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Database
data/
*.db
*.db-journal
*.db-wal

# Logs
logs/
*.log

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node
node_modules/
ui/build/
ui/.env.local
```

3. Create `.env.example`:
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

## Dependencies
- Tasks 01-02 completed

## Estimated Time: 15 minutes