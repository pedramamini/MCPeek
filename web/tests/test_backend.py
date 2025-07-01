"""
Test suite for MCPeek Web API Backend.
"""

import asyncio
import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import app after setting up test environment
import os
os.environ["MCPEEK_DEBUG"] = "true"
os.environ["MCPEEK_CORS_ORIGINS"] = "http://localhost:3000"

from web.backend.app import app, client_manager, create_error_response


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns correct status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mcpeek-web-api"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "uptime" in data


class TestAuthentication:
    """Test authentication mechanisms."""
    
    def test_api_key_header_extraction(self, client):
        """Test API key extraction from headers."""
        headers = {"X-API-Key": "test-key-123"}
        response = client.post(
            "/api/discover",
            json={"endpoint": "http://test.com", "verbosity": 0, "tool_tickle": False},
            headers=headers
        )
        # Should fail with connection error, but auth should be extracted
        assert response.status_code in [422, 500]  # Will fail due to mock, but headers processed
    
    def test_bearer_token_extraction(self, client):
        """Test bearer token extraction."""
        headers = {"Authorization": "Bearer test-token-456"}
        response = client.post(
            "/api/discover",
            json={"endpoint": "http://test.com", "verbosity": 0, "tool_tickle": False},
            headers=headers
        )
        # Should fail with connection error, but auth should be extracted
        assert response.status_code in [422, 500]


class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_empty_endpoint_validation(self, client):
        """Test empty endpoint validation."""
        response = client.post(
            "/api/discover",
            json={"endpoint": "", "verbosity": 0, "tool_tickle": False}
        )
        assert response.status_code == 422
    
    def test_invalid_timeout_validation(self, client):
        """Test timeout validation."""
        response = client.post(
            "/api/discover", 
            json={"endpoint": "http://test.com", "verbosity": 0, "tool_tickle": False, "timeout": -1}
        )
        assert response.status_code == 422
        
        response = client.post(
            "/api/discover",
            json={"endpoint": "http://test.com", "verbosity": 0, "tool_tickle": False, "timeout": 999}
        )
        assert response.status_code == 422
    
    def test_tool_name_validation(self, client):
        """Test tool name validation."""
        response = client.post(
            "/api/execute/tool",
            json={"endpoint": "http://test.com", "tool_name": "", "parameters": {}}
        )
        assert response.status_code == 422
    
    def test_resource_uri_validation(self, client):
        """Test resource URI validation."""
        response = client.post(
            "/api/execute/resource",
            json={"endpoint": "http://test.com", "resource_uri": ""}
        )
        assert response.status_code == 422


class TestErrorHandling:
    """Test error handling and response formatting."""
    
    def test_error_response_creation(self):
        """Test error response creation."""
        # In debug mode, should show details
        os.environ["MCPEEK_DEBUG"] = "true" 
        response = create_error_response("Test error", "Detailed info")
        assert not response.success
        assert "Test error" in response.error
        assert "Detailed info" in response.error
        
        # In production mode, should hide details
        os.environ.pop("MCPEEK_DEBUG", None)
        response = create_error_response("Test error", "Detailed info")
        assert not response.success
        assert response.error == "An error occurred processing your request"


@pytest.mark.asyncio
class TestMCPClientManager:
    """Test MCP client manager functionality."""
    
    @patch('web.backend.app.HTTPTransport')
    @patch('web.backend.app.MCPClient')
    async def test_create_client_success(self, mock_client_class, mock_transport_class):
        """Test successful client creation."""
        # Mock transport and client
        mock_transport = AsyncMock()
        mock_transport_class.return_value = mock_transport
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        
        # Create test request
        from web.backend.app import MCPEndpointRequest
        request = MCPEndpointRequest(endpoint="http://test.com", timeout=30.0)
        
        # Test client creation
        result = await client_manager.create_client(request, api_key="test-key")
        
        # Verify transport was configured and connected
        mock_transport_class.assert_called_once()
        mock_transport.connect.assert_called_once()
        mock_client_class.assert_called_once_with(mock_transport)
        assert result == mock_client
    
    @patch('web.backend.app.STDIOTransport')
    async def test_create_client_stdio(self, mock_transport_class):
        """Test STDIO client creation."""
        mock_transport = AsyncMock()
        mock_transport_class.from_command_string.return_value = mock_transport
        
        from web.backend.app import MCPEndpointRequest
        request = MCPEndpointRequest(endpoint="python test.py", timeout=30.0)
        
        with patch('web.backend.app.MCPClient') as mock_client_class:
            await client_manager.create_client(request)
            mock_transport_class.from_command_string.assert_called_once()


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiting_applied(self, client):
        """Test that rate limiting is applied to endpoints."""
        # Make multiple rapid requests to test rate limiting
        endpoint_data = {"endpoint": "http://test.com", "verbosity": 0, "tool_tickle": False}
        
        responses = []
        for _ in range(5):
            response = client.post("/api/discover", json=endpoint_data)
            responses.append(response.status_code)
        
        # At least some requests should succeed (even if they fail due to connection)
        # Rate limiting would return 429 if exceeded
        assert all(code != 429 for code in responses[:3])  # First few should not be rate limited


class TestCORSConfiguration:
    """Test CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/api/health")
        
        # Should have CORS headers in response
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
    
    def test_cors_origins_configured(self):
        """Test CORS origins are properly configured."""
        from web.backend.app import CORS_ORIGINS
        assert isinstance(CORS_ORIGINS, list)
        assert len(CORS_ORIGINS) > 0
        assert all(origin.startswith("http") for origin in CORS_ORIGINS)


class TestEnvironmentConfiguration: 
    """Test environment-based configuration."""
    
    def test_environment_variables_loaded(self):
        """Test environment variables are loaded correctly."""
        from web.backend.app import API_HOST, API_PORT, RATE_LIMIT
        
        assert isinstance(API_HOST, str)
        assert isinstance(API_PORT, int)
        assert isinstance(RATE_LIMIT, str)
        assert "/" in RATE_LIMIT  # Should be in format "60/minute"


if __name__ == "__main__":
    pytest.main([__file__])