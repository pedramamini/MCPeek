"""Core MCP protocol implementation."""

import asyncio
from typing import Dict, Any, List, Optional

from .transports.base import BaseTransport
from .utils.exceptions import ProtocolError, ConnectionError
from .utils.logging import get_logger
from .utils.helpers import create_request_id
from .version_detection import MCPVersionDetector, MCPVersionInfo


class MCPClient:
    """Core MCP protocol implementation."""

    def __init__(self, transport: BaseTransport):
        """Initialize client with transport layer."""
        self.transport = transport
        self.logger = get_logger()
        self._initialized = False
        self._server_capabilities = {}
        self._server_info = {}
        self._version_info = None
        self._version_detector = MCPVersionDetector()
        self._client_capabilities = {
            "experimental": {},
            "sampling": {},
            "roots": {
                "listChanged": False
            }
        }

    async def initialize_connection(self) -> Dict[str, Any]:
        """Perform MCP initialization handshake."""
        if self._initialized:
            return self._server_capabilities

        try:
            # Send initialize request
            init_params = {
                "protocolVersion": "2024-11-05",
                "capabilities": self._client_capabilities,
                "clientInfo": {
                    "name": "mcpeek",
                    "version": "1.0.0"
                }
            }

            self.logger.debug("Sending initialize request")
            response = await self.transport.send_request("initialize", init_params)

            if "result" not in response:
                raise ProtocolError("Initialize response missing result")

            result = response["result"]
            self._server_capabilities = result.get("capabilities", {})
            self._server_info = result.get("serverInfo", {})

            self.logger.debug(f"Server info: {self._server_info.get('name', 'unknown')} v{self._server_info.get('version', 'unknown')}")
            self.logger.debug(f"Server capabilities: {list(self._server_capabilities.keys())}")

            # Perform version detection
            server_info_for_detection = {
                "protocol_version": result.get("protocolVersion", init_params["protocolVersion"]),
                "server_name": self._server_info.get("name", "unknown"),
                "server_version": self._server_info.get("version", "unknown")
            }
            
            self._version_info = self._version_detector.detect_version(
                server_info_for_detection,
                self._server_capabilities
            )
            
            self.logger.info(f"Detected MCP specification version: {self._version_info.specification_version}")

            # Send initialized notification
            await self.transport.send_notification("notifications/initialized")

            self._initialized = True
            self.logger.info("MCP connection initialized successfully")

            return result

        except Exception as e:
            self.logger.error(f"Failed to initialize MCP connection: {e}")
            raise ConnectionError(f"MCP initialization failed: {e}")

    async def negotiate_capabilities(self) -> Dict[str, Any]:
        """Negotiate client/server capabilities."""
        if not self._initialized:
            await self.initialize_connection()

        return {
            "client_capabilities": self._client_capabilities,
            "server_capabilities": self._server_capabilities
        }

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from server."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            self.logger.debug("Requesting tools list")
            response = await self.transport.send_request("tools/list")

            # Handle empty or malformed responses gracefully
            if not response or not isinstance(response, dict):
                self.logger.warning("Received empty or invalid response for tools/list")
                return []

            if "result" not in response:
                self.logger.warning("Tools list response missing result field")
                return []

            result = response["result"]
            if not isinstance(result, dict):
                self.logger.warning("Tools list result is not a dictionary")
                return []

            tools = result.get("tools", [])
            self.logger.info(f"Retrieved {len(tools)} tools")
            return tools

        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            raise ProtocolError(f"Failed to list tools: {e}")

    async def list_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources from server."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            self.logger.debug("Requesting resources list")
            response = await self.transport.send_request("resources/list")

            # Handle empty or malformed responses gracefully
            if not response or not isinstance(response, dict):
                self.logger.warning("Received empty or invalid response for resources/list")
                return []

            if "result" not in response:
                self.logger.warning("Resources list response missing result field")
                return []

            result = response["result"]
            if not isinstance(result, dict):
                self.logger.warning("Resources list result is not a dictionary")
                return []

            resources = result.get("resources", [])
            self.logger.info(f"Retrieved {len(resources)} resources")
            return resources

        except Exception as e:
            self.logger.error(f"Failed to list resources: {e}")
            raise ProtocolError(f"Failed to list resources: {e}")

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available prompts from server."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            self.logger.debug("Requesting prompts list")
            response = await self.transport.send_request("prompts/list")

            # Handle empty or malformed responses gracefully
            if not response or not isinstance(response, dict):
                self.logger.warning("Received empty or invalid response for prompts/list")
                return []

            if "result" not in response:
                self.logger.warning("Prompts list response missing result field")
                return []

            result = response["result"]
            if not isinstance(result, dict):
                self.logger.warning("Prompts list result is not a dictionary")
                return []

            prompts = result.get("prompts", [])
            self.logger.info(f"Retrieved {len(prompts)} prompts")
            return prompts

        except Exception as e:
            self.logger.error(f"Failed to list prompts: {e}")
            raise ProtocolError(f"Failed to list prompts: {e}")

    async def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific tool with arguments."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            params = {"name": name}
            if arguments:
                params["arguments"] = arguments

            self.logger.debug(f"Calling tool: {name}")
            response = await self.transport.send_request("tools/call", params)

            if "result" not in response:
                raise ProtocolError("Tool call response missing result")

            result = response["result"]
            self.logger.info(f"Tool {name} executed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to call tool {name}: {e}")
            raise ProtocolError(f"Failed to call tool {name}: {e}")

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource by URI."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            params = {"uri": uri}

            self.logger.debug(f"Reading resource: {uri}")
            response = await self.transport.send_request("resources/read", params)

            if "result" not in response:
                raise ProtocolError("Resource read response missing result")

            result = response["result"]
            self.logger.info(f"Resource {uri} read successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to read resource {uri}: {e}")
            raise ProtocolError(f"Failed to read resource {uri}: {e}")

    async def get_prompt(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a specific prompt with arguments."""
        if not self._initialized:
            await self.initialize_connection()

        try:
            params = {"name": name}
            if arguments:
                params["arguments"] = arguments

            self.logger.debug(f"Getting prompt: {name}")
            response = await self.transport.send_request("prompts/get", params)

            if "result" not in response:
                raise ProtocolError("Prompt get response missing result")

            result = response["result"]
            self.logger.info(f"Prompt {name} retrieved successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to get prompt {name}: {e}")
            raise ProtocolError(f"Failed to get prompt {name}: {e}")

    async def ping(self) -> bool:
        """Send a ping to test connection."""
        if not self._initialized:
            return False

        try:
            response = await self.transport.send_request("ping")
            return "result" in response
        except Exception:
            return False

    async def get_server_info(self) -> Dict[str, Any]:
        """Get server information and capabilities."""
        if not self._initialized:
            await self.initialize_connection()

        server_info = {
            "capabilities": self._server_capabilities,
            "protocol_version": "2024-11-05",
            "initialized": self._initialized,
            "server_info": self._server_info
        }
        
        # Add version information if available
        if self._version_info:
            server_info["version_info"] = self._version_detector.get_version_summary(self._version_info)
            
        return server_info

    async def close(self) -> None:
        """Close the MCP client connection."""
        try:
            if self._initialized and self.transport.is_connected:
                # Send a goodbye notification if the server supports it
                try:
                    await self.transport.send_notification("goodbye")
                except Exception:
                    # Ignore errors during goodbye
                    pass

            await self.transport.close()
            self._initialized = False
            self.logger.info("MCP client connection closed")

        except Exception as e:
            self.logger.warning(f"Error during client close: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize_connection()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized

    @property
    def server_capabilities(self) -> Dict[str, Any]:
        """Get server capabilities."""
        return self._server_capabilities.copy()

    def supports_capability(self, capability: str) -> bool:
        """Check if server supports a specific capability."""
        return capability in self._server_capabilities

    def get_version_info(self) -> Optional[MCPVersionInfo]:
        """Get detected MCP version information."""
        return self._version_info

    def get_server_version_summary(self) -> Dict[str, Any]:
        """Get a summary of server version information."""
        if not self._version_info:
            return {"status": "not_detected"}
        
        return self._version_detector.get_version_summary(self._version_info)

    def is_server_compatible(self) -> bool:
        """Check if server is compatible with this client."""
        if not self._version_info:
            return False
        
        return self._version_detector.is_compatible_with_client(self._version_info)