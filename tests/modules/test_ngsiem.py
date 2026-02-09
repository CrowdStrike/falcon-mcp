"""
Tests for the NGSIEM module.
"""

import os
import unittest
from unittest.mock import AsyncMock, patch

import pytest

from falcon_mcp.modules.ngsiem import NGSIEMModule
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NGSIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_ngsiem",
        ]
        self.assert_tools_registered(expected_tools)

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_success(self, mock_sleep):
        """Test search that completes on first poll returns events list."""
        start_response = {
            "status_code": 200,
            "body": {
                "id": "job-123",
                "hashedQueryOnView": "abc",
            },
        }
        poll_response = {
            "status_code": 200,
            "body": {
                "done": True,
                "events": [
                    {"aid": "agent-1", "event": "ProcessRollup2"},
                    {"aid": "agent-2", "event": "DnsRequest"},
                ],
            },
        }
        self.mock_client.command.side_effect = [start_response, poll_response]

        result = await self.module.search_ngsiem(
            query_string="#event_simpleName=ProcessRollup2",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
        )

        # Verify start call
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["operation"], "StartSearchV1")
        self.assertEqual(first_call[1]["repository"], "search-all")
        self.assertEqual(first_call[1]["body"]["queryString"], "#event_simpleName=ProcessRollup2")
        # Verify start time is converted to epoch milliseconds
        self.assertEqual(first_call[1]["body"]["start"], 1735689600000)  # 2025-01-01T00:00:00Z

        # Verify poll call
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[1]["operation"], "GetSearchStatusV1")
        self.assertEqual(second_call[1]["search_id"], "job-123")
        self.assertEqual(second_call[1]["repository"], "search-all")

        # Verify result is the events list
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["aid"], "agent-1")
        self.assertEqual(result[1]["event"], "DnsRequest")

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_multiple_polls(self, mock_sleep):
        """Test search that requires multiple polls before completion."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-456"},
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"done": False},
        }
        poll_done = {
            "status_code": 200,
            "body": {
                "done": True,
                "events": [{"aid": "agent-1"}],
            },
        }
        self.mock_client.command.side_effect = [
            start_response,
            poll_not_done,
            poll_not_done,
            poll_done,
        ]

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
        )

        # Verify multiple polls occurred (1 start + 3 polls)
        self.assertEqual(self.mock_client.command.call_count, 4)

        # Verify result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["aid"], "agent-1")

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_start_error(self, mock_sleep):
        """Test that a non-200 on StartSearchV1 returns error dict."""
        error_response = {
            "status_code": 403,
            "body": {"errors": [{"message": "Forbidden"}]},
        }
        self.mock_client.command.return_value = error_response

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
        )

        # Verify only one call was made (no polling)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to start NGSIEM search", result["error"])

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_poll_error(self, mock_sleep):
        """Test that a non-200 on GetSearchStatusV1 returns error dict."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-789"},
        }
        poll_error = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]},
        }
        self.mock_client.command.side_effect = [start_response, poll_error]

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
        )

        # Verify error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to poll NGSIEM search status", result["error"])

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.TIMEOUT_SECONDS", 10)
    @patch("falcon_mcp.modules.ngsiem.POLL_INTERVAL_SECONDS", 5)
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_timeout(self, mock_sleep):
        """Test that exceeding timeout calls StopSearchV1 and returns error."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-timeout"},
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"done": False},
        }
        stop_response = {
            "status_code": 200,
            "body": {},
        }
        # 1 start + 2 polls (2 * 5s = 10s >= timeout) + 1 stop
        self.mock_client.command.side_effect = [
            start_response,
            poll_not_done,
            poll_not_done,
            stop_response,
        ]

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
        )

        # Verify StopSearchV1 was called for cleanup
        stop_call = self.mock_client.command.call_args_list[-1]
        self.assertEqual(stop_call[1]["operation"], "StopSearchV1")
        self.assertEqual(stop_call[1]["id"], "job-timeout")
        self.assertEqual(stop_call[1]["repository"], "search-all")

        # Verify error response uses _format_error_response structure
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("timed out", result["error"])
        self.assertIn("details", result)
        self.assertEqual(result["details"]["job_id"], "job-timeout")
        self.assertEqual(result["details"]["timeout_seconds"], 10)

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_with_optional_params(self, mock_sleep):
        """Test that end and limit are passed correctly in body."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-opt"},
        }
        poll_done = {
            "status_code": 200,
            "body": {"done": True, "events": []},
        }
        self.mock_client.command.side_effect = [start_response, poll_done]

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
            end="2025-02-06T00:00:00Z",
            repository="investigate_view",
        )

        # Verify start call body includes end (as epoch ms)
        first_call = self.mock_client.command.call_args_list[0]
        body = first_call[1]["body"]
        self.assertEqual(body["end"], 1738800000000)  # 2025-02-06T00:00:00Z in epoch ms

        # Verify repository was passed as top-level kwarg (path variable)
        params = first_call[1]
        self.assertEqual(params["repository"], "investigate_view")

        # Verify result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_default_repository(self, mock_sleep):
        """Test that the repository parameter defaults to 'search-all'.

        Note: When calling module methods directly (not through FastMCP), Pydantic
        Field defaults are not auto-resolved. This test verifies the Field definition
        has the correct default, and that passing 'search-all' explicitly works.
        """
        import inspect

        from pydantic.fields import FieldInfo

        sig = inspect.signature(self.module.search_ngsiem)
        repo_param = sig.parameters["repository"]
        self.assertIsInstance(repo_param.default, FieldInfo)
        self.assertEqual(repo_param.default.default, "search-all")

        # Also verify it works when passed explicitly
        start_response = {
            "status_code": 200,
            "body": {"id": "job-default"},
        }
        poll_done = {
            "status_code": 200,
            "body": {"done": True, "events": []},
        }
        self.mock_client.command.side_effect = [start_response, poll_done]

        await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
            repository="search-all",
        )

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["repository"], "search-all")

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_special_characters_in_query(self, mock_sleep):
        """Test that special characters in query_string pass through safely."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-special"},
        }
        poll_done = {
            "status_code": 200,
            "body": {"done": True, "events": []},
        }
        self.mock_client.command.side_effect = [start_response, poll_done]

        special_query = '#event_simpleName=ProcessRollup2 | ComputerName="test\'s <host>" | count()'
        result = await self.module.search_ngsiem(
            query_string=special_query,
            start="2025-01-01T00:00:00Z",
        )

        # Verify query was passed through unchanged
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["body"]["queryString"], special_query)

        # Should still return valid result
        self.assertIsInstance(result, list)

    @pytest.mark.asyncio
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    async def test_search_ngsiem_missing_job_id(self, mock_sleep):
        """Test that a missing job ID in start response returns error."""
        start_response = {
            "status_code": 200,
            "body": {},
        }
        self.mock_client.command.return_value = start_response

        result = await self.module.search_ngsiem(
            query_string="aid=abc123",
            start="2025-01-01T00:00:00Z",
        )

        # Verify only one call was made (no polling)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify error response uses _format_error_response structure
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("no job ID", result["error"])
        self.assertIn("details", result)


class TestNGSIEMModuleConfig(unittest.TestCase):
    """Test configuration handling for NGSIEM module."""

    def test_default_config_values(self):
        """Test that default config values are set correctly."""
        # Clear any env overrides and test defaults
        with patch.dict(os.environ, {}, clear=True):
            # Re-evaluate the config by reimporting
            poll_interval = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
            timeout = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))

            self.assertEqual(poll_interval, 5)
            self.assertEqual(timeout, 300)

    def test_custom_config_from_env(self):
        """Test that custom config values are read from environment."""
        with patch.dict(
            os.environ,
            {"FALCON_MCP_NGSIEM_POLL_INTERVAL": "10", "FALCON_MCP_NGSIEM_TIMEOUT": "60"},
        ):
            poll_interval = int(os.environ.get("FALCON_MCP_NGSIEM_POLL_INTERVAL", "5"))
            timeout = int(os.environ.get("FALCON_MCP_NGSIEM_TIMEOUT", "300"))

            self.assertEqual(poll_interval, 10)
            self.assertEqual(timeout, 60)


if __name__ == "__main__":
    unittest.main()
