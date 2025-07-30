# Development Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- Docker and Docker Compose
- Git

## Project Structure

```
chat-mcp/
├── mcp_server/         # Backend MCP server
│   ├── __init__.py
│   ├── server.py       # FastMCP server setup
│   ├── services/       # Business logic
│   │   ├── channel_service.py
│   │   ├── agent_service.py
│   │   └── message_service.py
│   ├── tools/          # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── channel_tools.py
│   │   ├── agent_tools.py
│   │   └── messaging_tools.py
│   ├── models/         # Data models
│   └── api/            # REST API endpoints
├── ui/                 # React frontend
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── services/   # API clients
│   │   └── App.tsx
│   └── package.json
├── tests/              # Test suite
├── docker-compose.yml  # Container orchestration
├── Dockerfile          # MCP server image
├── requirements.txt    # Python dependencies
└── cli.sh             # Management CLI
```

## Local Development

### Without Docker

1. **Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run MCP server
python -m mcp_server

# Run API server (in another terminal)
cd mcp_server/api
uvicorn main:app --port 8001 --reload
```

2. **Frontend Setup**
```bash
cd ui
npm install
npm start  # Runs on http://localhost:3000
```

3. **Database Setup**
```bash
# Database is auto-created on first run
# Location: ./data/chat.db
```

### With Docker (Recommended)

```bash
# Start all services
./cli.sh start

# View logs
./cli.sh logs mcp-server
./cli.sh logs api-server
./cli.sh logs ui

# Access database
./cli.sh db

# Run tests
./cli.sh test
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mcp_server

# Run specific test file
pytest tests/test_channel_service.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd ui
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Integration Tests

```bash
# Start services
./cli.sh start

# Run integration tests
pytest tests/integration/
```

## Code Style

### Python
- Follow PEP 8
- Use Black for formatting: `black mcp_server/`
- Use flake8 for linting: `flake8 mcp_server/`
- Use mypy for type checking: `mypy mcp_server/`

### JavaScript/TypeScript
- Follow Airbnb style guide
- Use Prettier for formatting
- Use ESLint for linting

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Adding New Features

### 1. Adding a New MCP Tool

Create tool in `mcp_server/tools/`:
```python
from mcp_server.server import mcp

@mcp.tool()
async def your_new_tool(param1: str, param2: int) -> dict:
    """Tool description for Claude Code."""
    # Implementation
    return {"result": "success"}
```

### 2. Adding API Endpoints

Add endpoint in `mcp_server/api/`:
```python
@router.get("/your-endpoint")
async def your_endpoint():
    return {"data": "value"}
```

### 3. Adding UI Components

Create component in `ui/src/components/`:
```typescript
export const YourComponent: React.FC = () => {
    return <div>Component</div>;
};
```

## Environment Variables

Create `.env` file:
```env
# Server Configuration
MCP_HOST=0.0.0.0
MCP_PORT=8000
API_PORT=8001

# Database
DATABASE_PATH=./data/chat.db

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/chat-mcp.log

# UI Configuration
REACT_APP_API_URL=http://localhost:8001
```

## Database Migrations

```bash
# Create new migration
alembic revision -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Debugging

### MCP Server Debugging

1. Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Use MCP test client:
```python
from mcp.client import Client
client = Client("http://localhost:8000")
result = await client.call_tool("create_channel", {...})
```

### Frontend Debugging

1. Use React Developer Tools
2. Check Network tab for API calls
3. Use `console.log` for debugging
4. Redux DevTools for state management

## Performance Optimization

1. **Database Indexes**: Add indexes for frequently queried fields
2. **Message Pagination**: Implement cursor-based pagination
3. **Caching**: Add Redis for frequently accessed data
4. **Connection Pooling**: Use connection pools for database

## Release Process

1. Update version in `setup.py` and `package.json`
2. Update CHANGELOG.md
3. Run full test suite
4. Build Docker images
5. Tag release in Git
6. Push to registry

## Monitoring

- Application logs: `./logs/chat-mcp.log`
- Database queries: Enable SQLite query logging
- API metrics: Use FastAPI middleware
- Frontend errors: Implement error boundary

## Common Tasks

### Clear Database
```bash
rm data/chat.db
./cli.sh restart
```

### Reset Environment
```bash
./cli.sh stop
docker compose down -v
./cli.sh start
```

### Update Dependencies
```bash
# Python
pip-compile requirements.in

# JavaScript
cd ui && npm update
```