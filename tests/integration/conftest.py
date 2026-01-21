"""Pytest fixtures for integration tests."""

import os

import pytest
from dotenv import load_dotenv

from falcon_mcp.client import FalconClient

# Load environment variables from .env file for local development
load_dotenv()


@pytest.fixture(scope="session")
def falcon_client():
    """
    Create a real FalconClient for integration tests.

    This fixture requires FALCON_CLIENT_ID and FALCON_CLIENT_SECRET environment
    variables to be set. Tests will be skipped if credentials are not available.
    """
    client_id = os.environ.get("FALCON_CLIENT_ID")
    client_secret = os.environ.get("FALCON_CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip(
            "Integration tests require FALCON_CLIENT_ID and FALCON_CLIENT_SECRET "
            "environment variables. Set these in your .env file or environment."
        )

    client = FalconClient()

    if not client.authenticate():
        pytest.skip(
            "Failed to authenticate with Falcon API. Check your credentials "
            "and ensure they have the required API scopes."
        )

    return client
