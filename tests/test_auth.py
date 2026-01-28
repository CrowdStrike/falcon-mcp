"""
Tests for the API key authentication middleware.
"""

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from falcon_mcp.common.auth import auth_middleware


def homepage(request):
    """Simple test endpoint."""
    return JSONResponse({"status": "ok"})


@pytest.fixture
def app_with_auth():
    """Create a test app with API key authentication."""
    app = Starlette(routes=[Route("/", homepage, methods=["GET", "POST", "PUT", "DELETE"])])
    return auth_middleware(app, api_key="test-secret-key")


@pytest.fixture
def client(app_with_auth):
    """Create a test client for the authenticated app."""
    return TestClient(app_with_auth)


class TestAPIKeyAuthMiddleware:
    """Test cases for the API key authentication middleware."""

    def test_returns_401_without_api_key(self, client):
        """Test middleware returns 401 when x-api-key header is missing."""
        response = client.get("/")
        assert response.status_code == 401
        assert response.json() == {"error": "Unauthorized"}

    def test_returns_401_with_wrong_api_key(self, client):
        """Test middleware returns 401 when x-api-key header has wrong value."""
        response = client.get("/", headers={"x-api-key": "wrong-key"})
        assert response.status_code == 401
        assert response.json() == {"error": "Unauthorized"}

    def test_passes_through_with_correct_api_key(self, client):
        """Test middleware allows request when x-api-key header is correct."""
        response = client.get("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_returns_401_with_empty_api_key(self, client):
        """Test middleware returns 401 when x-api-key header is empty."""
        response = client.get("/", headers={"x-api-key": ""})
        assert response.status_code == 401
        assert response.json() == {"error": "Unauthorized"}


class TestAPIKeyHeaderCaseSensitivity:
    """Test that HTTP headers are handled case-insensitively."""

    def test_lowercase_header_works(self, client):
        """Test that lowercase x-api-key header works."""
        response = client.get("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200

    def test_uppercase_header_works(self, client):
        """Test that uppercase X-API-KEY header works."""
        response = client.get("/", headers={"X-API-KEY": "test-secret-key"})
        assert response.status_code == 200

    def test_mixed_case_header_works(self, client):
        """Test that mixed case X-Api-Key header works."""
        response = client.get("/", headers={"X-Api-Key": "test-secret-key"})
        assert response.status_code == 200


class TestAPIKeyEdgeCases:
    """Test edge cases for API key validation."""

    def test_api_key_with_leading_whitespace_fails(self, client):
        """Test that API key with leading whitespace is rejected."""
        response = client.get("/", headers={"x-api-key": " test-secret-key"})
        assert response.status_code == 401

    def test_api_key_with_trailing_whitespace_fails(self, client):
        """Test that API key with trailing whitespace is rejected."""
        response = client.get("/", headers={"x-api-key": "test-secret-key "})
        assert response.status_code == 401

    def test_api_key_with_surrounding_whitespace_fails(self, client):
        """Test that API key with surrounding whitespace is rejected."""
        response = client.get("/", headers={"x-api-key": " test-secret-key "})
        assert response.status_code == 401

    def test_very_long_api_key_is_rejected(self, client):
        """Test that very long API keys (10KB+) are properly rejected."""
        long_key = "x" * 10240  # 10KB
        response = client.get("/", headers={"x-api-key": long_key})
        assert response.status_code == 401

    def test_api_key_with_null_byte_fails(self, client):
        """Test that API key with null byte is rejected."""
        response = client.get("/", headers={"x-api-key": "test\x00secret-key"})
        assert response.status_code == 401


class TestHTTPMethodCoverage:
    """Test that authentication applies to all HTTP methods."""

    def test_get_requires_auth(self, client):
        """Test GET requests require authentication."""
        response = client.get("/")
        assert response.status_code == 401

        response = client.get("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200

    def test_post_requires_auth(self, client):
        """Test POST requests require authentication."""
        response = client.post("/")
        assert response.status_code == 401

        response = client.post("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200

    def test_put_requires_auth(self, client):
        """Test PUT requests require authentication."""
        response = client.put("/")
        assert response.status_code == 401

        response = client.put("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200

    def test_delete_requires_auth(self, client):
        """Test DELETE requests require authentication."""
        response = client.delete("/")
        assert response.status_code == 401

        response = client.delete("/", headers={"x-api-key": "test-secret-key"})
        assert response.status_code == 200

    def test_options_requires_auth(self, app_with_auth):
        """Test OPTIONS requests require authentication."""
        # Need a fresh client with raise_server_exceptions=False for OPTIONS
        client = TestClient(app_with_auth, raise_server_exceptions=False)
        response = client.options("/")
        assert response.status_code == 401

        response = client.options("/", headers={"x-api-key": "test-secret-key"})
        # OPTIONS may return 405 if not explicitly handled, but auth should pass
        assert response.status_code != 401
