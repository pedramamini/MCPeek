"""Configuration manager for MCPeek."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import argparse

from .utils.exceptions import ValidationError
from .utils.helpers import parse_endpoint_url, merge_dicts
from .utils.logging import get_logger


@dataclass
class EndpointConfig:
    """Configuration for a specific endpoint."""
    url: str
    transport_type: str
    auth_headers: Dict[str, str]
    timeout: float = 30.0

    def __post_init__(self):
        if not self.auth_headers:
            self.auth_headers = {}


class ConfigManager:
    """Handles configuration from CLI args and environment."""

    def __init__(self):
        self.logger = get_logger()

    def load_config(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Load configuration from multiple sources."""
        # Start with default configuration
        config = self._get_default_config()

        # Load environment variables
        env_config = self._load_env_config()

        # Convert CLI args to config dict
        cli_config = self._args_to_config(args)

        # Merge configurations (CLI takes precedence)
        config = merge_dicts(config, env_config)
        config = merge_dicts(config, cli_config)

        # Validate the final configuration
        self.validate_config(config)

        self.logger.debug(f"Loaded configuration: {self._sanitize_config_for_logging(config)}")
        return config

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration completeness and correctness."""
        # Check required fields
        if not config.get('endpoint'):
            raise ValidationError("Endpoint is required")

        # Validate endpoint format
        endpoint_info = parse_endpoint_url(config['endpoint'])
        if endpoint_info['type'] == 'http':
            if not endpoint_info.get('host'):
                raise ValidationError(f"Invalid HTTP endpoint URL: {config['endpoint']}")

        # Validate verbosity level
        verbosity = config.get('verbosity', 0)
        if not isinstance(verbosity, int) or verbosity < 0 or verbosity > 3:
            raise ValidationError("Verbosity must be an integer between 0 and 3")

        # Validate timeout
        timeout = config.get('timeout', 30.0)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValidationError("Timeout must be a positive number")

        # Validate format
        output_format = config.get('format', 'table')
        if output_format not in ['json', 'table']:
            raise ValidationError("Format must be 'json' or 'table'")

        # Validate log level
        log_level = config.get('log_level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if log_level.upper() not in valid_levels:
            raise ValidationError(f"Log level must be one of: {', '.join(valid_levels)}")

    def get_endpoint_config(self, endpoint: str, auth_headers: Optional[Dict[str, str]] = None,
                           timeout: float = 30.0) -> EndpointConfig:
        """Get configuration for specific endpoint."""
        endpoint_info = parse_endpoint_url(endpoint)

        return EndpointConfig(
            url=endpoint,
            transport_type=endpoint_info['type'],
            auth_headers=auth_headers or {},
            timeout=timeout
        )

    def merge_cli_and_env_config(self, cli_args: Dict[str, Any],
                                env_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Merge CLI arguments with environment variables."""
        return merge_dicts(env_vars, cli_args)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'verbosity': 0,
            'format': 'table',
            'timeout': 30.0,
            'log_level': 'INFO',
            'discover': False,
            'tool_tickle': False,
            'stdin': False,
        }

    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}

        # Load environment variables with MCPEEK_ prefix
        env_mappings = {
            'MCPEEK_ENDPOINT': 'endpoint',
            'MCPEEK_FORMAT': 'format',
            'MCPEEK_TIMEOUT': 'timeout',
            'MCPEEK_LOG_LEVEL': 'log_level',
            'MCPEEK_API_KEY': 'api_key',
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                # Convert string values to appropriate types
                if config_key == 'timeout':
                    try:
                        config[config_key] = float(value)
                    except ValueError:
                        self.logger.warning(f"Invalid timeout value in {env_var}: {value}")
                else:
                    config[config_key] = value

        return config

    def _args_to_config(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Convert argparse Namespace to configuration dictionary."""
        config = {}

        # Map argparse attributes to config keys
        arg_mappings = {
            'endpoint': 'endpoint',
            'discover': 'discover',
            'tool_tickle': 'tool_tickle',
            'tool': 'tool',
            'resource': 'resource',
            'input': 'input',
            'stdin': 'stdin',
            'format': 'format',
            'verbosity': 'verbosity',
            'api_key': 'api_key',
            'auth_header': 'auth_header',
            'timeout': 'timeout',
            'log_level': 'log_level',
        }

        for arg_name, config_key in arg_mappings.items():
            if hasattr(args, arg_name):
                value = getattr(args, arg_name)
                if value is not None:
                    config[config_key] = value

        return config

    def _sanitize_config_for_logging(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config for logging."""
        sanitized = config.copy()

        # Remove or mask sensitive fields
        sensitive_fields = ['api_key', 'auth_header']
        for field in sensitive_fields:
            if field in sanitized and sanitized[field]:
                sanitized[field] = "***REDACTED***"

        return sanitized

    def get_transport_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract transport-specific configuration."""
        return {
            'timeout': config.get('timeout', 30.0),
            'auth_headers': self._build_auth_headers(config),
        }

    def _build_auth_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Build authentication headers from configuration."""
        headers = {}

        # This will be handled by AuthManager, but we can prepare basic structure
        if config.get('api_key'):
            headers['Authorization'] = f"Bearer {config['api_key']}"
        elif config.get('auth_header'):
            auth_header = config['auth_header']
            if not auth_header.startswith(('Bearer ', 'Basic ')):
                auth_header = f"Bearer {auth_header}"
            headers['Authorization'] = auth_header

        return headers

    def get_formatter_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract formatter-specific configuration."""
        return {
            'format': config.get('format', 'table'),
            'pretty_print': True,  # Always use pretty printing
            'use_colors': True,    # Always use colors for table format
        }

    def get_discovery_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract discovery-specific configuration."""
        return {
            'verbosity': config.get('verbosity', 0),
            'discover': config.get('discover', False),
            'tool_tickle': config.get('tool_tickle', False),
        }

    def get_execution_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract execution-specific configuration."""
        return {
            'tool': config.get('tool'),
            'resource': config.get('resource'),
            'input': config.get('input'),
            'stdin': config.get('stdin', False),
        }