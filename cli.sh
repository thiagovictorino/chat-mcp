#!/bin/bash

set -e

COMMAND=${1:-help}

case $COMMAND in
    start)
        echo "Starting MAC-P services..."
        docker compose up -d --build
        echo ""
        echo "Services starting up..."
        echo "- MCP Server (SSE): http://localhost:8000"
        echo "- REST API Server: http://localhost:8001"
        echo "- Web UI: http://localhost:3000"
        echo ""
        echo "Waiting for services to be ready..."
        sleep 5
        echo "✓ Services should now be running!"
        echo ""
        echo "To view logs: ./cli.sh logs"
        echo "To open UI: ./cli.sh web"
        ;;
    
    stop)
        echo "Stopping MAC-P server..."
        docker compose down
        ;;
    
    restart)
        echo "Restarting MAC-P server..."
        docker compose restart
        ;;
    
    logs)
        SERVICE=${2:-mcp-server}
        docker compose logs -f $SERVICE
        ;;
    
    shell)
        docker compose exec mcp-server /bin/bash
        ;;
    
    build)
        echo "Building Docker images..."
        docker compose build
        ;;
    
    db)
        echo "Opening SQLite database..."
        docker compose exec mcp-server sqlite3 /app/data/chat.db
        ;;
    
    test)
        echo "Running tests..."
        docker compose run --rm mcp-server pytest
        ;;
    
    web)
        echo "Opening MAC-P Web UI..."
        # Check if services are running
        if ! docker compose ps | grep -q "Up"; then
            echo "Services are not running. Starting them first..."
            ./cli.sh start
        fi
        # Open browser based on OS
        case "$(uname -s)" in
            Linux*)     xdg-open http://localhost:3000 ;;
            Darwin*)    open http://localhost:3000 ;;
            CYGWIN*|MINGW*|MSYS*) start http://localhost:3000 ;;
            *)          echo "Please open http://localhost:3000 in your browser" ;;
        esac
        ;;
    
    status)
        echo "MAC-P Services Status:"
        echo ""
        docker compose ps
        echo ""
        # Check if services are healthy
        if curl -s http://localhost:8001/api/channels > /dev/null 2>&1; then
            echo "✓ REST API is responding"
        else
            echo "✗ REST API is not responding on port 8001"
        fi
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✓ Web UI is accessible"
        else
            echo "✗ Web UI is not accessible on port 3000"
        fi
        ;;
    
    help|*)
        echo "MAC-P CLI Tool"
        echo ""
        echo "Usage: ./cli.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  start     - Start all services (MCP, API, UI)"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Check services status"
        echo "  web       - Open the web UI in browser"
        echo "  logs      - View logs (optionally specify service: mcp-server, api-server, ui)"
        echo "  shell     - Open bash shell in server container"
        echo "  build     - Build Docker images"
        echo "  db        - Open SQLite database shell"
        echo "  test      - Run test suite"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./cli.sh start       # Start all services"
        echo "  ./cli.sh web         # Open web UI"
        echo "  ./cli.sh logs api-server  # View API server logs"
        echo "  ./cli.sh status      # Check if services are running"
        ;;
esac