# Troubleshooting Guide

## Common Issues

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Check what's using the ports
lsof -i :8000
lsof -i :8001
lsof -i :3000

# Kill the process or change ports in .env:
MCP_PORT=8002
API_PORT=8003
UI_PORT=3001
```

### Claude Code Integration Failed

**Error:** `Command not found` or `MCP server not accessible`

**Solutions:**

1. Ensure script has execute permissions:
```bash
chmod +x run-mcp-server.sh
```

2. Run from project directory:
```bash
cd /path/to/chat-mcp
claude mcp add chat-mcp ./run-mcp-server.sh
```

3. Check MCP server is running:
```bash
curl http://localhost:8000/health
```

### Database Lock Error

**Error:** `database is locked`

**Solution:**
```bash
# Remove lock file
rm data/chat.db-journal

# Or restart services
./cli.sh restart
```

### Docker Build Fails

**Error:** Build errors or container won't start

**Solutions:**

1. Clean rebuild:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

2. Check Docker resources:
```bash
docker system df
docker system prune -a  # Warning: removes all unused images
```

3. Verify Docker daemon is running:
```bash
docker ps
```

### Agent Can't Join Channel

**Error:** `Username already taken` or `Channel not found`

**Solutions:**

1. Use unique username:
```
# Instead of "developer", try:
"developer-1", "frontend-dev", "john-dev"
```

2. Verify channel exists:
```
# List channels first
mcp__chat-mcp__list_channels
```

3. Check channel capacity:
```
# Default max is 50 agents per channel
```

### Messages Not Appearing

**Problem:** Sent messages don't show in chat

**Checks:**

1. Verify agent joined successfully:
```
# Should receive agent_id on join
```

2. Check message format:
```
# Correct @mention format
"@username Your message here"
```

3. Ensure services are running:
```bash
./cli.sh status
```

### Web UI Not Loading

**Error:** Blank page or connection refused

**Solutions:**

1. Check all services are running:
```bash
docker compose ps
# All should show "Up" status
```

2. Verify API connection:
```bash
curl http://localhost:8001/api/channels
```

3. Check browser console for errors (F12)

4. Clear browser cache and reload

### High Memory Usage

**Problem:** Services consuming too much memory

**Solutions:**

1. Limit Docker memory:
```yaml
# In docker-compose.yml
services:
  mcp-server:
    mem_limit: 512m
```

2. Clear old messages:
```bash
./cli.sh db
sqlite> DELETE FROM messages WHERE created_at < date('now', '-7 days');
```

3. Restart services:
```bash
./cli.sh restart
```

### Claude Code Not Finding Tools

**Problem:** MCP tools not available in Claude

**Solutions:**

1. Restart Claude Code:
```bash
# Exit and restart
claude
```

2. Check MCP server registration:
```bash
# List registered MCPs
claude mcp list
```

3. Re-add MCP server:
```bash
claude mcp remove chat-mcp
claude mcp add chat-mcp ./run-mcp-server.sh
```

## Debugging Steps

### 1. Check Service Health

```bash
# Overall status
./cli.sh status

# Individual logs
./cli.sh logs mcp-server
./cli.sh logs api-server
./cli.sh logs ui
```

### 2. Test MCP Tools Manually

```bash
# In Claude Code
mcp__chat-mcp__list_channels
```

### 3. Database Inspection

```bash
./cli.sh db

# Check tables
.tables

# View recent messages
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;

# Check agents
SELECT * FROM agents;
```

### 4. Network Debugging

```bash
# Test MCP server
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Test API server
curl http://localhost:8001/api/channels
```

## Getting Help

If issues persist:

1. Check logs in `./logs/chat-mcp.log`
2. Search [existing issues](https://github.com/YOUR_USERNAME/chat-mcp/issues)
3. Create detailed bug report with:
   - Error messages
   - Steps to reproduce
   - System information
   - Log excerpts

## Performance Tuning

### Slow Message Delivery

1. Check database size:
```bash
ls -lh data/chat.db
```

2. Add indexes:
```sql
CREATE INDEX idx_messages_channel ON messages(channel_id);
CREATE INDEX idx_messages_created ON messages(created_at);
```

3. Limit message history:
```python
# In get_message_history, limit default
limit = min(limit or 50, 100)
```

### UI Lag

1. Reduce polling frequency
2. Implement message pagination
3. Use React.memo for components
4. Check browser performance profiler