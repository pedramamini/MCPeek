"""JSON output formatting."""

import json
from typing import Dict, Any

from .base import BaseFormatter, DiscoveryResult
from ..utils.helpers import safe_json_dumps, extract_error_details


class JSONFormatter(BaseFormatter):
    """JSON output formatting."""

    def __init__(self, pretty_print: bool = True):
        """Initialize JSON formatter with pretty-print option."""
        super().__init__()
        self.pretty_print = pretty_print

    def format_discovery_result(self, result: DiscoveryResult) -> str:
        """Format discovery results as pretty-printed JSON."""
        output = {
            "server_info": result.server_info,
            "capabilities": result.capabilities,
            "tools": [self._tool_to_dict(tool) for tool in result.tools],
            "resources": [self._resource_to_dict(resource) for resource in result.resources],
            "prompts": [self._prompt_to_dict(prompt) for prompt in result.prompts],
            "summary": {
                "total_tools": len(result.tools),
                "total_resources": len(result.resources),
                "total_prompts": len(result.prompts),
                "verbosity_level": result.verbosity_level
            }
        }
        
        # Include version information if available
        if result.version_info:
            output["version_info"] = result.version_info

        return self._format_json(output)

    def format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool execution results as JSON."""
        return self._format_json(result)

    def format_resource_result(self, result: Dict[str, Any]) -> str:
        """Format resource read results as JSON."""
        return self._format_json(result)

    def format_error(self, error: Exception) -> str:
        """Format error messages as JSON."""
        error_data = {
            "error": extract_error_details(error),
            "success": False
        }
        return self._format_json(error_data)

    def format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary as JSON."""
        return self._format_json(data)

    def format_list(self, data: list) -> str:
        """Format a list as JSON."""
        return self._format_json(data)

    def _format_json(self, data: Any) -> str:
        """Format data as JSON with proper indentation."""
        if self.pretty_print:
            return safe_json_dumps(data, pretty=True)
        else:
            return safe_json_dumps(data, pretty=False)

    def _tool_to_dict(self, tool) -> Dict[str, Any]:
        """Convert ToolInfo to dictionary."""
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "schema": tool.schema
        }

    def _resource_to_dict(self, resource) -> Dict[str, Any]:
        """Convert ResourceInfo to dictionary."""
        return {
            "uri": resource.uri,
            "name": resource.name,
            "description": resource.description,
            "mime_type": resource.mime_type,
            "metadata": resource.metadata
        }

    def _prompt_to_dict(self, prompt) -> Dict[str, Any]:
        """Convert PromptInfo to dictionary."""
        return {
            "name": prompt.name,
            "description": prompt.description,
            "parameters": prompt.parameters,
            "schema": prompt.schema
        }