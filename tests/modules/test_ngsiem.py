"""
Tests for the NGSIEM module.
"""

import asyncio
import os
import unittest
from unittest.mock import AsyncMock, patch

from falcon_mcp.modules.ngsiem import NGSIEMModule
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NGSIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)

        # search_ngsiem is async and calls the async offload wrapper command_async.
        # Route it through the sync `command` mock so the existing side_effect /
        # call_args_list assertions (which inspect `command`) keep working. Because
        # every routed call passes through both mocks, `command.call_count` above
        # `command_async.await_count` means the module reached the blocking sync
        # client directly — see test_search_ngsiem_offloads_every_api_call.
        async def _command_async(*args, **kwargs):
            return self.mock_client.command(*args, **kwargs)

        self.mock_client.command_async = AsyncMock(side_effect=_command_async)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_offloads_every_api_call(self, mock_sleep):
        """Every NGSIEM API call must go through command_async, never sync command.

        search_ngsiem is an async handler, so `offload_to_thread` returns it
        untouched — nothing else moves its Falcon calls off the event loop. A
        direct `self.client.command(...)` here would block the loop and undo the
        concurrency fix, so this fails if any call site reverts to the sync path.
        """
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-123", "hashedQueryOnView": "abc"}},
            {"status_code": 200, "body": {"done": True, "events": [{"aid": "agent-1"}]}},
        ]

        asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=ProcessRollup2",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
            )
        )

        self.assertEqual(
            self.mock_client.command_async.await_count,
            self.mock_client.command.call_count,
            "every Falcon call in search_ngsiem must be awaited via command_async; "
            "a count mismatch means a call site uses the blocking sync client",
        )
        self.assertEqual(self.mock_client.command_async.await_count, 2)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_ngsiem",
        ]
        self.assert_tools_registered(expected_tools)

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_ngsiem_cql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_success(self, mock_sleep):
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

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=ProcessRollup2",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
            )
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

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["aid"], "agent-1")
        self.assertEqual(result["results"][1]["event"], "DnsRequest")
        # A populated result carries no guide/hint
        self.assertNotIn("cql_guide", result)
        self.assertNotIn("hint", result)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_multiple_polls(self, mock_sleep):
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

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        # Verify multiple polls occurred (1 start + 3 polls)
        self.assertEqual(self.mock_client.command.call_count, 4)

        # Verify result
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["aid"], "agent-1")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_start_error(self, mock_sleep):
        """Test that a non-200 on StartSearchV1 returns error dict."""
        error_response = {
            "status_code": 403,
            "body": {"errors": [{"message": "Forbidden"}]},
        }
        self.mock_client.command.return_value = error_response

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        # Verify only one call was made (no polling)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to start NGSIEM search", result["error"])
        # Verify the CQL guide + repair hint reach the model on failure
        self.assertIn("cql_guide", result)
        self.assertIn("CQL", result["cql_guide"])
        self.assertIn("hint", result)
        self.assertEqual(result["query_used"], "aid=abc123")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_poll_error(self, mock_sleep):
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

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        # Verify error response
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("Failed to poll NGSIEM search status", result["error"])
        # Verify the CQL guide + repair hint reach the model on failure
        self.assertIn("cql_guide", result)
        self.assertIn("hint", result)
        self.assertEqual(result["query_used"], "aid=abc123")

    @patch("falcon_mcp.modules.ngsiem.TIMEOUT_SECONDS", 10)
    @patch("falcon_mcp.modules.ngsiem.POLL_INTERVAL_SECONDS", 5)
    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_timeout(self, mock_sleep):
        """Test that exceeding timeout calls StopSearchV1 and returns error."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-timeout"},
        }
        poll_not_done = {
            "status_code": 200,
            "body": {"done": False, "metaData": {"processedEvents": 4200, "timeMillis": 9000}},
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

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
            )
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
        # Cleanup outcome and how far the job got before the deadline
        self.assertEqual(result["details"]["stop_status_code"], 200)
        self.assertEqual(result["details"]["last_job_status"]["processed_events"], 4200)
        self.assertEqual(result["details"]["last_job_status"]["duration_ms"], 9000)
        # Verify the CQL guide + repair hint reach the model on timeout
        self.assertIn("cql_guide", result)
        self.assertIn("hint", result)
        self.assertEqual(result["query_used"], "aid=abc123")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_with_optional_params(self, mock_sleep):
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

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
                end="2025-02-06T00:00:00Z",
                repository="investigate_view",
            )
        )

        # Verify start call body includes end (as epoch ms)
        first_call = self.mock_client.command.call_args_list[0]
        body = first_call[1]["body"]
        self.assertEqual(body["end"], 1738800000000)  # 2025-02-06T00:00:00Z in epoch ms

        # Verify repository was passed as top-level kwarg (path variable)
        params = first_call[1]
        self.assertEqual(params["repository"], "investigate_view")

        # Verify empty result returns the dict envelope carrying the CQL guide + hint
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("cql_guide", result)
        self.assertIn("hint", result)
        self.assertEqual(result["query_used"], "aid=abc123")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_default_repository(self, mock_sleep):
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

        asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
            )
        )

        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["repository"], "search-all")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_special_characters_in_query(self, mock_sleep):
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
        result = asyncio.run(
            self.module.search_ngsiem(
                query_string=special_query,
                start="2025-01-01T00:00:00Z",
            )
        )

        # Verify query was passed through unchanged
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["body"]["queryString"], special_query)

        # Empty events now return the dict envelope; the query is echoed back verbatim
        self.assertIsInstance(result, dict)
        self.assertEqual(result["query_used"], special_query)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_missing_job_id(self, mock_sleep):
        """Test that a missing job ID in start response returns error."""
        start_response = {
            "status_code": 200,
            "body": {},
        }
        self.mock_client.command.return_value = start_response

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        # Verify only one call was made (no polling)
        self.assertEqual(self.mock_client.command.call_count, 1)

        # Verify error response uses _format_error_response structure
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("no job ID", result["error"])
        # Verify the CQL guide + repair hint reach the model on failure
        self.assertIn("cql_guide", result)
        self.assertIn("hint", result)
        self.assertEqual(result["query_used"], "aid=abc123")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_surfaces_job_metadata_on_success(self, mock_sleep):
        """A populated result carries the job metadata, mapped from the real body shape."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-meta"}},
            {
                "status_code": 200,
                "body": {
                    "done": True,
                    "cancelled": False,
                    "events": [{"aid": "agent-1"}],
                    "warnings": [],
                    "metaData": {
                        "eventCount": 1,
                        "processedEvents": 189064,
                        "processedBytes": 498887584,
                        "timeMillis": 5799,
                        "isAggregate": False,
                        "queryStart": 1735689600000,  # 2025-01-01T00:00:00Z
                        "queryEnd": 1735693200000,  # 2025-01-01T01:00:00Z
                        "warnings": [],
                        "filterQuery": {"queryString": "#event_simpleName=ProcessRollup2"},
                    },
                },
            },
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=ProcessRollup2 | head(1)",
                start="2025-01-01T00:00:00Z",
                repository="search-all",
            )
        )

        job = result["job"]
        self.assertEqual(job["job_id"], "job-meta")
        self.assertEqual(job["repository"], "search-all")
        self.assertEqual(job["event_count"], 1)
        self.assertEqual(job["processed_events"], 189064)
        self.assertEqual(job["processed_bytes"], 498887584)
        self.assertEqual(job["duration_ms"], 5799)
        self.assertIs(job["is_aggregate"], False)
        self.assertIs(job["cancelled"], False)
        self.assertEqual(job["warnings"], [])
        self.assertEqual(job["search_start"], "2025-01-01T00:00:00Z")
        self.assertEqual(job["search_end"], "2025-01-01T01:00:00Z")
        self.assertEqual(result["query_used"], "#event_simpleName=ProcessRollup2 | head(1)")
        self.assertEqual(job["parsed_query"], "#event_simpleName=ProcessRollup2")

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_search_ngsiem_exposes_misparse_on_populated_result(self, mock_sleep):
        """A misparsed query still returns rows, so parsed_query must survive success.

        Live, `| limit 5` returns 147 rows for a query the caller believes caps at 5.
        """
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-misparse"}},
            {
                "status_code": 200,
                "body": {
                    "done": True,
                    "events": [{"aid": f"agent-{i}"} for i in range(147)],
                    "metaData": {
                        "eventCount": 147,
                        "processedEvents": 66067,
                        "filterQuery": {
                            "queryString": "#event_simpleName=ProcessRollup2 | limit | 5"
                        },
                    },
                },
            },
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=ProcessRollup2 | limit 5",
                start="2025-01-01T00:00:00Z",
            )
        )

        self.assertEqual(len(result["results"]), 147)
        self.assertEqual(
            result["job"]["parsed_query"], "#event_simpleName=ProcessRollup2 | limit | 5"
        )

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_zero_rows_with_events_scanned_is_reported_as_a_real_negative(self, mock_sleep):
        """A job that scanned events and matched none is stated as a true negative.

        Live, a valid filter on an absent aid scans thousands of events; a misparsed
        query scans zero. So a nonzero scan count settles it.
        """
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-zero"}},
            {
                "status_code": 200,
                "body": {
                    "done": True,
                    "events": [],
                    "metaData": {
                        "eventCount": 0,
                        "processedEvents": 90102,
                        "processedBytes": 23734288,
                        "filterQuery": {"queryString": "#event_simpleName=DnsRequest"},
                    },
                },
            },
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=DnsRequest DomainName=*example*",
                start="2025-01-01T00:00:00Z",
            )
        )

        self.assertEqual(result["results"], [])
        self.assertEqual(result["job"]["processed_events"], 90102)
        # The scan count is quoted back, and the verdict is stated, not doubted
        self.assertIn("90,102", result["hint"])
        self.assertIn("a real negative", result["hint"])
        self.assertNotIn("not a confirmed negative", result["hint"])
        self.assertNotIn("it is also how the API reports an invalid query", result["hint"])

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_zero_rows_with_nothing_scanned_stays_unresolved(self, mock_sleep):
        """Zero scanned events is ambiguous, so the hint points at parsed_query.

        Live, both an empty tag partition and a misparse scan zero.
        """
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-unscanned"}},
            {
                "status_code": 200,
                "body": {
                    "done": True,
                    "events": [],
                    "metaData": {
                        "eventCount": 0,
                        "processedEvents": 0,
                        "processedBytes": 0,
                        "filterQuery": {"queryString": "#event_simpleName=ProcessRollupTwo"},
                    },
                },
            },
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="#event_simpleName=ProcessRollupTwo | head(3)",
                start="2025-01-01T00:00:00Z",
            )
        )

        self.assertEqual(result["job"]["processed_events"], 0)
        self.assertIn("not a confirmed negative", result["hint"])
        self.assertIn("parsed_query", result["hint"])
        self.assertIn("cql_guide", result)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_absent_metadata_reports_none_rather_than_zero(self, mock_sleep):
        """A response without metaData reports None, not a fabricated 0."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-bare"}},
            {"status_code": 200, "body": {"done": True, "events": []}},
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        job = result["job"]
        self.assertIsNone(job["event_count"])
        self.assertIsNone(job["processed_events"])
        self.assertIsNone(job["parsed_query"])
        self.assertIsNone(job["search_start"])
        self.assertIsNone(job["search_end"])
        self.assertIn("not a confirmed negative", result["hint"])

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_warnings_are_merged_from_both_scopes(self, mock_sleep):
        """Warnings from both the job-level and metaData scopes reach the caller."""
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-warn"}},
            {
                "status_code": 200,
                "body": {
                    "done": True,
                    "events": [{"aid": "agent-1"}],
                    "warnings": ["job-level warning"],
                    "metaData": {"warnings": ["query-level warning"]},
                },
            },
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
            )
        )

        self.assertEqual(result["job"]["warnings"], ["job-level warning", "query-level warning"])

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_empty_and_populated_results_share_one_shape(self, mock_sleep):
        """Both outcomes must be the same shape, so a caller needs one parse path."""
        common = ["results", "query_used", "job"]

        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-a"}},
            {"status_code": 200, "body": {"done": True, "events": [{"aid": "agent-1"}]}},
        ]
        populated = asyncio.run(
            self.module.search_ngsiem(query_string="aid=a", start="2025-01-01T00:00:00Z")
        )

        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-b"}},
            {"status_code": 200, "body": {"done": True, "events": []}},
        ]
        empty = asyncio.run(
            self.module.search_ngsiem(query_string="aid=b", start="2025-01-01T00:00:00Z")
        )

        for key in common:
            self.assertIn(key, populated)
            self.assertIn(key, empty)
        self.assertIsInstance(populated["results"], list)
        self.assertIsInstance(empty["results"], list)
        self.assertEqual(sorted(populated["job"]), sorted(empty["job"]))

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_repository_that_would_alter_the_request_path_is_rejected(self, mock_sleep):
        """`repository` reaches a URL path variable, so it must not carry path syntax.

        FalconPy interpolates path variables into the route, and `requests` then
        normalizes the path before sending it. An unencoded separator or dot-segment
        therefore retargets the request: `a/../../oauth2/token` builds
        `/humio/api/v1/repositories/a/../../oauth2/token/queryjobs`, which normalizes
        to `/humio/api/v1/oauth2/token/queryjobs` — a different route than
        StartSearchV1 selected. Reject before any call rather than relying on the SDK.

        The client is wired to succeed, so without the guard this reports a clean
        search result and the assertions fail on that, not on a mock error.
        """
        for repository in (
            "a/../../oauth2/token",
            "search-all/queryjobs",
            "..",
            "../search-all",
            "search\\all",
            "search%2Fall",
        ):
            with self.subTest(repository=repository):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = [
                    {"status_code": 200, "body": {"id": "job-should-not-run"}},
                    {"status_code": 200, "body": {"done": True, "events": []}},
                ]

                result = asyncio.run(
                    self.module.search_ngsiem(
                        query_string="aid=abc123",
                        start="2025-01-01T00:00:00Z",
                        repository=repository,
                    )
                )

                self.assertIn("error", result)
                self.assertIn("repository", result["error"])
                # The guard is worthless if the request still goes out.
                self.assertEqual(self.mock_client.command.call_count, 0)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_repository_rejection_does_not_offer_the_cql_guide(self, mock_sleep):
        """A bad `repository` is not a CQL mistake, so it must not ship the CQL guide.

        Every other error path here routes through `_format_cql_error_response`, which
        attaches the full guide and tells the model to correct its query. Doing that
        for an argument error would send the model to rewrite a query that was fine.
        """
        self.mock_client.command.side_effect = [
            {"status_code": 200, "body": {"id": "job-should-not-run"}},
            {"status_code": 200, "body": {"done": True, "events": []}},
        ]

        result = asyncio.run(
            self.module.search_ngsiem(
                query_string="aid=abc123",
                start="2025-01-01T00:00:00Z",
                repository="a/../../oauth2/token",
            )
        )

        self.assertIn("error", result)
        self.assertNotIn("cql_guide", result)
        self.assertNotIn("hint", result)

    @patch("falcon_mcp.modules.ngsiem.asyncio.sleep", new_callable=AsyncMock)
    def test_documented_repository_names_still_pass_the_guard(self, mock_sleep):
        """The guard must not reject the repositories the tool advertises.

        The field description names these and says custom views may also be passed,
        so an over-strict rule would break normal use. This is the counterweight to
        the rejection test above.
        """
        for repository in (
            "search-all",
            "investigate_view",
            "xdr",
            "third-party",
            "falcon_for_it_view",
            "forensics_view",
        ):
            with self.subTest(repository=repository):
                self.mock_client.command.reset_mock()
                self.mock_client.command.side_effect = [
                    {"status_code": 200, "body": {"id": "job-ok"}},
                    {"status_code": 200, "body": {"done": True, "events": []}},
                ]

                result = asyncio.run(
                    self.module.search_ngsiem(
                        query_string="aid=abc123",
                        start="2025-01-01T00:00:00Z",
                        repository=repository,
                    )
                )

                self.assertNotIn("error", result)
                self.assertEqual(self.mock_client.command.call_count, 2)


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
