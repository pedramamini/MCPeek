"""
MCPeek Web API Backend

FastAPI server that exposes MCPeek functionality via REST endpoints.
"""

import asyncio
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional, List

from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, HttpUrl, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Add the src directory to Python path safely
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path.resolve()))

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
log_level = os.getenv("MCPEEK_LOG_LEVEL", "INFO")
logging_manager.setup_logging(log_level)
logger = get_logger()

# Configuration from environment
CORS_ORIGINS = os.getenv("MCPEEK_CORS_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",")
API_HOST = os.getenv("MCPEEK_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("MCPEEK_API_PORT", "8080"))
RATE_LIMIT = os.getenv("MCPEEK_RATE_LIMIT", "60/minute")
TRUSTED_HOSTS = os.getenv("MCPEEK_TRUSTED_HOSTS", "localhost,127.0.0.1").split(",")

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer(auto_error=False)

app = FastAPI(
    title="MCPeek Web API",
    description="Web interface for MCPeek - MCP Protocol exploration tool",
    version="1.0.0",
    docs_url="/docs" if os.getenv("MCPEEK_DEBUG") else None,
    redoc_url="/redoc" if os.getenv("MCPEEK_DEBUG") else None
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add trusted host middleware for security
app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

# CORS middleware with secure defaults
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Auth-Header"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)

# Request models with validation
class MCPEndpointRequest(BaseModel):
    endpoint: str = Field(..., min_length=1, max_length=2048, description="MCP endpoint URL or command")
    timeout: float = Field(30.0, ge=1.0, le=300.0, description="Connection timeout in seconds")
    
    @validator('endpoint')
    def validate_endpoint(cls, v):
        # Basic validation for endpoint format
        if not v or v.isspace():
            raise ValueError('Endpoint cannot be empty')
        return v.strip()

class DiscoveryRequest(MCPEndpointRequest):
    verbosity: int = Field(0, description="Verbosity level (0-3)")
    tool_tickle: bool = Field(False, description="Test safe tools during discovery")

class ToolExecutionRequest(MCPEndpointRequest):
    tool_name: str = Field(..., min_length=1, max_length=256, description="Name of the tool to execute")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Tool parameters")
    
    @validator('tool_name')
    def validate_tool_name(cls, v):
        if not v or v.isspace():
            raise ValueError('Tool name cannot be empty')
        return v.strip()

class ResourceRequest(MCPEndpointRequest):
    resource_uri: str = Field(..., min_length=1, max_length=2048, description="URI of the resource to read")
    
    @validator('resource_uri')
    def validate_resource_uri(cls, v):
        if not v or v.isspace():
            raise ValueError('Resource URI cannot be empty')
        return v.strip()

class PromptRequest(MCPEndpointRequest):
    prompt_name: str = Field(..., min_length=1, max_length=256, description="Name of the prompt to get")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Prompt parameters")
    
    @validator('prompt_name')
    def validate_prompt_name(cls, v):
        if not v or v.isspace():
            raise ValueError('Prompt name cannot be empty')
        return v.strip()

# Response models
class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None
    
    class Config:
        # Don't expose internal model details
        arbitrary_types_allowed = True

class MCPClientManager:
    """Manages MCP client connections and operations."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.auth_manager = AuthManager()
    
    async def create_client(self, request: MCPEndpointRequest, api_key: Optional[str] = None, auth_header: Optional[str] = None) -> MCPClient:
        """Create and connect an MCP client."""
        try:
            # Parse endpoint info
            endpoint_info = parse_endpoint_url(request.endpoint)
            
            # Get authentication headers from request headers, not body
            auth_headers = self.auth_manager.get_auth_headers(
                request.endpoint,
                api_key,
                auth_header
            )
        except Exception as e:
            logger.error(f"Failed to parse endpoint or auth: {e}")
            raise MCPeekException(f"Invalid endpoint configuration: {str(e)}")
        
        # Create transport
        if endpoint_info['type'] == 'http':
            transport = HTTPTransport(request.endpoint, auth_headers, request.timeout)
        else:
            # STDIO transport
            if ' ' in request.endpoint:
                transport = STDIOTransport.from_command_string(request.endpoint, request.timeout)
            else:
                transport = STDIOTransport([request.endpoint], request.timeout)
        
        # Connect and create client with timeout
        try:
            await asyncio.wait_for(transport.connect(), timeout=request.timeout)
            return MCPClient(transport)
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout after {request.timeout}s")
            raise MCPeekException(f"Connection timeout after {request.timeout} seconds")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise MCPeekException(f"Failed to connect to endpoint")

client_manager = MCPClientManager()

# Authentication helpers
def get_api_key(x_api_key: Optional[str] = Header(None)) -> Optional[str]:
    """Extract API key from headers."""
    return x_api_key

def get_auth_header(x_auth_header: Optional[str] = Header(None)) -> Optional[str]:
    """Extract custom auth header from headers."""
    return x_auth_header

def get_auth_from_bearer(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract API key from Bearer token."""
    return credentials.credentials if credentials else None

def create_error_response(message: str, details: Optional[str] = None) -> MCPResponse:
    """Create a sanitized error response."""
    # Log detailed error server-side
    if details:
        logger.error(f"API Error: {message} - Details: {details}")
    else:
        logger.error(f"API Error: {message}")
    
    # Return generic error to client in production
    if os.getenv("MCPEEK_DEBUG"):
        return MCPResponse(success=False, error=f"{message}: {details}" if details else message)
    else:
        return MCPResponse(success=False, error="An error occurred processing your request")

@app.get("/")
async def serve_frontend():
    """Serve the React frontend."""
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build', 'index.html'))

@app.post("/api/discover", response_model=MCPResponse)
@limiter.limit(RATE_LIMIT)
async def discover_endpoint(
    request: Request,
    discovery_request: DiscoveryRequest,
    api_key: Optional[str] = Depends(get_api_key),
    auth_header: Optional[str] = Depends(get_auth_header),
    bearer_token: Optional[str] = Depends(get_auth_from_bearer)
):
    """Discover MCP endpoint capabilities."""
    client = None
    try:
        # Use bearer token as fallback for API key
        final_api_key = api_key or bearer_token
        
        client = await client_manager.create_client(discovery_request, final_api_key, auth_header)
        
        discovery_engine = DiscoveryEngine(client, discovery_request.verbosity, discovery_request.tool_tickle)
        result = await discovery_engine.discover_endpoint()
        
        # Format as JSON for web interface
        formatter = JSONFormatter(pretty_print=False)
        formatted_result = formatter.format_discovery_result(result)
        
        return MCPResponse(success=True, data=json.loads(formatted_result))
        
    except MCPeekException as e:
        return create_error_response("Discovery failed", str(e))
    except json.JSONDecodeError as e:
        return create_error_response("Invalid response format", str(e))
    except Exception as e:
        return create_error_response("Discovery failed", str(e))
    finally:
        if client:
            try:
                await client.close()
            except Exception as close_error:
                logger.error(f"Error closing client: {close_error}")

@app.post("/api/execute/tool", response_model=MCPResponse)
@limiter.limit(RATE_LIMIT)
async def execute_tool(
    request: Request,
    tool_request: ToolExecutionRequest,
    api_key: Optional[str] = Depends(get_api_key),
    auth_header: Optional[str] = Depends(get_auth_header),
    bearer_token: Optional[str] = Depends(get_auth_from_bearer)
):
    """Execute an MCP tool."""
    client = None
    try:
        # Use bearer token as fallback for API key
        final_api_key = api_key or bearer_token
        
        client = await client_manager.create_client(tool_request, final_api_key, auth_header)
        
        execution_engine = ExecutionEngine(client)
        result = await execution_engine.execute_tool(tool_request.tool_name, tool_request.parameters)
        
        # Format as JSON for web interface
        formatter = JSONFormatter(pretty_print=False)
        formatted_result = formatter.format_tool_result(result)
        
        return MCPResponse(success=True, data=json.loads(formatted_result))
        
    except MCPeekException as e:
        return create_error_response("Tool execution failed", str(e))
    except json.JSONDecodeError as e:
        return create_error_response("Invalid response format", str(e))
    except Exception as e:
        return create_error_response("Tool execution failed", str(e))
    finally:
        if client:
            try:
                await client.close()
            except Exception as close_error:
                logger.error(f"Error closing client: {close_error}")

@app.post("/api/execute/resource", response_model=MCPResponse)
@limiter.limit(RATE_LIMIT)
async def read_resource(
    request: Request,
    resource_request: ResourceRequest,
    api_key: Optional[str] = Depends(get_api_key),
    auth_header: Optional[str] = Depends(get_auth_header),
    bearer_token: Optional[str] = Depends(get_auth_from_bearer)
):
    """Read an MCP resource."""
    client = None
    try:
        # Use bearer token as fallback for API key
        final_api_key = api_key or bearer_token
        
        client = await client_manager.create_client(resource_request, final_api_key, auth_header)
        
        execution_engine = ExecutionEngine(client)
        result = await execution_engine.read_resource(resource_request.resource_uri)
        
        # Format as JSON for web interface
        formatter = JSONFormatter(pretty_print=False)
        formatted_result = formatter.format_resource_result(result)
        
        return MCPResponse(success=True, data=json.loads(formatted_result))
        
    except MCPeekException as e:
        return create_error_response("Resource read failed", str(e))
    except json.JSONDecodeError as e:
        return create_error_response("Invalid response format", str(e))
    except Exception as e:
        return create_error_response("Resource read failed", str(e))
    finally:
        if client:
            try:
                await client.close()
            except Exception as close_error:
                logger.error(f"Error closing client: {close_error}")

@app.post("/api/execute/prompt", response_model=MCPResponse)
@limiter.limit(RATE_LIMIT)
async def get_prompt(
    request: Request,
    prompt_request: PromptRequest,
    api_key: Optional[str] = Depends(get_api_key),
    auth_header: Optional[str] = Depends(get_auth_header),
    bearer_token: Optional[str] = Depends(get_auth_from_bearer)
):
    """Get an MCP prompt."""
    client = None
    try:
        # Use bearer token as fallback for API key
        final_api_key = api_key or bearer_token
        
        client = await client_manager.create_client(prompt_request, final_api_key, auth_header)
        
        execution_engine = ExecutionEngine(client)
        result = await execution_engine.get_prompt(prompt_request.prompt_name, prompt_request.parameters)
        
        # Format as JSON for web interface  
        formatter = JSONFormatter(pretty_print=False)
        formatted_result = formatter.format_tool_result(result)  # Prompts use same format as tools
        
        return MCPResponse(success=True, data=json.loads(formatted_result))
        
    except MCPeekException as e:
        return create_error_response("Prompt retrieval failed", str(e))
    except json.JSONDecodeError as e:
        return create_error_response("Invalid response format", str(e))
    except Exception as e:
        return create_error_response("Prompt retrieval failed", str(e))
    finally:
        if client:
            try:
                await client.close()
            except Exception as close_error:
                logger.error(f"Error closing client: {close_error}")

@app.get("/api/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint with detailed status."""
    import time
    import platform
    
    return {
        "status": "healthy",
        "service": "mcpeek-web-api",
        "version": "1.0.0",
        "timestamp": time.time(),
        "uptime": time.time() - getattr(health_check, '_start_time', time.time()),
        "python_version": platform.python_version(),
        "environment": {
            "cors_origins": len(CORS_ORIGINS),
            "rate_limit": RATE_LIMIT,
            "debug_mode": bool(os.getenv("MCPEEK_DEBUG"))
        }
    }

# Set start time for uptime calculation
health_check._start_time = time.time()

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build')
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

if __name__ == "__main__":
    import uvicorn
    import time
    
    # Set start time for health check
    health_check._start_time = time.time()
    
    logger.info(f"Starting MCPeek Web API on {API_HOST}:{API_PORT}")
    logger.info(f"CORS Origins: {CORS_ORIGINS}")
    logger.info(f"Rate Limit: {RATE_LIMIT}")
    logger.info(f"Debug Mode: {bool(os.getenv('MCPEEK_DEBUG'))}")
    
    uvicorn.run(
        app, 
        host=API_HOST, 
        port=API_PORT,
        log_level=log_level.lower(),
        access_log=bool(os.getenv("MCPEEK_ACCESS_LOG", "true"))
    )