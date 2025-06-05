"""STDIO transport implementation for MCP."""

import asyncio
import json
import shlex
from typing import Dict, Any, Optional, List
import subprocess

from .base import BaseTransport
from ..utils.exceptions import ConnectionError, TimeoutError, ProtocolError
from ..utils.helpers import validate_json_rpc_message, safe_json_loads, safe_json_dumps, sanitize_file_path


class STDIOTransport(BaseTransport):
    """STDIO transport for local processes."""

    def __init__(self, command: List[str], timeout: float = 30.0):
        """Initialize STDIO transport with command."""
        super().__init__()
        self.command = command
        self.timeout = timeout
        self.process: Optional[asyncio.subprocess.Process] = None
        self._read_task: Optional[asyncio.Task] = None
        self._response_queue: asyncio.Queue = asyncio.Queue()

    @classmethod
    def from_command_string(cls, command_str: str, timeout: float = 30.0) -> 'STDIOTransport':
        """Create transport from command string."""
        # Parse command string safely
        try:
            command_parts = shlex.split(command_str)
        except ValueError as e:
            raise ValueError(f"Invalid command string: {e}")

        # Sanitize the executable path
        if command_parts:
            command_parts[0] = sanitize_file_path(command_parts[0])

        return cls(command_parts, timeout)

    async def connect(self) -> None:
        """Start subprocess and establish stdio communication."""
        if self._connected:
            return

        try:
            # Start the subprocess
            self.process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Start background task to read responses
            self._read_task = asyncio.create_task(self._read_responses())

            self._connected = True
            self.logger.info(f"Started STDIO process: {' '.join(self.command)}")

        except Exception as e:
            await self._cleanup()
            raise ConnectionError(f"Failed to start process {' '.join(self.command)}: {e}")

    async def _read_responses(self) -> None:
        """Background task to read responses from stdout."""
        if not self.process or not self.process.stdout:
            return

        try:
            while self._connected and not self._closed:
                # Read line from stdout
                line = await self.process.stdout.readline()
                if not line:
                    # Process ended
                    break

                try:
                    # Decode and parse JSON
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        self.logger.debug(f"Received STDIO line: {line_str}")
                        response_data = safe_json_loads(line_str)
                        await self._response_queue.put(response_data)

                except Exception as e:
                    self.logger.warning(f"Failed to parse STDIO response: {e}")

        except Exception as e:
            self.logger.error(f"Error reading STDIO responses: {e}")

    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send JSON-RPC message via stdin."""
        if not self.process or not self.process.stdin or not self._connected:
            raise ConnectionError("Transport not connected")

        try:
            # Validate message structure
            validate_json_rpc_message(message)

            # Convert to JSON and add newline
            json_data = safe_json_dumps(message) + '\n'

            self.logger.debug(f"Sending STDIO message: {json_data.strip()}")

            # Write to stdin
            self.process.stdin.write(json_data.encode('utf-8'))
            await self.process.stdin.drain()

        except Exception as e:
            raise ConnectionError(f"Failed to send STDIO message: {e}")

    async def receive_message(self) -> Dict[str, Any]:
        """Read JSON-RPC message from stdout."""
        if not self._connected:
            raise ConnectionError("Transport not connected")

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(
                self._response_queue.get(),
                timeout=self.timeout
            )

            self.logger.debug(f"Received STDIO response: {response}")

            # Validate response structure
            validate_json_rpc_message(response)

            return response

        except asyncio.TimeoutError:
            raise TimeoutError(f"No response received within {self.timeout}s")

    async def close(self) -> None:
        """Close subprocess and cleanup."""
        if self._closed:
            return

        self._connected = False
        self._closed = True

        await self._cleanup()
        self.logger.info("STDIO transport closed")

    async def _cleanup(self) -> None:
        """Clean up process and tasks."""
        # Cancel read task
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        # Terminate process
        if self.process:
            try:
                # Close stdin first
                if self.process.stdin:
                    self.process.stdin.close()
                    await self.process.stdin.wait_closed()

                # Try graceful termination first
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    # Force kill if graceful termination fails
                    self.process.kill()
                    await self.process.wait()

            except Exception as e:
                self.logger.warning(f"Error during process cleanup: {e}")
            finally:
                self.process = None

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None,
                          request_id: Optional[str] = None) -> Dict[str, Any]:
        """Send STDIO request and wait for response."""
        from ..utils.helpers import create_request_id

        if not self.process or not self._connected:
            raise ConnectionError("Transport not connected")

        # Create request message
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id or create_request_id()
        }

        if params is not None:
            message["params"] = params

        # Send message
        await self.send_message(message)

        # Wait for response
        response = await self.receive_message()

        # Validate response
        if "error" in response:
            error = response["error"]
            raise ProtocolError(f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}")

        return response

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'process') and self.process:
            try:
                self.process.terminate()
            except:
                pass