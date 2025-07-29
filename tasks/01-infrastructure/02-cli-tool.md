# Task: Create CLI Management Tool

## Description
Create a shell script CLI tool to manage the Docker containers and provide easy server management commands.

## Acceptance Criteria
- [ ] CLI script executable from project root
- [ ] Commands: start, stop, restart, logs, shell
- [ ] Proper error handling and user feedback
- [ ] Works without local Python installation

## Implementation Steps

1. Create `cli.sh`:
```bash
#!/bin/bash

set -e

COMMAND=${1:-help}

case $COMMAND in
    start)
        echo "Starting MAC-P server..."
        docker-compose up -d
        echo "Server started at http://localhost:8000"
        echo "UI available at http://localhost:3000"
        ;;
    
    stop)
        echo "Stopping MAC-P server..."
        docker-compose down
        ;;
    
    restart)
        echo "Restarting MAC-P server..."
        docker-compose restart
        ;;
    
    logs)
        SERVICE=${2:-mcp-server}
        docker-compose logs -f $SERVICE
        ;;
    
    shell)
        docker-compose exec mcp-server /bin/bash
        ;;
    
    build)
        echo "Building Docker images..."
        docker-compose build
        ;;
    
    db)
        echo "Opening SQLite database..."
        docker-compose exec mcp-server sqlite3 /app/data/chat.db
        ;;
    
    test)
        echo "Running tests..."
        docker-compose exec mcp-server pytest
        ;;
    
    help|*)
        echo "MAC-P CLI Tool"
        echo ""
        echo "Usage: ./cli.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start     - Start the server and UI"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  logs      - View logs (optionally specify service)"
        echo "  shell     - Open bash shell in server container"
        echo "  build     - Build Docker images"
        echo "  db        - Open SQLite database shell"
        echo "  test      - Run test suite"
        echo "  help      - Show this help message"
        ;;
esac
```

2. Make executable:
```bash
chmod +x cli.sh
```

## Dependencies
- Task 01 (Docker setup) completed

## Estimated Time: 20 minutes