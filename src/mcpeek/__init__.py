"""MCPeek - An elegant MCP (Model Context Protocol) exploration tool."""

__version__ = "1.0.0"
__author__ = "MCPeek Development Team"
__description__ = "A swiss army knife for AI hackers to explore and interact with MCP endpoints"

from .cli import MCPeekCLI
from .config import ConfigManager
from .auth import AuthManager
from .mcp_client import MCPClient
from .discovery import DiscoveryEngine
from .execution import ExecutionEngine

__all__ = [
    "MCPeekCLI",
    "ConfigManager",
    "AuthManager",
    "MCPClient",
    "DiscoveryEngine",
    "ExecutionEngine",
]