"""Abstract base formatter for output formatting."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ToolInfo:
    """Information about an MCP tool."""
    name: str
    description: str = ""
    parameters: Dict[str, Any] = None
    schema: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.schema is None:
            self.schema = {}


@dataclass
class ResourceInfo:
    """Information about an MCP resource."""
    uri: str
    name: str = ""
    description: str = ""
    mime_type: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PromptInfo:
    """Information about an MCP prompt."""
    name: str
    description: str = ""
    parameters: Dict[str, Any] = None
    schema: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.schema is None:
            self.schema = {}


@dataclass
class DiscoveryResult:
    """Result of endpoint discovery."""
    server_info: Dict[str, Any]
    tools: List[ToolInfo]
    resources: List[ResourceInfo]
    prompts: List[PromptInfo]
    capabilities: Dict[str, Any]
    verbosity_level: int = 0
    version_info: Optional[Dict[str, Any]] = None
    tool_exploration: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not isinstance(self.tools, list):
            self.tools = []
        if not isinstance(self.resources, list):
            self.resources = []
        if not isinstance(self.prompts, list):
            self.prompts = []


class BaseFormatter(ABC):
    """Abstract base for output formatters."""

    def __init__(self):
        pass

    @abstractmethod
    def format_discovery_result(self, result: DiscoveryResult) -> str:
        """Format discovery results for output."""
        pass

    @abstractmethod
    def format_tool_result(self, result: Dict[str, Any]) -> str:
        """Format tool execution results."""
        pass

    @abstractmethod
    def format_resource_result(self, result: Dict[str, Any]) -> str:
        """Format resource read results."""
        pass

    @abstractmethod
    def format_error(self, error: Exception) -> str:
        """Format error messages."""
        pass

    def format_server_info(self, server_info: Dict[str, Any]) -> str:
        """Format server information."""
        return self.format_dict(server_info)

    def format_dict(self, data: Dict[str, Any]) -> str:
        """Format a dictionary for display."""
        # Default implementation - subclasses should override
        return str(data)

    def format_list(self, data: List[Any]) -> str:
        """Format a list for display."""
        # Default implementation - subclasses should override
        return str(data)

    def truncate_text(self, text: str, max_length: int = 100) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def format_parameter_info(self, params: Dict[str, Any], verbosity: int = 0) -> str:
        """Format parameter information based on verbosity level."""
        if verbosity == 0:
            # Just parameter names
            return ", ".join(params.keys()) if params else "None"
        elif verbosity == 1:
            # Parameter names and types
            result = []
            for name, info in params.items():
                param_type = info.get('type', 'unknown') if isinstance(info, dict) else 'unknown'
                result.append(f"{name}: {param_type}")
            return ", ".join(result) if result else "None"
        else:
            # Full parameter details
            return self.format_dict(params)