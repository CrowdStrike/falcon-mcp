"""
Integration tests for Flight Control (MSSP) support.

These tests verify that the member_cid parameter works correctly with real API calls.

Prerequisites:
- FALCON_CLIENT_ID and FALCON_CLIENT_SECRET environment variables set with parent CID credentials
- FALCON_MEMBER_CID environment variable set with a valid child CID
- Flight Control enabled on the parent tenant
- Parent API client must have appropriate scopes for the child CID

Note: These tests require a real Flight Control enabled tenant and will be skipped if
FALCON_MEMBER_CID is not set.
"""

import os

import pytest

from falcon_mcp.client import FalconClient


@pytest.fixture(scope="module")
def member_cid():
    """
    Get the member_cid from environment for testing.

    Tests will be skipped if FALCON_MEMBER_CID is not set.
    """
    member_cid_value = os.environ.get("FALCON_MEMBER_CID")
    if not member_cid_value:
        pytest.skip(
            "Flight Control integration tests require FALCON_MEMBER_CID environment variable. "
            "Set this to a valid child CID in your .env file or environment."
        )
    return member_cid_value


@pytest.fixture(scope="module")
def parent_client():
    """
    Create a FalconClient for the parent CID (no member_cid).

    This client will authenticate with the parent tenant.
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


@pytest.fixture(scope="module")
def child_client(member_cid):
    """
    Create a FalconClient for a child CID using member_cid parameter.

    This client will authenticate with the specified child tenant.
    """
    client_id = os.environ.get("FALCON_CLIENT_ID")
    client_secret = os.environ.get("FALCON_CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip(
            "Integration tests require FALCON_CLIENT_ID and FALCON_CLIENT_SECRET "
            "environment variables. Set these in your .env file or environment."
        )

    client = FalconClient(member_cid=member_cid)

    if not client.authenticate():
        pytest.skip(
            "Failed to authenticate with Falcon API using member_cid. "
            "Check that Flight Control is enabled and the member_cid is valid."
        )

    return client


def test_client_initialization_with_member_cid(member_cid):
    """Test that FalconClient can be initialized with member_cid."""
    client = FalconClient(member_cid=member_cid)
    assert client.member_cid == member_cid


def test_client_initialization_with_env_var_member_cid(member_cid):
    """Test that FalconClient loads member_cid from environment variable."""
    # member_cid fixture already checks that FALCON_MEMBER_CID is set
    client = FalconClient()

    # If FALCON_MEMBER_CID is set, it should be loaded
    # If not set, it should be None (which causes the skip in the fixture)
    if os.environ.get("FALCON_MEMBER_CID"):
        assert client.member_cid == member_cid


def test_parent_client_connectivity(parent_client):
    """Test connectivity with parent CID client."""
    assert parent_client.is_authenticated()


def test_child_client_connectivity(child_client):
    """Test connectivity with child CID client."""
    assert child_client.is_authenticated()


def test_child_client_has_different_token_context(parent_client, child_client):
    """
    Test that parent and child clients have different authentication contexts.

    This is a sanity check to ensure that member_cid actually affects the token.
    Note: Both clients may have similar headers format but the token should be
    scoped differently (we can't directly validate token claims without decoding).
    """
    parent_headers = parent_client.get_headers()
    child_headers = child_client.get_headers()

    # Both should have Authorization headers
    assert "Authorization" in parent_headers
    assert "Authorization" in child_headers

    # The tokens should be different (different CID context)
    # Note: In some cases they might be the same if member_cid doesn't affect the token,
    # but typically they should differ
    assert parent_headers["Authorization"] != child_headers["Authorization"], (
        "Parent and child clients have identical tokens, which suggests member_cid "
        "is not affecting authentication. Check Flight Control configuration."
    )


def test_child_client_command_execution(child_client):
    """
    Test that child client can execute commands successfully.

    This uses a simple query operation that should work with minimal permissions.
    """
    # Use QueryDevicesByFilter as a lightweight test operation
    # This should return data scoped to the child CID
    result = child_client.command(
        "QueryDevicesByFilter",
        limit=1,  # Just need one result to verify it works
    )

    # Check basic response structure
    assert isinstance(result, dict)
    assert "status_code" in result

    # Status code should be 200 (success) or 404 (no devices found, but API worked)
    assert result["status_code"] in [200, 404], (
        f"Unexpected status code: {result['status_code']}. "
        f"Response: {result}"
    )


def test_member_cid_stored_correctly(member_cid):
    """Test that member_cid is stored correctly in the client instance."""
    client = FalconClient(member_cid=member_cid)
    assert hasattr(client, "member_cid")
    assert client.member_cid == member_cid


def test_member_cid_parameter_precedence(member_cid):
    """Test that member_cid parameter takes precedence over environment variable."""
    # Even if FALCON_MEMBER_CID is set in environment, the parameter should override
    param_cid = "param-override-cid"
    client = FalconClient(member_cid=param_cid)
    assert client.member_cid == param_cid
    assert client.member_cid != member_cid  # Should not use env var
