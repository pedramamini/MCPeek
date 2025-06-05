"""Exception classes for MCPeek."""

from typing import Optional, Dict, Any


class MCPeekException(Exception):
    """Base exception for MCPeek."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class ConnectionError(MCPeekException):
    """Connection-related errors."""
    pass


class AuthenticationError(MCPeekException):
    """Authentication failures."""
    pass


class ProtocolError(MCPeekException):
    """MCP protocol violations."""
    pass


class ValidationError(MCPeekException):
    """Input validation errors."""
    pass


class TimeoutError(MCPeekException):
    """Operation timeout errors."""
    pass