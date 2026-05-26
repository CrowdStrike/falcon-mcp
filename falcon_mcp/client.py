"""
Falcon API Client for MCP Server

This module provides the Falcon API client and authentication utilities for the Falcon MCP server.
"""

import os
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any

# Import the APIHarnessV2 from FalconPy
from falconpy import APIHarnessV2  # type: ignore[import-untyped]

from falcon_mcp.common.logging import get_logger

logger = get_logger(__name__)


class FalconClient:
    """Client for interacting with the CrowdStrike Falcon API."""

    def __init__(
        self,
        base_url: str | None = None,
        debug: bool = False,
        user_agent_comment: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        member_cid: str | None = None,
        proxy: str | None = None,
    ):
        """Initialize the Falcon client.

        Args:
            base_url: Falcon API base URL (defaults to FALCON_BASE_URL env var)
            debug: Enable debug logging
            user_agent_comment: Additional information to include in the User-Agent comment section
            client_id: Falcon API Client ID (defaults to FALCON_CLIENT_ID env var)
            client_secret: Falcon API Client Secret (defaults to FALCON_CLIENT_SECRET env var)
            member_cid: Child CID for Flight Control (MSSP) support (defaults to FALCON_MEMBER_CID env var)
            proxy: HTTP/HTTPS proxy URL for outbound Falcon API connections (defaults to FALCON_PROXY_URL env var).
                   Example: "http://proxy.corp.example.com:8080"
        """
        # Get credentials from parameters or environment variables (parameters take precedence)
        self.client_id = client_id or os.environ.get("FALCON_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("FALCON_CLIENT_SECRET")
        self.base_url = base_url or os.environ.get(
            "FALCON_BASE_URL", "https://api.crowdstrike.com"
        )
        self.debug = debug
        self.user_agent_comment = user_agent_comment or os.environ.get(
            "FALCON_MCP_USER_AGENT_COMMENT"
        )
        self.member_cid = member_cid or os.environ.get("FALCON_MEMBER_CID")
        self.proxy = proxy or os.environ.get("FALCON_PROXY_URL")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Falcon API credentials not provided. Either pass client_id and client_secret "
                "parameters or set FALCON_CLIENT_ID and FALCON_CLIENT_SECRET environment variables."
            )

        # Build APIHarnessV2 initialization parameters
        api_params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "base_url": self.base_url,
            "debug": debug,
            "user_agent": self.get_user_agent(),
        }

        # Only include member_cid if it's provided
        if self.member_cid:
            api_params["member_cid"] = self.member_cid

        # Only include proxy if configured; APIHarnessV2 expects {"https": url}
        if self.proxy:
            api_params["proxy"] = {"https": self.proxy}

        # Initialize the Falcon API client using APIHarnessV2
        self.client = APIHarnessV2(**api_params)

        logger.debug("Initialized Falcon client with base URL: %s", self.base_url)
        if self.member_cid:
            logger.debug("Flight Control member_cid: %s", self.member_cid)

    @property
    def token_status(self) -> int | None:
        """HTTP status code from the last authentication attempt."""
        result: int | None = self.client.token_status
        return result

    @property
    def token_fail_reason(self) -> str | None:
        """Error message from the API when authentication failed."""
        result: str | None = self.client.token_fail_reason
        return result

    def auth_failure_message(self) -> str:
        """Build a diagnostic message after a failed authentication attempt."""
        parts = ["Failed to authenticate with the Falcon API"]
        if self.token_status:
            parts[0] += f" (HTTP {self.token_status})"
        if self.token_fail_reason:
            parts.append(self.token_fail_reason)

        if self.token_status == 401:
            parts.append(
                "Hint: Verify FALCON_CLIENT_ID and FALCON_CLIENT_SECRET are correct"
                " and the API key has not been revoked."
            )
        elif self.token_status == 403 and self.member_cid:
            parts.append(
                f"Hint: A member_cid is configured ({self.member_cid})."
                " Verify this is a valid child CID managed by your parent tenant,"
                " not the parent CID itself."
            )
        elif self.token_status == 403:
            parts.append(
                "Hint: Verify the API client has the required scopes"
                " and has not been disabled."
            )
        else:
            parts.append(
                f"Hint: Check network connectivity to {self.base_url}"
                " and verify FALCON_BASE_URL is correct for your CrowdStrike region."
            )

        return ". ".join(parts)

    def authenticate(self) -> bool:
        """Authenticate with the Falcon API.

        Returns:
            bool: True if authentication was successful
        """
        result: bool = self.client.login()
        return result

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated.

        Returns:
            bool: True if the client is authenticated
        """
        result: bool = self.client.token_valid
        return result

    def command(self, operation: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a Falcon API command.

        Args:
            operation: The API operation to execute
            **kwargs: Additional arguments to pass to the API

        Returns:
            dict[str, Any]: The API response
        """
        result: dict[str, Any] = self.client.command(operation, **kwargs)
        return result

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

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        This method returns the authentication headers from the underlying Falcon API client,
        which can be used for custom HTTP requests or advanced integration scenarios.

        Returns:
            dict[str, str]: Authentication headers including the bearer token
        """
        headers: dict[str, str] = self.client.auth_headers
        return headers


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
                    version_str: str = data["project"]["version"]
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
