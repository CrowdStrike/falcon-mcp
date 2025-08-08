"""
Falcon API Client for MCP Server

This module provides the Falcon API client and authentication utilities for the Falcon MCP server.
"""

import os
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any, Dict, Optional

# Import the APIHarnessV2 from FalconPy
from falconpy import APIHarnessV2

from falcon_mcp.common.logging import get_logger

logger = get_logger(__name__)


class FalconClient:
    """Client for interacting with the CrowdStrike Falcon API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        debug: bool = False,
        user_agent_comment: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """Initialize the Falcon client.

        Args:
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var)
            debug: Enable debug logging
            user_agent_comment: Additional information to include in the User-Agent comment section
        """
        # Get credentials from environment variables
        self.client_id = client_id or os.environ.get("FALCON_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.environ.get(
            "FALCON_BASE_URL", "https://api.crowdstrike.com"
        )
        self.debug = debug
        self.user_agent_comment = user_agent_comment or os.environ.get(
            "FALCON_MCP_USER_AGENT_COMMENT"
        )

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
            debug=debug,
            user_agent=self.get_user_agent(),
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

    def get_user_agent(self) -> str:
        """Get RFC-compliant user agent string for API requests.

        Returns:
            str: User agent string in RFC format "falcon-mcp/VERSION (comment; falconpy/VERSION; Python/VERSION; Platform/VERSION)"
        """
        # Get falcon-mcp version
        falcon_mcp_version = get_version()

        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Get platform information
        platform_info = f"{platform.system()}/{platform.release()}"

        # Get FalconPy version
        try:
            falconpy_version = version("crowdstrike-falconpy")
        except PackageNotFoundError:
            falconpy_version = "unknown"
            logger.debug("crowdstrike-falconpy package version not found")

        # Build comment section components (RFC-compliant format)
        comment_parts = []
        if self.user_agent_comment:
            comment_parts.append(self.user_agent_comment.strip())
        comment_parts.extend(
            [f"falconpy/{falconpy_version}", f"Python/{python_version}", platform_info]
        )

        return f"falcon-mcp/{falcon_mcp_version} ({'; '.join(comment_parts)})"

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        This method returns the authentication headers from the underlying Falcon API client,
        which can be used for custom HTTP requests or advanced integration scenarios.

        Returns:
            Dict[str, str]: Authentication headers including the bearer token
        """
        return self.client.auth_headers


def get_version() -> str:
    """Get falcon-mcp version with multiple fallback methods.

    This function tries multiple methods to determine the version:
    1. importlib.metadata (works when package is properly installed)
    2. pyproject.toml (works in development/Docker environments)
    3. Hardcoded fallback

    Returns:
        str: The version string
    """
    # Try importlib.metadata first (works when properly installed)
    try:
        return version("falcon-mcp")
    except PackageNotFoundError:
        logger.debug(
            "falcon-mcp package not found via importlib.metadata, trying pyproject.toml"
        )

    # Try reading from pyproject.toml (works in development/Docker)
    try:
        import pathlib
        import tomllib  # Python 3.11+

        # Look for pyproject.toml in current directory and parent directories
        current_path = pathlib.Path(__file__).parent
        for _ in range(3):  # Check up to 3 levels up
            pyproject_path = current_path / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    version_str = data["project"]["version"]
                    logger.debug(
                        "Found version %s in pyproject.toml at %s",
                        version_str,
                        pyproject_path,
                    )
                    return version_str
            current_path = current_path.parent

        logger.debug("pyproject.toml not found in current or parent directories")
    except (KeyError, ImportError, OSError, TypeError) as e:
        logger.debug("Failed to read version from pyproject.toml: %s", e)

    # Final fallback
    fallback_version = "0.1.0"
    logger.debug("Using fallback version: %s", fallback_version)
    return fallback_version
