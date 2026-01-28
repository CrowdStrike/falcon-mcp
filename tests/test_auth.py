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
    app = Starlette(routes=[Route("/", homepage)])
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
