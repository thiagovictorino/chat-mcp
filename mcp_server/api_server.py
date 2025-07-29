"""
Separate REST API server for the UI
Runs on port 8001 while MCP server runs on port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

# Create FastAPI app
app = FastAPI(title="MAC-P REST API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routes
from mcp_server.api import router
app.include_router(router, prefix="/api")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    from mcp_server.models.database import init_database
    from mcp_server.utils.logging import setup_logging
    
    setup_logging()
    await init_database()
    print(f"MAC-P REST API Server started on port 8001")

if __name__ == "__main__":
    uvicorn.run(
        "mcp_server.api_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )