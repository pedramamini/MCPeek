#!/usr/bin/env python3
"""
MCPeek Web Interface Backend
FastAPI server exposing MCPeek functionality via REST API
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Add MCPeek to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcpeek.cli import main as mcpeek_main
from mcpeek.config import Config
from mcpeek.auth import AuthManager  
from mcpeek.mcp_client import MCPClient
from mcpeek.discovery import DiscoveryEngine
from mcpeek.execution import ExecutionEngine
from mcpeek.transports.http import HTTPTransport
from mcpeek.transports.stdio import STDIOTransport
from mcpeek.formatters.json import JSONFormatter
from mcpeek.utils.exceptions import MCPeekError

# Configuration
HOST = os.getenv("MCPEEK_HOST", "127.0.0.1")
PORT = int(os.getenv("MCPEEK_PORT", 8080))
DEBUG = os.getenv("MCPEEK_DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("MCPEEK_LOG_LEVEL", "INFO").upper()
CORS_ORIGINS = os.getenv("MCPEEK_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# FastAPI app
app = FastAPI(
    title="MCPeek Web Interface API",
    description="Badass hacker-themed web interface for MCP exploration",
    version="1.0.0",
    docs_url="/api/docs" if DEBUG else None,
    redoc_url="/api/redoc" if DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class MCPEndpoint(BaseModel):
    url: str = Field(..., description="MCP endpoint URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom authorization header")

class DiscoverRequest(BaseModel):
    endpoint: MCPEndpoint
    verbosity: int = Field(1, ge=1, le=3, description="Verbosity level (1-3)")

class ToolRequest(BaseModel):
    endpoint: MCPEndpoint
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters as JSON")

class ResourceRequest(BaseModel):
    endpoint: MCPEndpoint
    uri: str = Field(..., description="Resource URI to read")

class PromptRequest(BaseModel):
    endpoint: MCPEndpoint
    name: str = Field(..., description="Prompt name")
    arguments: Optional[Dict[str, Any]] = Field(None, description="Prompt arguments as JSON")

class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

# Global state
current_sessions: Dict[str, Dict] = {}

async def create_mcp_session(endpoint: MCPEndpoint) -> Dict:
    """Create and initialize an MCP client session"""
    try:
        # Create configuration
        config = Config()
        config.endpoint_url = endpoint.url
        config.api_key = endpoint.api_key
        config.auth_header = endpoint.auth_header
        
        # Create auth manager
        auth_manager = AuthManager(config)
        
        # Determine transport type
        if endpoint.url.startswith(('http://', 'https://')):
            transport = HTTPTransport(endpoint.url, auth_manager)
        else:
            transport = STDIOTransport(endpoint.url, auth_manager)
            
        # Create MCP client
        client = MCPClient(transport)
        
        return {
            'client': client,
            'transport': transport,
            'config': config,
            'auth_manager': auth_manager,
            'connected': False
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create MCP session: {str(e)}")

async def ensure_connected(session: Dict) -> None:
    """Ensure MCP client is connected"""
    if not session['connected']:
        try:
            await session['client'].connect()
            session['connected'] = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to MCP endpoint: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "version": "1.0.0",
            "endpoints": len(current_sessions)
        }
    )

@app.post("/api/discover")
async def discover_endpoint(request: DiscoverRequest) -> APIResponse:
    """Discover MCP endpoint capabilities"""
    import time
    start_time = time.time()
    
    try:
        # Create session
        session_id = f"{request.endpoint.url}_{hash(request.endpoint.url)}"
        session = await create_mcp_session(request.endpoint)
        await ensure_connected(session)
        
        # Create discovery engine
        formatter = JSONFormatter()
        discovery = DiscoveryEngine(session['client'], formatter)
        
        # Perform discovery
        results = await discovery.discover_all(verbosity=request.verbosity)
        
        # Store session for reuse
        current_sessions[session_id] = session
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=results,
            execution_time=execution_time
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time
        )

@app.post("/api/tool")
async def execute_tool(request: ToolRequest) -> APIResponse:
    """Execute an MCP tool"""
    import time
    start_time = time.time()
    
    try:
        # Create session
        session_id = f"{request.endpoint.url}_{hash(request.endpoint.url)}"
        
        # Reuse existing session or create new one
        if session_id in current_sessions:
            session = current_sessions[session_id]
        else:
            session = await create_mcp_session(request.endpoint)
            current_sessions[session_id] = session
            
        await ensure_connected(session)
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(session['client'], formatter)
        
        # Execute tool
        results = await execution.execute_tool(request.tool_name, request.parameters or {})
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=results,
            execution_time=execution_time
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time
        )

@app.post("/api/resource")
async def read_resource(request: ResourceRequest) -> APIResponse:
    """Read an MCP resource"""
    import time
    start_time = time.time()
    
    try:
        # Create session
        session_id = f"{request.endpoint.url}_{hash(request.endpoint.url)}"
        
        # Reuse existing session or create new one
        if session_id in current_sessions:
            session = current_sessions[session_id]
        else:
            session = await create_mcp_session(request.endpoint)
            current_sessions[session_id] = session
            
        await ensure_connected(session)
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(session['client'], formatter)
        
        # Read resource
        results = await execution.read_resource(request.uri)
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=results,
            execution_time=execution_time
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time
        )

@app.post("/api/prompt")
async def get_prompt(request: PromptRequest) -> APIResponse:
    """Get an MCP prompt"""
    import time
    start_time = time.time()
    
    try:
        # Create session
        session_id = f"{request.endpoint.url}_{hash(request.endpoint.url)}"
        
        # Reuse existing session or create new one
        if session_id in current_sessions:
            session = current_sessions[session_id]
        else:
            session = await create_mcp_session(request.endpoint)
            current_sessions[session_id] = session
            
        await ensure_connected(session)
        
        # Create execution engine
        formatter = JSONFormatter()
        execution = ExecutionEngine(session['client'], formatter)
        
        # Get prompt
        results = await execution.get_prompt(request.name, request.arguments or {})
        
        execution_time = time.time() - start_time
        
        return APIResponse(
            success=True,
            data=results,
            execution_time=execution_time
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time
        )

@app.delete("/api/sessions")
async def clear_sessions():
    """Clear all active sessions"""
    try:
        # Close all connections
        for session in current_sessions.values():
            if session['connected']:
                try:
                    await session['client'].disconnect()
                except:
                    pass
        
        current_sessions.clear()
        
        return APIResponse(
            success=True,
            data={"message": "All sessions cleared"}
        )
        
    except Exception as e:
        return APIResponse(
            success=False,
            error=str(e)
        )

# Serve static files
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
    
    @app.get("/")
    async def serve_index():
        return FileResponse(str(STATIC_DIR / "index.html"))

if __name__ == "__main__":
    print(f"""
    ████████████████████████████████████████████████████████████████████████████████
    ██                                                                            ██
    ██  ███    ███  ██████ ██████  ███████ ███████ ██   ██                       ██
    ██  ████  ████ ██      ██   ██ ██      ██      ██  ██                        ██
    ██  ██ ████ ██ ██      ██████  █████   █████   █████                         ██
    ██  ██  ██  ██ ██      ██      ██      ██      ██  ██                        ██
    ██  ██      ██  ██████ ██      ███████ ███████ ██   ██                       ██
    ██                                                                            ██
    ██            🚀 BACKEND API SERVER - RUNNING 🚀                             ██
    ██                                                                            ██
    ████████████████████████████████████████████████████████████████████████████████
    
    🌐 Server: http://{HOST}:{PORT}
    📚 API Docs: http://{HOST}:{PORT}/api/docs
    🐞 Debug Mode: {DEBUG}
    🔧 Log Level: {LOG_LEVEL}
    """)
    
    uvicorn.run(
        "app:app" if DEBUG else app,
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL.lower(),
        reload=DEBUG
    )