"""
Falcon API Client for MCP Server

This module provides the Falcon API client and authentication utilities for the Falcon MCP server.
"""
import os
from typing import Dict, Optional, Any

# Import the APIHarnessV2 from FalconPy
from falconpy import APIHarnessV2

from .common.logging import get_logger

logger = get_logger(__name__)


class FalconClient:
    """Client for interacting with the CrowdStrike Falcon API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
    ):
        """Initialize the Falcon client.

        Args:
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var)
            debug: Enable debug logging
        """
        # Get credentials from environment variables
        self.client_id = os.environ.get("FALCON_CLIENT_ID")
        self.client_secret = os.environ.get("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.environ.get("FALCON_BASE_URL", "https://api.crowdstrike.com")
        self.debug = debug

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Falcon API credentials not provided. Set FALCON_CLIENT_ID and "
                "FALCON_CLIENT_SECRET environment variables."
            )

        # Initialize the Falcon API client using APIHarnessV2
        self.client = APIHarnessV2(
            client_id=self.client_id,
            client_secret=self.client_secret,
            base_url=self.base_url,
            debug=debug
        )

        logger.debug("Initialized Falcon client with base URL: %s", self.base_url)

    def authenticate(self) -> bool:
        """Authenticate with the Falcon API.

        Returns:
            bool: True if authentication was successful
        """
        return self.client.login()

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated.

        Returns:
            bool: True if the client is authenticated
        """
        return self.client.token_valid

    def command(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute a Falcon API command.

        Args:
            operation: The API operation to execute
            **kwargs: Additional arguments to pass to the API

        Returns:
            Dict[str, Any]: The API response
        """
        return self.client.command(operation, **kwargs)

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        This method returns the authentication headers from the underlying Falcon API client,
        which can be used for custom HTTP requests or advanced integration scenarios.

        Returns:
            Dict[str, str]: Authentication headers including the bearer token
        """
        return self.client.auth_headers
