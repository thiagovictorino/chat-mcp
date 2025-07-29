# Context

## Scenario
As a developer, I want to be able to start many agents and subagents to execute different part of a project or interact with each other with different POV. I want that each agent can talk with each other as it was a slack channel and then the can send and read messages to each other. 

## Problem

The problem we want to solve with this project is the lack of communication between ai agents when they are running in parallel. 

Sometimes, an agent needs to talk with other agents to create a agentic conversation to achieve a goal more rapidly and effectively.

## Solution
To solve this problem, we need to create a MCP Server where each agent can connect in a specific channel and talk with each other.

## Feature Requirements
- The project will manage channels where each channel has one unique identifier.

- Each agent can join to a channel with an user (unique) and a short description about his role in that channel.

- When an agent want to talk to onother specific agent, this agent can tag with @ the target agent user. For example, "Hey @php-developer, what do you think about..."

- When an agent read the message, the chat manager should mark that message as read by that specific agent.

- When an agent requests for new messages, only those not readed messages should return to the requester.

- When an agent join in the channel, the agent cannot read the whole history, only new messages.

- The agent can request for the last X messages in the channel and in this case, it will return all messages from the history, even if the message was already read the that agent.
- The agent can request for the last X from another specific agent and it will return even if that agent has already read those messages.

## Tech stack
- We will use python as our main language to develop this MCP server
- Lets use Docker to run the python, we dont want to have python insalled locally, to we should have a Dockerfile and a compose.yml to manage our containers
- We should be able to run commands in the docker using a CLI created in shell or python to start the server
- To store the channels, we will use SQLite
- The application should have an UI where the I, as a developer, can follow all the conversation happenning within agents.
    - The UI can be simple, it it auto fetch new messages will be great. You can use react.js
- The architecture can be simple, but decoupled from the MCP, do it is easy to extendo it later, the MCP Server will be an interface to interact with the application
- The MCP server will be a http server, not stdio or other protocol.

## Some tasks to run before start with project
- Read the documentation in https://modelcontextprotocol.io/quickstart/server
- You can also read this doc https://github.com/modelcontextprotocol/python-sdk

Here is one example of MCP server that I have used before

```requirements.txt
fastapi==0.110.2
uvicorn[standard]==0.29.0
httpx==0.27.0
python-dotenv==1.0.1
mcp==1.9.1 
```

server.py
```py
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance with stateless HTTP for better scalability
mcp = FastMCP("Weather MCP Server", stateless_http=True)

# Import tool modules so their @mcp.tool decorators register functions
from mcp_server.tools import weather  # noqa: E402, F401

# Optional: expose the run helper
run = mcp.run

if __name__ == "__main__":
    mcp.run() 
```

tools/weather.py
```py
import os
import httpx
from dotenv import load_dotenv

from mcp_server.server import mcp

load_dotenv()

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@mcp.tool()
async def weather(lat: float, lon: float) -> dict:
    """Return current weather for the given coordinates (metric units)."""
    if not OPEN_WEATHER_API_KEY:
        raise RuntimeError("Environment variable OPEN_WEATHER_API_KEY not set")

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "metric",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_WEATHER_URL, params=params)
        resp.raise_for_status()
        return resp.json() 
```

tools/__init__.py
```py
from importlib import import_module

# Ensure tool modules are imported when package is initialized
_module_names = [
    "mcp_server.tools.weather",
]

for _name in _module_names:
    import_module(_name) 
```

Dockerfile
```
# Use official Python image as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port (change if needed)
EXPOSE 8000

# Default command
CMD ["python", "-m", "mcp_server"] 
```

Use these code as reference of another project that I have done.



