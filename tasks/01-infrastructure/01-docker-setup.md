# Task: Docker Environment Setup

## Description
Set up the Docker environment for running the Python MCP server without requiring local Python installation.

## Acceptance Criteria
- [ ] Dockerfile created for Python 3.11 slim image
- [ ] docker-compose.yml configured with proper services
- [ ] Python dependencies installed in container
- [ ] Volume mounts for code and data persistence
- [ ] Container runs without requiring local Python

## Implementation Steps

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "-m", "mcp_server"]
```

2. Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./mcp_server:/app/mcp_server
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - MCP_HOST=0.0.0.0
      - MCP_PORT=8000
      - DATABASE_PATH=/app/data/chat.db
      - LOG_FILE_PATH=/app/logs/chat-mcp.log
    restart: unless-stopped

  ui:
    build: ./ui
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - mcp-server
```

3. Create initial `requirements.txt`:
```
fastapi==0.110.2
uvicorn[standard]==0.29.0
httpx==0.27.0
python-dotenv==1.0.1
mcp==1.9.1
aiosqlite==0.19.0
```

## Dependencies
- Docker 24+
- Docker Compose 2.20+

## Estimated Time: 30 minutes