"""Authentication manager for MCP endpoints."""

import os
from typing import Dict, Optional

from .utils.exceptions import AuthenticationError
from .utils.logging import get_logger


class AuthManager:
    """Handles authentication for MCP endpoints."""

    def __init__(self):
        self.logger = get_logger()

    def get_auth_headers(self, endpoint: str, api_key: Optional[str] = None,
                        auth_header: Optional[str] = None) -> Dict[str, str]:
        """Generate authentication headers for endpoint."""
        headers = {}

        # Try explicit auth header first
        if auth_header:
            if auth_header.startswith("Bearer "):
                headers["Authorization"] = auth_header
            elif auth_header.startswith("Basic "):
                headers["Authorization"] = auth_header
            else:
                # Assume it's a bearer token without prefix
                headers["Authorization"] = f"Bearer {auth_header}"
            self.logger.debug("Using explicit auth header")
            return headers

        # Try API key
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            self.logger.debug("Using API key for authentication")
            return headers

        # Try environment variables
        env_api_key = self.load_api_key("MCPEEK_API_KEY")
        if env_api_key:
            headers["Authorization"] = f"Bearer {env_api_key}"
            self.logger.debug("Using API key from environment")
            return headers

        # Try endpoint-specific environment variables
        env_key = self._get_endpoint_env_key(endpoint)
        if env_key:
            endpoint_api_key = self.load_api_key(env_key)
            if endpoint_api_key:
                headers["Authorization"] = f"Bearer {endpoint_api_key}"
                self.logger.debug(f"Using API key from {env_key}")
                return headers

        # No authentication found
        self.logger.debug("No authentication credentials found")
        return headers

    def load_api_key(self, key_name: str) -> Optional[str]:
        """Load API key from environment or CLI."""
        api_key = os.getenv(key_name)
        if api_key:
            self.logger.debug(f"Loaded API key from environment variable: {key_name}")
            return api_key.strip()
        return None

    def validate_credentials(self, endpoint: str, api_key: Optional[str] = None,
                           auth_header: Optional[str] = None) -> bool:
        """Validate that required credentials are available."""
        # For HTTP endpoints, we might need authentication
        if endpoint.startswith(('http://', 'https://')):
            headers = self.get_auth_headers(endpoint, api_key, auth_header)

            # If it's HTTPS and no auth headers, warn but don't fail
            if endpoint.startswith('https://') and not headers:
                self.logger.warning("HTTPS endpoint with no authentication - this may fail")
                return True

            return True

        # STDIO endpoints don't typically need authentication
        return True

    def _get_endpoint_env_key(self, endpoint: str) -> Optional[str]:
        """Get environment variable key for specific endpoint."""
        if not endpoint.startswith(('http://', 'https://')):
            return None

        # Extract hostname and create environment variable name
        try:
            from urllib.parse import urlparse
            parsed = urlparse(endpoint)
            hostname = parsed.hostname

            if hostname:
                # Convert hostname to environment variable format
                # e.g., api.example.com -> MCPEEK_API_EXAMPLE_COM_KEY
                env_name = hostname.replace('.', '_').replace('-', '_').upper()
                return f"MCPEEK_{env_name}_KEY"
        except Exception:
            pass

        return None

    def get_auth_info(self, endpoint: str, api_key: Optional[str] = None,
                     auth_header: Optional[str] = None) -> Dict[str, str]:
        """Get authentication information for display purposes."""
        info = {}

        if auth_header:
            if auth_header.startswith("Bearer "):
                info["type"] = "Bearer Token (explicit)"
                info["source"] = "command line"
            elif auth_header.startswith("Basic "):
                info["type"] = "Basic Auth (explicit)"
                info["source"] = "command line"
            else:
                info["type"] = "Bearer Token (explicit)"
                info["source"] = "command line"
        elif api_key:
            info["type"] = "API Key"
            info["source"] = "command line"
        elif self.load_api_key("MCPEEK_API_KEY"):
            info["type"] = "API Key"
            info["source"] = "MCPEEK_API_KEY environment variable"
        else:
            env_key = self._get_endpoint_env_key(endpoint)
            if env_key and self.load_api_key(env_key):
                info["type"] = "API Key"
                info["source"] = f"{env_key} environment variable"
            else:
                info["type"] = "None"
                info["source"] = "No authentication configured"

        return info

    def clear_cached_credentials(self) -> None:
        """Clear any cached credentials (for future use)."""
        # Currently no caching implemented, but this method provides
        # a hook for future credential caching functionality
        pass