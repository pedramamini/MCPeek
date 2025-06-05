"""Helper utilities for MCPeek."""

import json
import os
import re
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urlparse

from .exceptions import ValidationError


def parse_endpoint_url(endpoint: str) -> Dict[str, str]:
    """Parse endpoint URL and determine transport type."""
    if endpoint.startswith(('http://', 'https://')):
        parsed = urlparse(endpoint)
        return {
            'type': 'http',
            'url': endpoint,
            'scheme': parsed.scheme,
            'host': parsed.hostname or '',
            'port': str(parsed.port) if parsed.port else '',
            'path': parsed.path
        }
    else:
        # Assume STDIO transport for non-HTTP endpoints
        return {
            'type': 'stdio',
            'command': endpoint,
            'executable': endpoint.split()[0] if ' ' in endpoint else endpoint
        }


def validate_json_rpc_message(message: Dict[str, Any]) -> None:
    """Validate JSON-RPC message structure."""
    if not isinstance(message, dict):
        raise ValidationError("Message must be a dictionary")

    # Check for required JSON-RPC fields
    if 'jsonrpc' not in message:
        raise ValidationError("Missing 'jsonrpc' field")

    if message['jsonrpc'] != '2.0':
        raise ValidationError("Invalid JSON-RPC version, must be '2.0'")

    # Check for either method (request) or result/error (response)
    if 'method' in message:
        # Request message
        if 'id' not in message:
            # Notification - id is optional
            pass
    elif 'result' in message or 'error' in message:
        # Response message
        if 'id' not in message:
            raise ValidationError("Response message missing 'id' field")
    else:
        raise ValidationError("Message must have either 'method' or 'result'/'error'")


def sanitize_file_path(file_path: str) -> str:
    """Sanitize file path for security."""
    # Remove any path traversal attempts
    sanitized = os.path.normpath(file_path)

    # Ensure we don't go above current directory
    if sanitized.startswith('..'):
        raise ValidationError(f"Invalid file path: {file_path}")

    return sanitized


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"


def safe_json_loads(data: str) -> Dict[str, Any]:
    """Safely load JSON data with error handling."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON data: {e}")


def safe_json_dumps(data: Any, pretty: bool = False) -> str:
    """Safely dump data to JSON with error handling."""
    try:
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"Cannot serialize to JSON: {e}")


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_error_details(error: Exception) -> Dict[str, Any]:
    """Extract detailed error information."""
    return {
        'type': type(error).__name__,
        'message': str(error),
        'details': getattr(error, 'details', {})
    }


def create_request_id() -> str:
    """Create a unique request ID for JSON-RPC messages."""
    return f"mcpeek-{int(time.time() * 1000)}"


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with dict2 taking precedence."""
    result = dict1.copy()
    result.update(dict2)
    return result


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_verbosity_level(level: int) -> int:
    """Validate and normalize verbosity level."""
    if level < 0:
        return 0
    elif level > 3:
        return 3
    return level