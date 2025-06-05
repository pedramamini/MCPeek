"""HTTP/HTTPS transport implementation for MCP."""

import asyncio
import json
from typing import Dict, Any, Optional
import aiohttp

from .base import BaseTransport
from ..utils.exceptions import ConnectionError, TimeoutError, ProtocolError
from ..utils.helpers import validate_json_rpc_message, safe_json_loads, safe_json_dumps


class HTTPTransport(BaseTransport):
    """HTTP/HTTPS transport implementation."""

    def __init__(self, url: str, auth_headers: Optional[Dict[str, str]] = None,
                 timeout: float = 30.0):
        """Initialize HTTP transport with URL and auth."""
        super().__init__()
        self.url = url
        self.auth_headers = auth_headers or {}
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self._response_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self) -> None:
        """Establish HTTP connection using aiohttp."""
        if self._connected:
            return

        try:
            # Create session with timeout configuration
            timeout_config = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout_config,
                headers=self.auth_headers
            )

            # Test connection with a simple request
            await self._test_connection()

            self._connected = True
            self.logger.info(f"Connected to HTTP endpoint: {self.url}")

        except Exception as e:
            if self.session:
                await self.session.close()
                self.session = None
            raise ConnectionError(f"Failed to connect to {self.url}: {e}")

    async def _test_connection(self) -> None:
        """Test the HTTP connection."""
        if not self.session:
            raise ConnectionError("No session available")

        try:
            # Try to make a simple request to test connectivity
            async with self.session.post(self.url, json={"test": "connection"}) as response:
                # We don't care about the response content, just that we can connect
                pass
        except aiohttp.ClientError as e:
            raise ConnectionError(f"Connection test failed: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send HTTP POST request with JSON-RPC payload."""
        if not self.session or not self._connected:
            raise ConnectionError("Transport not connected")

        try:
            # Validate message structure
            validate_json_rpc_message(message)

            # Convert to JSON
            json_data = safe_json_dumps(message)

            self.logger.debug(f"Sending HTTP message: {json_data}")

            # Send POST request
            async with self.session.post(
                self.url,
                data=json_data,
                headers={"Content-Type": "application/json"}
            ) as response:

                if response.status >= 400:
                    error_text = await response.text()
                    raise ProtocolError(f"HTTP {response.status}: {error_text}")

                # For HTTP transport, we expect immediate response
                response_text = await response.text()
                if response_text:
                    response_data = safe_json_loads(response_text)
                    await self._response_queue.put(response_data)

        except aiohttp.ClientError as e:
            raise ConnectionError(f"HTTP request failed: {e}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"HTTP request timed out after {self.timeout}s")

    async def receive_message(self) -> Dict[str, Any]:
        """Handle HTTP response or polling for responses."""
        if not self._connected:
            raise ConnectionError("Transport not connected")

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=self.timeout
            )

            self.logger.debug(f"Received HTTP response: {response}")

            # Validate response structure
            validate_json_rpc_message(response)

            return response

        except asyncio.TimeoutError:
            raise TimeoutError(f"No response received within {self.timeout}s")

    async def close(self) -> None:
        """Close HTTP connection."""
        if self._closed:
            return

        self._connected = False
        self._closed = True

        if self.session:
            await self.session.close()
            self.session = None

        self.logger.info("HTTP transport closed")

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None,
                          request_id: Optional[str] = None) -> Dict[str, Any]:
        """Send HTTP request and get immediate response."""
        from ..utils.helpers import create_request_id

        if not self.session or not self._connected:
            raise ConnectionError("Transport not connected")

        # Create request message
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id or create_request_id()
        }

        if params is not None:
            message["params"] = params

        try:
            # Validate message structure
            validate_json_rpc_message(message)

            # Convert to JSON
            json_data = safe_json_dumps(message)

            self.logger.debug(f"Sending HTTP request: {method}")

            # Send POST request and get response
            async with self.session.post(
                self.url,
                data=json_data,
                headers={"Content-Type": "application/json"}
            ) as response:

                if response.status >= 400:
                    error_text = await response.text()
                    raise ProtocolError(f"HTTP {response.status}: {error_text}")

                response_text = await response.text()
                if not response_text:
                    raise ProtocolError("Empty response from server")

                response_data = safe_json_loads(response_text)

                # Validate response
                validate_json_rpc_message(response_data)

                if "error" in response_data:
                    error = response_data["error"]
                    raise ProtocolError(f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")

                return response_data

        except aiohttp.ClientError as e:
            raise ConnectionError(f"HTTP request failed: {e}")
        except asyncio.TimeoutError:
            raise TimeoutError(f"HTTP request timed out after {self.timeout}s")