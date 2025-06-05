"""Abstract base transport for MCP communication."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio

from ..utils.logging import get_logger


class BaseTransport(ABC):
    """Abstract base for all transports."""

    def __init__(self):
        self.logger = get_logger()
        self._connected = False
        self._closed = False

    @property
    def is_connected(self) -> bool:
        """Check if transport is connected."""
        return self._connected and not self._closed

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to MCP endpoint."""
        pass

    @abstractmethod
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message to endpoint."""
        pass

    @abstractmethod
    async def receive_message(self) -> Dict[str, Any]:
        """Receive JSON-RPC message from endpoint."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close connection to endpoint."""
        pass

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None,
                          request_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request and wait for response."""
        from ..utils.helpers import create_request_id

        if not self.is_connected:
            raise RuntimeError("Transport not connected")

        # Create request message
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id or create_request_id()
        }

        if params is not None:
            message["params"] = params

        self.logger.debug(f"Sending request: {method}")
        await self.send_message(message)

        # Wait for response
        response = await self.receive_message()

        # Validate response
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")

        return response

    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self.is_connected:
            raise RuntimeError("Transport not connected")

        # Create notification message (no id field)
        message = {
            "jsonrpc": "2.0",
            "method": method
        }

        if params is not None:
            message["params"] = params

        self.logger.debug(f"Sending notification: {method}")
        await self.send_message(message)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()