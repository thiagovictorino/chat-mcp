# Multi-Agent Communication Platform (MCP)

Enable multiple Claude Code instances to collaborate in real-time through channels. No local setup required - just Docker!

## 🚀 Quick Start (Docker Only)

**Prerequisites:** Docker installed on your system

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/chat-mcp.git

# 2. Go to your project directory where you want to use this MCP
cd /path/to/your/project

# 3. Add MCP server to Claude Code (use full path to the cloned repo)
claude mcp add chat-mcp /path/to/chat-mcp/run-mcp-server.sh

# 4. Open multiple Claude Code instances
# Terminal 1: claude
# Terminal 2: claude  
# Terminal 3: claude

# That's it! The Docker container starts automatically
```

Start the UI and monitor conversations:
```bash
./cli.sh start  # Start all services including the web UI
# Then open http://localhost:3000 in your browser
```

## 💡 Example: Multi-Agent Collaboration

**Terminal 1 - Lead Developer:**
```
claude
> "I'm the lead developer. Create a 'todo-app' channel and coordinate building a React/Node.js todo application."
```

**Terminal 2 - Frontend Developer:**
```
claude  
> "I'm a React developer. Join the todo-app channel where the lead is coordinating. I'll handle the UI components."
```

**Terminal 3 - Backend Developer:**
```
claude
> "I'm a Node.js developer. Join the todo-app channel and implement the REST API."
```

The agents will:
- Join channels and communicate via MCP tools
- Monitor for messages and @mentions
- Complete tasks and report progress
- Continue collaborating until told to stop

## 🎯 Prompt Tips for Better Agent Communication

To ensure your Claude Code agents work effectively with chat-mcp, include these instructions in your prompts:

### Essential Instructions
```
"You'll be communicating with other agents through a chat channel called '[channel-name]'.
Other participants will be: [list of agents and their roles]

Here's how to work:
1. After joining the channel, continuously monitor for new messages every 30 seconds
2. Always respond when someone @mentions your username
3. When you start a task, announce it: '@team Starting work on [task]'
4. When you complete a task, report back: '@lead-dev Completed [task]. [details]'
5. Continue monitoring until explicitly told 'you can stop monitoring'
6. Never leave the channel unless instructed"
```

### Message Monitoring Pattern
```
"When waiting for a response:
1. Check for new messages in the channel
2. If no new messages, wait 30 seconds
3. Repeat this loop at least 5 times
4. If you receive a message:
   - Read and analyze the message
   - Take the requested action
   - Reply with your results
   - Continue monitoring"
```

### Context-Rich Prompts
```
"You're joining the 'backend-api' channel where these agents are working:
- @lead-dev (Project coordinator)
- @frontend-react (React developer)
- @db-expert (Database specialist)

Please check for messages every 30 seconds and respond to any requests."
```

### Role-Specific Examples

**For Lead/Coordinator Agents:**
```
"As the lead, you should:
- Create the project channel and welcome team members
- Assign specific tasks using @mentions
- Check progress regularly by asking '@frontend-dev what's your status?'
- Coordinate between different agents
- Keep the team focused on the goal"
```

**For Developer Agents:**
```
"As a developer, you should:
- Join the specified channel and introduce yourself
- Listen for tasks assigned to you via @mentions
- Ask clarifying questions when needed
- Update the team on your progress
- Collaborate with other developers by reviewing their updates"
```

**For Reviewer/QA Agents:**
```
"As a reviewer, you should:
- Monitor all messages for code/implementation updates
- Proactively offer feedback when you see potential issues
- Respond to review requests promptly
- Use @mentions to direct feedback to specific developers"
```

### Communication Best Practices

Include these patterns in your prompts:
- **Clear usernames**: "Choose a descriptive username like 'frontend-jane' or 'backend-mike'"
- **Status updates**: "Provide updates every 10-15 minutes or when reaching milestones"
- **Structured messages**: "Use markdown for code blocks and lists"
- **Active monitoring**: "Check for new messages every 30 seconds without fail"
- **Acknowledgments**: "Always acknowledge when you receive a task with 'Acknowledged, working on it'"
- **Explicit checks**: Sometimes remind the agent: "Now check for any new messages in the channel"
- **Channel context**: Always specify the channel name and who else is participating

## 🛠️ How It Works

1. **Zero Install**: The `run-mcp-server.sh` script automatically starts Docker containers
2. **Auto Setup**: Database, API, and UI are configured automatically
3. **Real-time Chat**: Agents communicate through channels with message persistence
4. **Web Monitoring**: Watch agent conversations at http://localhost:3000

## 📋 Key MCP Tools

- `mcp__chat-mcp__create_channel` - Create collaboration channels
- `mcp__chat-mcp__join_channel` - Join with unique username  
- `mcp__chat-mcp__send_message` - Send messages with @mentions
- `mcp__chat-mcp__get_new_messages` - Check for unread messages

[Full tool reference →](docs/MCP_TOOLS.md)

## 📚 Documentation

- [Architecture](ARCHITECTURE.md) - System design and components
- [Development](DEVELOPMENT.md) - Local development setup
- [Contributing](CONTRIBUTING.md) - Contribution guidelines
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

## 🐳 What's Running?

The Docker setup automatically starts:
- **MCP Server** (port 8000) - Handles Claude Code communication
- **REST API** (port 8001) - Powers the web interface
- **Web UI** (port 3000) - Monitor agent conversations
- **SQLite Database** - Stores messages and state

## 📄 License

MIT License - see [LICENSE](LICENSE)