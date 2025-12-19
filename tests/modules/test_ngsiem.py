"""
Tests for the NG-SIEM module.
"""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from falcon_mcp.modules.ngsiem import NGSIEMModule, NGSIEMQueryEngine, NGSIEMConfig
from tests.modules.utils.test_modules import TestModules


class TestNGSIEMModule(TestModules):
    """Test cases for the NG-SIEM module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(NGSIEMModule)
        self.query_engine = NGSIEMQueryEngine(self.mock_client)

    # Test 3: Time Range Parsing Tests
    def test_parse_time_range_relative_minutes(self):
        """Test parsing relative time ranges in minutes."""
        result = self.query_engine.parse_time_range("15m")

        self.assertIn("start", result)
        self.assertIn("end", result)
        self.assertIsInstance(result["start"], int)
        self.assertIsInstance(result["end"], int)

        # Check that the time difference is approximately 15 minutes (900 seconds)
        time_diff_seconds = (result["end"] - result["start"]) / 1000
        self.assertAlmostEqual(time_diff_seconds, 900, delta=5)

    def test_parse_time_range_relative_hours(self):
        """Test parsing relative time ranges in hours."""
        result = self.query_engine.parse_time_range("24h")

        self.assertIn("start", result)
        self.assertIn("end", result)

        # Check that the time difference is approximately 24 hours (86400 seconds)
        time_diff_seconds = (result["end"] - result["start"]) / 1000
        self.assertAlmostEqual(time_diff_seconds, 86400, delta=5)

    def test_parse_time_range_relative_days(self):
        """Test parsing relative time ranges in days."""
        result = self.query_engine.parse_time_range("7d")

        self.assertIn("start", result)
        self.assertIn("end", result)

        # Check that the time difference is approximately 7 days (604800 seconds)
        time_diff_seconds = (result["end"] - result["start"]) / 1000
        self.assertAlmostEqual(time_diff_seconds, 604800, delta=5)

    def test_parse_time_range_relative_weeks(self):
        """Test parsing relative time ranges in weeks."""
        result = self.query_engine.parse_time_range("2w")

        self.assertIn("start", result)
        self.assertIn("end", result)

        # Check that the time difference is approximately 2 weeks (1209600 seconds)
        time_diff_seconds = (result["end"] - result["start"]) / 1000
        self.assertAlmostEqual(time_diff_seconds, 1209600, delta=5)

    def test_parse_time_range_absolute_start_end(self):
        """Test parsing absolute time ranges with start and end."""
        time_range = "2024-01-01T00:00:00Z,2024-01-02T00:00:00Z"
        result = self.query_engine.parse_time_range(time_range)

        self.assertIn("start", result)
        self.assertIn("end", result)

        # Convert back to datetime to verify parsing
        start_dt = datetime.fromtimestamp(result["start"] / 1000, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(result["end"] / 1000, tz=timezone.utc)

        self.assertEqual(start_dt.year, 2024)
        self.assertEqual(start_dt.month, 1)
        self.assertEqual(start_dt.day, 1)
        self.assertEqual(end_dt.day, 2)

    def test_parse_time_range_single_timestamp(self):
        """Test parsing single timestamp (start time only)."""
        time_range = "2024-01-01T00:00:00Z"
        result = self.query_engine.parse_time_range(time_range)

        self.assertIn("start", result)
        self.assertIn("end", result)

        # Start should be the specified time
        start_dt = datetime.fromtimestamp(result["start"] / 1000, tz=timezone.utc)
        self.assertEqual(start_dt.year, 2024)
        self.assertEqual(start_dt.month, 1)
        self.assertEqual(start_dt.day, 1)

        # End should be approximately now
        end_dt = datetime.fromtimestamp(result["end"] / 1000, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        self.assertAlmostEqual(end_dt.timestamp(), now.timestamp(), delta=5)

    # Test 4: Search Parameter Building Tests
    def test_build_search_parameters_relative(self):
        """Test building search parameters for relative time ranges."""
        query = "#event_simpleName=ProcessRollup2"
        time_range = "15m"
        time_params = self.query_engine.parse_time_range(time_range)

        params = self.query_engine._build_search_parameters(query, time_range, time_params)

        self.assertEqual(params["queryString"], query)
        self.assertEqual(params["start"], time_range)
        self.assertFalse(params["isLive"])
        self.assertEqual(params["timeZoneOffsetMinutes"], 0)
        # For relative time ranges, "end" should not be present
        self.assertNotIn("end", params)

    def test_build_search_parameters_absolute(self):
        """Test building search parameters for absolute time ranges."""
        query = "#event_simpleName=ProcessRollup2"
        time_range = "2024-01-01T00:00:00Z,2024-01-02T00:00:00Z"
        time_params = self.query_engine.parse_time_range(time_range)

        params = self.query_engine._build_search_parameters(query, time_range, time_params)

        self.assertEqual(params["queryString"], query)
        self.assertIn("start", params)
        self.assertIn("end", params)
        self.assertFalse(params["isLive"])
        self.assertEqual(params["timeZoneOffsetMinutes"], 0)

        # For absolute time ranges, start and end should be timestamp strings
        self.assertEqual(params["start"], str(time_params["start"]))
        self.assertEqual(params["end"], str(time_params["end"]))

    def test_build_search_parameters_single_timestamp(self):
        """Test building search parameters for single timestamp."""
        query = "#event_simpleName=ProcessRollup2"
        time_range = "2024-01-01T00:00:00Z"
        time_params = self.query_engine.parse_time_range(time_range)

        params = self.query_engine._build_search_parameters(query, time_range, time_params)

        self.assertEqual(params["queryString"], query)
        self.assertIn("start", params)
        self.assertIn("end", params)
        self.assertFalse(params["isLive"])
        self.assertEqual(params["timeZoneOffsetMinutes"], 0)

    # Test 5: Search ID Extraction Tests
    def test_extract_search_id_from_body(self):
        """Test extracting search ID from response body."""
        response = {"body": {"id": "search-123"}}
        search_id = self.query_engine._extract_search_id(response)
        self.assertEqual(search_id, "search-123")

    def test_extract_search_id_from_resources(self):
        """Test extracting search ID from response resources."""
        response = {"resources": {"id": "search-456"}}
        search_id = self.query_engine._extract_search_id(response)
        self.assertEqual(search_id, "search-456")

    def test_extract_search_id_from_top_level(self):
        """Test extracting search ID from top-level response."""
        response = {"id": "search-789"}
        search_id = self.query_engine._extract_search_id(response)
        self.assertEqual(search_id, "search-789")

    def test_extract_search_id_not_found(self):
        """Test handling when search ID is not found."""
        response = {"body": {}}
        search_id = self.query_engine._extract_search_id(response)
        self.assertIsNone(search_id)

    def test_extract_search_id_empty_response(self):
        """Test handling empty response."""
        response = {}
        search_id = self.query_engine._extract_search_id(response)
        self.assertIsNone(search_id)

    def test_extract_search_id_non_dict_body(self):
        """Test handling when body is not a dictionary."""
        response = {"body": "not a dict"}
        search_id = self.query_engine._extract_search_id(response)
        self.assertIsNone(search_id)

    # Test 7: Error Handling Tests
    def test_execute_query_authentication_failure(self):
        """Test handling authentication failure."""
        self.mock_client.is_authenticated.return_value = False

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        self.assertIn("error", result)
        self.assertIn("Authentication failed", str(result))

    def test_execute_query_invalid_repository_warning(self):
        """Test warning for invalid repository."""
        # Mock successful authentication to get past that check
        self.mock_client.is_authenticated.return_value = True

        # Mock start_search to raise an exception so we can capture the warning
        self.mock_client.command.side_effect = Exception("Test exception")

        with self.assertLogs('falcon_mcp.modules.ngsiem', level='WARNING') as log:
            result = self.module.execute_ngsiem_query(
                query="#event_simpleName=ProcessRollup2",
                repository="invalid_repo"
            )

        # Check that warning was logged
        self.assertTrue(any("invalid_repo" in message for message in log.output))
        # Should return error response
        self.assertIn("error", result)

    def test_execute_query_start_search_failure(self):
        """Test handling start_search API failure."""
        self.mock_client.is_authenticated.return_value = True
        self.mock_client.command.return_value = {
            "status_code": 500,
            "body": {"errors": [{"message": "Internal server error"}]}
        }

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        self.assertIn("error", result)

    def test_execute_query_missing_search_id(self):
        """Test handling when search ID cannot be extracted."""
        self.mock_client.is_authenticated.return_value = True
        self.mock_client.command.return_value = {
            "status_code": 200,
            "body": {}  # No search ID
        }

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        self.assertIn("error", result)
        self.assertIn("Search ID not found", str(result))

    def test_execute_query_exception_handling(self):
        """Test general exception handling."""
        self.mock_client.is_authenticated.side_effect = Exception("Test exception")

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        self.assertIn("error", result)
        self.assertIn("Query execution failed", str(result))

    # Test 8: Integration Tests (with mocking)
    @patch('falcon_mcp.modules.ngsiem.time.sleep')  # Speed up polling tests
    def test_successful_query_execution(self, mock_sleep):
        """Test successful query execution end-to-end."""
        # Mock successful authentication
        self.mock_client.is_authenticated.return_value = True

        # Mock successful search start (StartSearchV1) and status check (GetSearchStatusV1)
        def mock_command(operation, **kwargs):
            if operation == "StartSearchV1":
                return {
                    "status_code": 200,
                    "body": {"id": "search-123"}
                }
            elif operation == "GetSearchStatusV1":
                return {
                    "status_code": 200,
                    "body": {
                        "done": True,
                        "events": [{"event": "test_event", "timestamp": "2024-01-01T00:00:00Z"}]
                    }
                }
            return {}

        self.mock_client.command.side_effect = mock_command

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2 | tail(3)",
            time_range="15m"
        )

        # Should have successful response structure
        self.assertIn("search_id", result)
        self.assertIn("results", result)
        self.assertIn("query", result)
        self.assertIn("time_range", result)
        self.assertIn("result_count", result)
        self.assertEqual(result["search_id"], "search-123")
        self.assertEqual(result["query"], "#event_simpleName=ProcessRollup2 | tail(3)")

        # Verify client methods were called
        self.mock_client.is_authenticated.assert_called()
        self.mock_client.command.assert_called()


    @patch('falcon_mcp.modules.ngsiem.time.sleep')
    def test_query_polling_status_feedback(self, mock_sleep):
        """Test query execution provides status feedback for long-running queries."""
        # Mock successful authentication
        self.mock_client.is_authenticated.return_value = True

        # Mock polling that returns done=False multiple times before completing
        poll_call_count = 0
        def mock_command_polling(operation, **kwargs):
            nonlocal poll_call_count
            if operation == "StartSearchV1":
                return {
                    "status_code": 200,
                    "body": {"id": "search-long-running"}
                }
            elif operation == "GetSearchStatusV1":
                poll_call_count += 1
                return {"status_code": 200, "body": {"done": False}}
            return {}

        self.mock_client.command.side_effect = mock_command_polling

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        # Should return long-running query status
        self.assertIn("polling_status", result)
        self.assertEqual(result["polling_status"], "long_running_query")
        self.assertIn("search_id", result)
        self.assertIn("elapsed_time_seconds", result)
        self.assertIn("suggestions", result)

    @patch('falcon_mcp.modules.ngsiem.time.sleep')
    def test_query_polling_error(self, mock_sleep):
        """Test handling polling errors."""
        # Mock successful authentication
        self.mock_client.is_authenticated.return_value = True

        # Mock successful start, then polling error
        def mock_command_error(operation, **kwargs):
            if operation == "StartSearchV1":
                return {
                    "status_code": 200,
                    "body": {"id": "search-poll-error"}
                }
            elif operation == "GetSearchStatusV1":
                return {
                    "status_code": 500,
                    "body": {"errors": [{"message": "Polling failed"}]}
                }
            return {}

        self.mock_client.command.side_effect = mock_command_error

        result = self.module.execute_ngsiem_query(
            query="#event_simpleName=ProcessRollup2",
            time_range="15m"
        )

        # Should return error from polling
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()