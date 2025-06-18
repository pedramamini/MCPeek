"""Discovery engine for MCP endpoint capabilities."""

import asyncio
import re
from typing import List, Dict, Any

from .mcp_client import MCPClient
from .formatters.base import DiscoveryResult, ToolInfo, ResourceInfo, PromptInfo
from .utils.logging import get_logger
from .utils.helpers import validate_verbosity_level


class DiscoveryEngine:
    """Discovers and catalogs MCP endpoint capabilities."""
    
    # Default regex pattern for safe tools to tickle
    SAFE_TOOL_PATTERN = re.compile(r".*(list|status|help).*", re.IGNORECASE)

    def __init__(self, client: MCPClient, verbosity: int = 0, tool_tickle: bool = False):
        """Initialize discovery engine with client, verbosity level, and tool exploration option."""
        self.client = client
        self.verbosity = validate_verbosity_level(verbosity)
        self.tool_tickle = tool_tickle
        self.logger = get_logger()

    async def discover_endpoint(self) -> DiscoveryResult:
        """Perform complete endpoint discovery."""
        self.logger.info(f"Starting endpoint discovery (verbosity: {self.verbosity})")

        try:
            # Get server info and capabilities
            server_info = await self.get_server_info()

            # Discover all capabilities concurrently
            tools_task = asyncio.create_task(self.catalog_tools())
            resources_task = asyncio.create_task(self.catalog_resources())
            prompts_task = asyncio.create_task(self.catalog_prompts())

            # Wait for all discovery tasks to complete
            tools, resources, prompts = await asyncio.gather(
                tools_task, resources_task, prompts_task,
                return_exceptions=True
            )

            # Handle any exceptions from discovery tasks
            if isinstance(tools, Exception):
                self.logger.warning(f"Failed to discover tools: {tools}")
                tools = []

            if isinstance(resources, Exception):
                self.logger.warning(f"Failed to discover resources: {resources}")
                resources = []

            if isinstance(prompts, Exception):
                self.logger.warning(f"Failed to discover prompts: {prompts}")
                prompts = []
            
            # Perform tool exploration if enabled
            tool_exploration_results = None
            if self.tool_tickle and tools and not isinstance(tools, Exception):
                try:
                    from typing import cast
                    safe_tools = cast(List[ToolInfo], tools)
                    tool_exploration_results = await self.explore_tools(safe_tools)
                except Exception as e:
                    self.logger.warning(f"Tool exploration failed: {e}")
                    tool_exploration_results = {"error": str(e)}

            # Update server capabilities based on actual discovery results
            # Only build capabilities from successful discoveries (not exceptions)
            discovered_capabilities = {}

            # Convert results to proper types, handling exceptions
            from typing import cast
            final_tools = cast(List[ToolInfo], tools) if not isinstance(tools, Exception) else []
            final_resources = cast(List[ResourceInfo], resources) if not isinstance(resources, Exception) else []
            final_prompts = cast(List[PromptInfo], prompts) if not isinstance(prompts, Exception) else []

            discovered_capabilities['tools'] = {tool.name: {'description': tool.description} for tool in final_tools} if final_tools else {}
            discovered_capabilities['resources'] = {resource.uri: {'name': resource.name, 'description': resource.description} for resource in final_resources} if final_resources else {}
            discovered_capabilities['prompts'] = {prompt.name: {'description': prompt.description} for prompt in final_prompts} if final_prompts else {}

            # Get version information from client
            try:
                version_info = self.client.get_server_version_summary()
            except Exception as e:
                self.logger.warning(f"Failed to get version information: {e}")
                version_info = {"status": "detection_failed", "error": str(e)}

            # Create discovery result with discovered capabilities
            result = DiscoveryResult(
                server_info=server_info,
                tools=final_tools,
                resources=final_resources,
                prompts=final_prompts,
                capabilities=discovered_capabilities,
                verbosity_level=self.verbosity,
                version_info=version_info,
                tool_exploration=tool_exploration_results
            )

            self.logger.info(f"Discovery complete: {len(final_tools)} tools, {len(final_resources)} resources, {len(final_prompts)} prompts")
            return result

        except Exception as e:
            self.logger.error(f"Discovery failed: {e}")
            raise

    async def get_server_info(self) -> Dict[str, Any]:
        """Get basic server information and capabilities."""
        try:
            server_info = await self.client.get_server_info()
            self.logger.debug("Retrieved server information")
            return server_info
        except Exception as e:
            self.logger.warning(f"Failed to get server info: {e}")
            return {}

    async def catalog_tools(self) -> List[ToolInfo]:
        """Catalog all available tools with appropriate detail level."""
        try:
            tools_data = await self.client.list_tools()
            tools = []

            for tool_data in tools_data:
                tool_info = self._process_tool_data(tool_data)
                tools.append(tool_info)

            # DEBUG: Compare discovered tools vs capabilities
            server_capabilities = self.client.server_capabilities
            tools_capability = server_capabilities.get('tools', {})
            self.logger.debug(f"Cataloged {len(tools)} tools via list_tools()")
            self.logger.debug(f"Server capabilities show tools: {tools_capability}")
            self.logger.debug(f"Tool names discovered: {[tool.name for tool in tools]}")

            return tools

        except Exception as e:
            self.logger.error(f"Failed to catalog tools: {e}")
            return []

    async def catalog_resources(self) -> List[ResourceInfo]:
        """Catalog all available resources with appropriate detail level."""
        try:
            resources_data = await self.client.list_resources()
            resources = []

            for resource_data in resources_data:
                resource_info = self._process_resource_data(resource_data)
                resources.append(resource_info)

            # DEBUG: Compare discovered resources vs capabilities
            server_capabilities = self.client.server_capabilities
            resources_capability = server_capabilities.get('resources', {})
            self.logger.debug(f"Cataloged {len(resources)} resources via list_resources()")
            self.logger.debug(f"Server capabilities show resources: {resources_capability}")
            self.logger.debug(f"Resource URIs discovered: {[resource.uri for resource in resources]}")

            return resources

        except Exception as e:
            self.logger.error(f"Failed to catalog resources: {e}")
            return []

    async def catalog_prompts(self) -> List[PromptInfo]:
        """Catalog all available prompts with appropriate detail level."""
        try:
            prompts_data = await self.client.list_prompts()
            prompts = []

            for prompt_data in prompts_data:
                prompt_info = self._process_prompt_data(prompt_data)
                prompts.append(prompt_info)

            self.logger.debug(f"Cataloged {len(prompts)} prompts")
            return prompts

        except Exception as e:
            self.logger.error(f"Failed to catalog prompts: {e}")
            return []

    def _process_tool_data(self, tool_data: Dict[str, Any]) -> ToolInfo:
        """Process raw tool data into ToolInfo based on verbosity."""
        name = tool_data.get("name", "unknown")
        description = tool_data.get("description", "")

        # Extract parameters and schema based on verbosity level
        input_schema = tool_data.get("inputSchema", {})
        parameters = {}
        schema = {}

        if self.verbosity >= 1:
            # Include parameter information
            if "properties" in input_schema:
                parameters = input_schema["properties"]

        if self.verbosity >= 3:
            # Include full schema
            schema = input_schema

        return ToolInfo(
            name=name,
            description=description,
            parameters=parameters,
            schema=schema
        )

    def _process_resource_data(self, resource_data: Dict[str, Any]) -> ResourceInfo:
        """Process raw resource data into ResourceInfo based on verbosity."""
        uri = resource_data.get("uri", "")
        name = resource_data.get("name", "")
        description = resource_data.get("description", "")
        mime_type = resource_data.get("mimeType", "")

        metadata = {}
        if self.verbosity >= 3:
            # Include all metadata at highest verbosity
            metadata = {k: v for k, v in resource_data.items()
                       if k not in ["uri", "name", "description", "mimeType"]}

        return ResourceInfo(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type,
            metadata=metadata
        )

    def _process_prompt_data(self, prompt_data: Dict[str, Any]) -> PromptInfo:
        """Process raw prompt data into PromptInfo based on verbosity."""
        name = prompt_data.get("name", "unknown")
        description = prompt_data.get("description", "")

        # Extract parameters and schema based on verbosity level
        arguments_schema = prompt_data.get("arguments", {})
        parameters = {}
        schema = {}

        if self.verbosity >= 1:
            # Include parameter information
            if isinstance(arguments_schema, list):
                # Convert list format to dict
                parameters = {arg.get("name", f"arg_{i}"): arg
                            for i, arg in enumerate(arguments_schema)}
            elif isinstance(arguments_schema, dict) and "properties" in arguments_schema:
                parameters = arguments_schema["properties"]

        if self.verbosity >= 3:
            # Include full schema
            schema = arguments_schema

        return PromptInfo(
            name=name,
            description=description,
            parameters=parameters,
            schema=schema
        )

    def generate_discovery_report(self, discovery_result: DiscoveryResult) -> str:
        """Generate formatted discovery report."""
        lines = []

        # Header
        lines.append("=== MCP Endpoint Discovery Report ===")
        lines.append("")

        # Server Info
        if discovery_result.server_info:
            lines.append("Server Information:")
            for key, value in discovery_result.server_info.items():
                lines.append(f"  {key}: {value}")
            lines.append("")

        # Summary
        lines.append("Summary:")
        lines.append(f"  Tools: {len(discovery_result.tools)}")
        lines.append(f"  Resources: {len(discovery_result.resources)}")
        lines.append(f"  Prompts: {len(discovery_result.prompts)}")
        lines.append(f"  Verbosity Level: {discovery_result.verbosity_level}")
        lines.append("")

        # Tools
        if discovery_result.tools:
            lines.append("Available Tools:")
            for tool in discovery_result.tools:
                lines.append(f"  - {tool.name}")
                if self.verbosity >= 1 and tool.description:
                    lines.append(f"    Description: {tool.description}")
                if self.verbosity >= 2 and tool.parameters:
                    param_names = ", ".join(tool.parameters.keys())
                    lines.append(f"    Parameters: {param_names}")
            lines.append("")

        # Resources
        if discovery_result.resources:
            lines.append("Available Resources:")
            for resource in discovery_result.resources:
                lines.append(f"  - {resource.uri}")
                if self.verbosity >= 1:
                    if resource.name:
                        lines.append(f"    Name: {resource.name}")
                    if resource.description:
                        lines.append(f"    Description: {resource.description}")
                if self.verbosity >= 2 and resource.mime_type:
                    lines.append(f"    MIME Type: {resource.mime_type}")
            lines.append("")

        # Prompts
        if discovery_result.prompts:
            lines.append("Available Prompts:")
            for prompt in discovery_result.prompts:
                lines.append(f"  - {prompt.name}")
                if self.verbosity >= 1 and prompt.description:
                    lines.append(f"    Description: {prompt.description}")
                if self.verbosity >= 2 and prompt.parameters:
                    param_names = ", ".join(prompt.parameters.keys())
                    lines.append(f"    Parameters: {param_names}")
            lines.append("")

        return "\n".join(lines)

    async def explore_tools(self, tools: List[ToolInfo]) -> Dict[str, Any]:
        """Explore tools by actually calling safe ones."""
        if not self.tool_tickle or not tools:
            return {}
        
        self.logger.info(f"Starting tool exploration with {len(tools)} tools")
        exploration_results = {}
        
        # Filter tools that match the safe pattern
        safe_tools = self.filter_safe_tools(tools)
        self.logger.info(f"Found {len(safe_tools)} safe tools to explore: {[tool.name for tool in safe_tools]}")
        
        # Execute safe tools in parallel with error handling
        exploration_tasks = []
        for tool in safe_tools:
            task = asyncio.create_task(self._explore_single_tool(tool))
            exploration_tasks.append(task)
        
        # Wait for all explorations to complete
        results = await asyncio.gather(*exploration_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        for i, result in enumerate(results):
            tool_name = safe_tools[i].name
            if isinstance(result, Exception):
                self.logger.warning(f"Failed to explore tool {tool_name}: {result}")
                exploration_results[tool_name] = {
                    "status": "error",
                    "error": str(result)
                }
            else:
                exploration_results[tool_name] = result
        
        self.logger.info(f"Tool exploration complete: explored {len(exploration_results)} tools")
        return exploration_results
    
    def filter_safe_tools(self, tools: List[ToolInfo]) -> List[ToolInfo]:
        """Filter tools that match the safe pattern."""
        safe_tools = []
        for tool in tools:
            if self.SAFE_TOOL_PATTERN.match(tool.name):
                safe_tools.append(tool)
                self.logger.debug(f"Tool {tool.name} matches safe pattern")
            else:
                self.logger.debug(f"Tool {tool.name} does not match safe pattern")
        
        return safe_tools
    
    async def _explore_single_tool(self, tool: ToolInfo) -> Dict[str, Any]:
        """Explore a single tool by calling it with minimal/no parameters."""
        try:
            self.logger.debug(f"Exploring tool: {tool.name}")
            
            # Try to call the tool with no parameters first
            # Most list/status/help tools should work without parameters
            try:
                result = await self.client.call_tool(tool.name, {})
                return {
                    "status": "success",
                    "result": result,
                    "called_with": {}
                }
            except Exception as e:
                # If calling with no parameters fails, we could try to analyze
                # the tool schema and provide minimal required parameters
                # For now, just report the failure
                self.logger.debug(f"Tool {tool.name} failed with empty parameters: {e}")
                return {
                    "status": "failed_empty_params",
                    "error": str(e),
                    "called_with": {}
                }
                
        except Exception as e:
            self.logger.error(f"Unexpected error exploring tool {tool.name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }