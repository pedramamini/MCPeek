"""
MCPeek Web API Backend

FastAPI server that exposes MCPeek functionality via REST endpoints.
"""

import asyncio
import json
from typing import Any, Dict, Optional, List
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os
import sys

# Add the src directory to Python path so we can import mcpeek
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mcpeek.config import ConfigManager
from mcpeek.auth import AuthManager
from mcpeek.transports.http import HTTPTransport
from mcpeek.transports.stdio import STDIOTransport
from mcpeek.mcp_client import MCPClient
from mcpeek.discovery import DiscoveryEngine
from mcpeek.execution import ExecutionEngine
from mcpeek.formatters.json import JSONFormatter
from mcpeek.utils.exceptions import MCPeekException
from mcpeek.utils.helpers import parse_endpoint_url
from mcpeek.utils.logging import logging_manager, get_logger

# Initialize logging
logging_manager.setup_logging("INFO")
logger = get_logger()

app = FastAPI(
    title="MCPeek Web API",
    description="Web interface for MCPeek - MCP Protocol exploration tool",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class MCPEndpointRequest(BaseModel):
    endpoint: str = Field(..., description="MCP endpoint URL or command")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    auth_header: Optional[str] = Field(None, description="Custom auth header")
    timeout: float = Field(30.0, description="Connection timeout in seconds")

class DiscoveryRequest(MCPEndpointRequest):
    verbosity: int = Field(0, description="Verbosity level (0-3)")
    tool_tickle: bool = Field(False, description="Test safe tools during discovery")

class ToolExecutionRequest(MCPEndpointRequest):
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters")

class ResourceRequest(MCPEndpointRequest):
    resource_uri: str = Field(..., description="URI of the resource to read")

class PromptRequest(MCPEndpointRequest):
    prompt_name: str = Field(..., description="Name of the prompt to get")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Prompt parameters")

# Response models
class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

class MCPClientManager:
    """Manages MCP client connections and operations."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
    
    async def create_client(self, request: MCPEndpointRequest) -> MCPClient:
        """Create and connect an MCP client."""
        # Parse endpoint info
        endpoint_info = parse_endpoint_url(request.endpoint)
        
        # Get authentication headers
        auth_headers = self.auth_manager.get_auth_headers(
            request.endpoint,
            request.api_key,
            request.auth_header
        )
        
        # Create transport
        if endpoint_info['type'] == 'http':
            transport = HTTPTransport(request.endpoint, auth_headers, request.timeout)
        else:
            # STDIO transport
            if ' ' in request.endpoint:
                transport = STDIOTransport.from_command_string(request.endpoint, request.timeout)
            else:
                transport = STDIOTransport([request.endpoint], request.timeout)
        
        # Connect and create client
        await transport.connect()
        return MCPClient(transport)

client_manager = MCPClientManager()

@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build', 'index.html'))

@app.post("/api/discover", response_model=MCPResponse)
async def discover_endpoint(request: DiscoveryRequest):
    """Discover MCP endpoint capabilities."""
    try:
        client = await client_manager.create_client(request)
        
        try:
            discovery_engine = DiscoveryEngine(client, request.verbosity, request.tool_tickle)
            result = await discovery_engine.discover_endpoint()
            
            # Format as JSON for web interface
            formatter = JSONFormatter(pretty_print=False)
            formatted_result = formatter.format_discovery_result(result)
            
            return MCPResponse(success=True, data=json.loads(formatted_result))
            
        finally:
            await client.close()
            
    except MCPeekException as e:
        logger.error(f"MCPeek error in discovery: {e}")
        return MCPResponse(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in discovery: {e}")
        return MCPResponse(success=False, error=f"Unexpected error: {str(e)}")

@app.post("/api/execute/tool", response_model=MCPResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute an MCP tool."""
    try:
        client = await client_manager.create_client(request)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.execute_tool(request.tool_name, request.parameters)
            
            # Format as JSON for web interface
            formatter = JSONFormatter(pretty_print=False)
            formatted_result = formatter.format_tool_result(result)
            
            return MCPResponse(success=True, data=json.loads(formatted_result))
            
        finally:
            await client.close()
            
    except MCPeekException as e:
        logger.error(f"MCPeek error in tool execution: {e}")
        return MCPResponse(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in tool execution: {e}")
        return MCPResponse(success=False, error=f"Unexpected error: {str(e)}")

@app.post("/api/execute/resource", response_model=MCPResponse)
async def read_resource(request: ResourceRequest):
    """Read an MCP resource."""
    try:
        client = await client_manager.create_client(request)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.read_resource(request.resource_uri)
            
            # Format as JSON for web interface
            formatter = JSONFormatter(pretty_print=False)
            formatted_result = formatter.format_resource_result(result)
            
            return MCPResponse(success=True, data=json.loads(formatted_result))
            
        finally:
            await client.close()
            
    except MCPeekException as e:
        logger.error(f"MCPeek error in resource reading: {e}")
        return MCPResponse(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in resource reading: {e}")
        return MCPResponse(success=False, error=f"Unexpected error: {str(e)}")

@app.post("/api/execute/prompt", response_model=MCPResponse)
async def get_prompt(request: PromptRequest):
    """Get an MCP prompt."""
    try:
        client = await client_manager.create_client(request)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.get_prompt(request.prompt_name, request.parameters)
            
            # Format as JSON for web interface  
            formatter = JSONFormatter(pretty_print=False)
            formatted_result = formatter.format_tool_result(result)  # Prompts use same format as tools
            
            return MCPResponse(success=True, data=json.loads(formatted_result))
            
        finally:
            await client.close()
            
    except MCPeekException as e:
        logger.error(f"MCPeek error in prompt retrieval: {e}")
        return MCPResponse(success=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in prompt retrieval: {e}")
        return MCPResponse(success=False, error=f"Unexpected error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mcpeek-web-api"}

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)