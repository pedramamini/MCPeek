#!/usr/bin/env python3
"""
MCPeek Web Interface Backend
FastAPI server exposing MCPeek functionality via REST API
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add parent directory to path to import MCPeek
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcpeek.config import MCPeekConfig
from mcpeek.auth import AuthManager
from mcpeek.mcp_client import MCPClient
from mcpeek.discovery import DiscoveryEngine
from mcpeek.execution import ExecutionEngine
from mcpeek.transports.http import HTTPTransport
from mcpeek.transports.stdio import StdioTransport
from mcpeek.formatters.json import JSONFormatter
from mcpeek.utils.exceptions import MCPeekError
from mcpeek.utils.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(level=os.getenv("MCPEEK_LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Request/Response Models
class EndpointRequest(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class DiscoverRequest(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    verbosity: int = Field(1, ge=1, le=3, description="Verbosity level (1-3)")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class ToolRequest(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class ResourceRequest(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    resource_uri: str = Field(..., description="Resource URI to read")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class PromptRequest(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    prompt_name: str = Field(..., description="Name of the prompt to get")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Prompt arguments")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

# Global session manager
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, MCPClient] = {}
    
    async def get_client(self, url: str, api_key: Optional[str] = None, 
                        auth_header: Optional[str] = None) -> MCPClient:
        """Get or create MCP client for endpoint"""
        session_key = f"{url}:{api_key or ''}:{auth_header or ''}"
        
        if session_key not in self.sessions:
            # Create configuration
            config = MCPeekConfig(
                endpoint_url=url,
                api_key=api_key,
                auth_header=auth_header,
                formatter="json",
                timeout=30.0
            )
            
            # Create auth manager
            auth_manager = AuthManager(config)
            
            # Create transport
            if url.startswith(('http://', 'https://')):
                transport = HTTPTransport(config, auth_manager)
            else:
                # Assume local command for STDIO
                transport = StdioTransport(config, auth_manager)
            
            # Create client
            client = MCPClient(transport)
            await client.connect()
            
            self.sessions[session_key] = client
        
        return self.sessions[session_key]
    
    async def cleanup(self):
        """Clean up all sessions"""
        for client in self.sessions.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client: {e}")
        self.sessions.clear()

# Global session manager instance
session_manager = SessionManager()

# Create FastAPI app
app = FastAPI(
    title="MCPeek Web Interface",
    description="Badass hacker-themed web interface for exploring MCP endpoints",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
cors_origins = os.getenv("MCPEEK_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "MCPeek Web Interface is running",
        "version": "1.0.0"
    }

@app.post("/api/discover")
async def discover_endpoint(request: DiscoverRequest):
    """Discover MCP endpoint capabilities"""
    try:
        client = await session_manager.get_client(
            request.url, 
            request.api_key, 
            request.auth_header
        )
        
        # Create discovery engine
        formatter = JSONFormatter()
        discovery = DiscoveryEngine(client, formatter)
        
        # Perform discovery
        result = await discovery.discover(verbosity=request.verbosity)
        
        return {
            "success": True,
            "data": result,
            "endpoint": request.url
        }
        
    except Exception as e:
        logger.error(f"Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tool")
async def execute_tool(request: ToolRequest):
    """Execute MCP tool"""
    try:
        client = await session_manager.get_client(
            request.url,
            request.api_key,
            request.auth_header
        )
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(client, formatter)
        
        # Execute tool
        result = await execution.execute_tool(request.tool_name, request.parameters)
        
        return {
            "success": True,
            "data": result,
            "tool": request.tool_name,
            "endpoint": request.url
        }
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resource")
async def read_resource(request: ResourceRequest):
    """Read MCP resource"""
    try:
        client = await session_manager.get_client(
            request.url,
            request.api_key,
            request.auth_header
        )
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(client, formatter)
        
        # Read resource
        result = await execution.read_resource(request.resource_uri)
        
        return {
            "success": True,
            "data": result,
            "resource": request.resource_uri,
            "endpoint": request.url
        }
        
    except Exception as e:
        logger.error(f"Resource read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompt")
async def get_prompt(request: PromptRequest):
    """Get MCP prompt"""
    try:
        client = await session_manager.get_client(
            request.url,
            request.api_key,
            request.auth_header
        )
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(client, formatter)
        
        # Get prompt
        result = await execution.get_prompt(request.prompt_name, request.arguments)
        
        return {
            "success": True,
            "data": result,
            "prompt": request.prompt_name,
            "endpoint": request.url
        }
        
    except Exception as e:
        logger.error(f"Prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get server status"""
    return {
        "success": True,
        "data": {
            "active_sessions": len(session_manager.sessions),
            "endpoints": list(set(url.split(":")[0] for url in session_manager.sessions.keys())),
            "server": {
                "host": os.getenv("MCPEEK_WEB_HOST", "127.0.0.1"),
                "port": int(os.getenv("MCPEEK_WEB_PORT", "8080")),
                "debug": os.getenv("MCPEEK_DEBUG", "false").lower() == "true"
            }
        }
    }

# Serve static files and frontend
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the React frontend"""
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(), status_code=200)
        else:
            return HTMLResponse(
                content="<h1>MCPeek Web Interface</h1><p>Frontend not built. Run 'npm run build' in frontend directory.</p>",
                status_code=503
            )
else:
    @app.get("/")
    async def serve_placeholder():
        """Serve placeholder when frontend not available"""
        return HTMLResponse(
            content="""
            <html>
                <head><title>MCPeek Web Interface</title></head>
                <body style="background: #000; color: #00ff00; font-family: monospace; padding: 20px;">
                    <h1>🚀 MCPeek Web Interface</h1>
                    <p>Frontend not available. Build the frontend with:</p>
                    <pre>cd frontend && npm install && npm run build</pre>
                    <p>API Documentation: <a href="/api/docs" style="color: #00ff00;">/api/docs</a></p>
                </body>
            </html>
            """,
            status_code=503
        )

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up sessions on shutdown"""
    await session_manager.cleanup()

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("MCPEEK_WEB_HOST", "127.0.0.1")
    port = int(os.getenv("MCPEEK_WEB_PORT", "8080"))
    debug = os.getenv("MCPEEK_DEBUG", "false").lower() == "true"
    
    print(f"🚀 Starting MCPeek Web Interface on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/api/docs")
    print(f"🎮 Terminal Interface: http://{host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )