"""FastAPI backend for MCPeek web interface."""

import asyncio
import json
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

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


class MCPCommand(BaseModel):
    """Base command model."""
    endpoint: str
    api_key: Optional[str] = None
    auth_header: Optional[str] = None
    timeout: float = 30.0


class DiscoveryCommand(MCPCommand):
    """Discovery command model."""
    verbosity: int = Field(default=0, ge=0, le=3)
    tool_tickle: bool = False


class ToolCommand(MCPCommand):
    """Tool execution command model."""
    tool_name: str
    input_data: Optional[Dict[str, Any]] = None


class ResourceCommand(MCPCommand):
    """Resource command model."""
    resource_uri: str


class PromptCommand(MCPCommand):
    """Prompt command model."""
    prompt_name: str
    input_data: Optional[Dict[str, Any]] = None


class MCPeekWebBackend:
    """MCPeek web backend service."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
        self.active_connections: List[WebSocket] = []
    
    async def create_transport_and_client(self, command: MCPCommand) -> tuple[Any, MCPClient]:
        """Create transport and MCP client from command."""
        endpoint_info = parse_endpoint_url(command.endpoint)
        
        # Get authentication headers
        auth_headers = self.auth_manager.get_auth_headers(
            command.endpoint,
            command.api_key,
            command.auth_header
        )
        
        # Create transport
        if endpoint_info['type'] == 'http':
            transport = HTTPTransport(command.endpoint, auth_headers, command.timeout)
        else:
            # STDIO transport
            if ' ' in command.endpoint:
                transport = STDIOTransport.from_command_string(command.endpoint, command.timeout)
            else:
                transport = STDIOTransport([command.endpoint], command.timeout)
        
        await transport.connect()
        client = MCPClient(transport)
        
        return transport, client
    
    async def execute_discovery(self, command: DiscoveryCommand) -> dict:
        """Execute MCP discovery."""
        transport, client = await self.create_transport_and_client(command)
        
        try:
            discovery_engine = DiscoveryEngine(client, command.verbosity, command.tool_tickle)
            result = await discovery_engine.discover_endpoint()
            
            # Format result as JSON
            formatter = JSONFormatter(pretty_print=True)
            formatted_result = formatter.format_discovery_result(result)
            
            return {
                "success": True,
                "data": json.loads(formatted_result),
                "raw_output": formatted_result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await client.close()
    
    async def execute_tool(self, command: ToolCommand) -> dict:
        """Execute MCP tool."""
        transport, client = await self.create_transport_and_client(command)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.execute_tool(command.tool_name, command.input_data)
            
            # Format result as JSON
            formatter = JSONFormatter(pretty_print=True)
            formatted_result = formatter.format_tool_result(result)
            
            return {
                "success": True,
                "data": json.loads(formatted_result),
                "raw_output": formatted_result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await client.close()
    
    async def read_resource(self, command: ResourceCommand) -> dict:
        """Read MCP resource."""
        transport, client = await self.create_transport_and_client(command)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.read_resource(command.resource_uri)
            
            # Format result as JSON
            formatter = JSONFormatter(pretty_print=True)
            formatted_result = formatter.format_resource_result(result)
            
            return {
                "success": True,
                "data": json.loads(formatted_result),
                "raw_output": formatted_result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await client.close()
    
    async def get_prompt(self, command: PromptCommand) -> dict:
        """Get MCP prompt."""
        transport, client = await self.create_transport_and_client(command)
        
        try:
            execution_engine = ExecutionEngine(client)
            result = await execution_engine.get_prompt(command.prompt_name, command.input_data)
            
            # Format result as JSON
            formatter = JSONFormatter(pretty_print=True)
            formatted_result = formatter.format_tool_result(result)  # Prompts use same format as tools
            
            return {
                "success": True,
                "data": json.loads(formatted_result),
                "raw_output": formatted_result
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await client.close()


# Initialize backend
backend = MCPeekWebBackend()

# Create FastAPI app
app = FastAPI(
    title="MCPeek Web Interface",
    description="Badass hacker-style web interface for MCPeek MCP exploration tool",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - serve the React app."""
    return FileResponse("/app/web/frontend/build/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "online", "service": "MCPeek Web Backend"}


@app.post("/api/discover")
async def discover_endpoint(command: DiscoveryCommand):
    """Discover MCP endpoint capabilities."""
    try:
        result = await backend.execute_discovery(command)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


@app.post("/api/tool")
async def execute_tool(command: ToolCommand):
    """Execute MCP tool."""
    try:
        result = await backend.execute_tool(command)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@app.post("/api/resource")
async def read_resource(command: ResourceCommand):
    """Read MCP resource."""
    try:
        result = await backend.read_resource(command)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource read failed: {str(e)}")


@app.post("/api/prompt")
async def get_prompt(command: PromptCommand):
    """Get MCP prompt."""
    try:
        result = await backend.get_prompt(command)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt get failed: {str(e)}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    backend.active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be extended for real-time features
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        backend.active_connections.remove(websocket)


# Serve static files (React build)
app.mount("/static", StaticFiles(directory="/app/web/frontend/build/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MCPeek Web Interface - Hacker Terminal Mode")
    print("🌐 Access at: http://localhost:8080")
    print("💀 Prepare for the most badass MCP exploration experience...")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )