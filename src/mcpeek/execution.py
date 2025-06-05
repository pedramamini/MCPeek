"""Execution engine for MCP operations."""

import sys
import json
from typing import Dict, Any, Optional

from .mcp_client import MCPClient
from .utils.exceptions import ValidationError, ProtocolError
from .utils.logging import get_logger
from .utils.helpers import safe_json_loads, sanitize_file_path


class ExecutionEngine:
    """Executes specific MCP operations."""

    def __init__(self, client: MCPClient):
        """Initialize execution engine with MCP client."""
        self.client = client
        self.logger = get_logger()

    async def execute_tool(self, tool_name: str, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Execute a specific tool with input data."""
        try:
            self.logger.info(f"Executing tool: {tool_name}")

            # Process input data
            arguments = {}
            if input_data is not None:
                arguments = self.process_input_data(input_data)

            # Validate tool exists and get its schema
            await self._validate_tool_exists(tool_name)

            # Execute the tool
            result = await self.client.call_tool(tool_name, arguments)

            self.logger.info(f"Tool {tool_name} executed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool_name}: {e}")
            raise

    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read a specific resource."""
        try:
            self.logger.info(f"Reading resource: {resource_uri}")

            # Validate resource exists
            await self._validate_resource_exists(resource_uri)

            # Read the resource
            result = await self.client.read_resource(resource_uri)

            self.logger.info(f"Resource {resource_uri} read successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to read resource {resource_uri}: {e}")
            raise

    async def get_prompt(self, prompt_name: str, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Get a specific prompt with arguments."""
        try:
            self.logger.info(f"Getting prompt: {prompt_name}")

            # Process input data
            arguments = {}
            if input_data is not None:
                arguments = self.process_input_data(input_data)

            # Validate prompt exists
            await self._validate_prompt_exists(prompt_name)

            # Get the prompt
            result = await self.client.get_prompt(prompt_name, arguments)

            self.logger.info(f"Prompt {prompt_name} retrieved successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to get prompt {prompt_name}: {e}")
            raise

    def process_input_data(self, input_source: Any) -> Dict[str, Any]:
        """Process input data from various sources."""
        if input_source is None:
            return {}

        # If it's already a dict, return as-is
        if isinstance(input_source, dict):
            return input_source

        # If it's a string, try to parse as JSON or treat as file path
        if isinstance(input_source, str):
            # First try to parse as JSON
            try:
                return safe_json_loads(input_source)
            except ValidationError:
                # If JSON parsing fails, treat as file path
                return self._load_from_file(input_source)

        # For other types, try to convert to dict
        try:
            if hasattr(input_source, '__dict__'):
                return input_source.__dict__
            else:
                return {"value": input_source}
        except Exception as e:
            raise ValidationError(f"Cannot process input data: {e}")

    async def handle_stdin_input(self) -> Dict[str, Any]:
        """Handle input data from stdin."""
        try:
            self.logger.debug("Reading input from stdin")

            # Read all data from stdin
            stdin_data = sys.stdin.read().strip()

            if not stdin_data:
                return {}

            # Try to parse as JSON first
            try:
                return safe_json_loads(stdin_data)
            except ValidationError:
                # If not JSON, return as text
                return {"text": stdin_data}

        except Exception as e:
            raise ValidationError(f"Failed to read from stdin: {e}")

    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load input data from file."""
        try:
            # Sanitize file path
            safe_path = sanitize_file_path(file_path)

            self.logger.debug(f"Loading input from file: {safe_path}")

            with open(safe_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if not content:
                return {}

            # Try to parse as JSON first
            try:
                return safe_json_loads(content)
            except ValidationError:
                # If not JSON, return as text
                return {"text": content}

        except FileNotFoundError:
            raise ValidationError(f"Input file not found: {file_path}")
        except PermissionError:
            raise ValidationError(f"Permission denied reading file: {file_path}")
        except Exception as e:
            raise ValidationError(f"Failed to load file {file_path}: {e}")

    async def validate_tool_parameters(self, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Validate tool arguments against schema."""
        try:
            # Get tool schema
            tools = await self.client.list_tools()
            tool_schema = None

            for tool in tools:
                if tool.get("name") == tool_name:
                    tool_schema = tool.get("inputSchema", {})
                    break

            if not tool_schema:
                self.logger.warning(f"No schema found for tool: {tool_name}")
                return

            # Basic validation - check required parameters
            required_params = tool_schema.get("required", [])
            for param in required_params:
                if param not in arguments:
                    raise ValidationError(f"Missing required parameter: {param}")

            # Type validation could be added here
            self.logger.debug(f"Tool parameters validated for: {tool_name}")

        except Exception as e:
            self.logger.warning(f"Parameter validation failed for {tool_name}: {e}")
            # Don't fail execution for validation errors, just warn

    async def _validate_tool_exists(self, tool_name: str) -> None:
        """Validate that a tool exists."""
        try:
            tools = await self.client.list_tools()
            tool_names = [tool.get("name") for tool in tools]

            if tool_name not in tool_names:
                available = ", ".join(tool_names) if tool_names else "none"
                raise ValidationError(f"Tool '{tool_name}' not found. Available tools: {available}")

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self.logger.warning(f"Could not validate tool existence: {e}")

    async def _validate_resource_exists(self, resource_uri: str) -> None:
        """Validate that a resource exists."""
        try:
            resources = await self.client.list_resources()
            resource_uris = [resource.get("uri") for resource in resources]

            if resource_uri not in resource_uris:
                available = ", ".join(resource_uris) if resource_uris else "none"
                raise ValidationError(f"Resource '{resource_uri}' not found. Available resources: {available}")

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self.logger.warning(f"Could not validate resource existence: {e}")

    async def _validate_prompt_exists(self, prompt_name: str) -> None:
        """Validate that a prompt exists."""
        try:
            prompts = await self.client.list_prompts()
            prompt_names = [prompt.get("name") for prompt in prompts]

            if prompt_name not in prompt_names:
                available = ", ".join(prompt_names) if prompt_names else "none"
                raise ValidationError(f"Prompt '{prompt_name}' not found. Available prompts: {available}")

        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            self.logger.warning(f"Could not validate prompt existence: {e}")

    async def list_available_tools(self) -> Dict[str, Any]:
        """Get list of available tools for reference."""
        try:
            tools = await self.client.list_tools()
            return {
                "tools": [{"name": tool.get("name"), "description": tool.get("description", "")}
                         for tool in tools],
                "count": len(tools)
            }
        except Exception as e:
            self.logger.error(f"Failed to list available tools: {e}")
            return {"tools": [], "count": 0, "error": str(e)}

    async def list_available_resources(self) -> Dict[str, Any]:
        """Get list of available resources for reference."""
        try:
            resources = await self.client.list_resources()
            return {
                "resources": [{"uri": resource.get("uri"), "name": resource.get("name", "")}
                             for resource in resources],
                "count": len(resources)
            }
        except Exception as e:
            self.logger.error(f"Failed to list available resources: {e}")
            return {"resources": [], "count": 0, "error": str(e)}

    async def list_available_prompts(self) -> Dict[str, Any]:
        """Get list of available prompts for reference."""
        try:
            prompts = await self.client.list_prompts()
            return {
                "prompts": [{"name": prompt.get("name"), "description": prompt.get("description", "")}
                           for prompt in prompts],
                "count": len(prompts)
            }
        except Exception as e:
            self.logger.error(f"Failed to list available prompts: {e}")
            return {"prompts": [], "count": 0, "error": str(e)}