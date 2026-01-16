"""
E2E tests for the Detections module.
"""

import re
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestDetectionsModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Detections Module.
    """

    def test_get_top_3_high_severity_detections(self):
        """Verify the agent can retrieve the top 3 high-severity detections."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetQueriesAlertsV2",
                    "validator": lambda kwargs: (
                        (
                            "severity:>=60+severity:<80"
                            in (
                                filter_str := kwargs.get("parameters", {}).get("filter", "").lower()
                            )
                            or "severity_name:'high'" in filter_str
                        )
                        and kwargs.get("parameters", {}).get("limit", 0) == 3
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"resources": ["detection-1", "detection-2", "detection-3"]},
                    },
                },
                {
                    "operation": "PostEntitiesAlertsV2",
                    "validator": lambda kwargs: "detection-1"
                    in kwargs.get("body", {}).get("composite_ids", []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "detection-1",
                                    "composite_id": "detection-1",
                                    "status": "new",
                                    "severity": 75,
                                    "severity_name": "High",
                                    "confidence": 85,
                                    "description": "A high detection for E2E testing.",
                                    "created_timestamp": "2024-01-20T10:00:00Z",
                                    "agent_id": "test-agent-001",
                                },
                                {
                                    "id": "detection-2",
                                    "composite_id": "detection-2",
                                    "status": "new",
                                    "severity": 70,
                                    "severity_name": "High",
                                    "confidence": 80,
                                    "description": "A high severity detection for E2E testing.",
                                    "created_timestamp": "2024-01-20T09:30:00Z",
                                    "agent_id": "test-agent-002",
                                },
                                {
                                    "id": "detection-3",
                                    "composite_id": "detection-3",
                                    "status": "new",
                                    "severity": 70,
                                    "severity_name": "High",
                                    "confidence": 75,
                                    "description": "Another high severity detection for E2E testing.",
                                    "created_timestamp": "2024-01-20T09:00:00Z",
                                    "agent_id": "test-agent-003",
                                },
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Give me the details of the 3 most recent detections of severity level high."
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Validate tool execution - search_detections must be called (may have extra calls)
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertIn(
                "falcon_search_detections",
                tool_names,
                f"Expected falcon_search_detections in tool calls. Got: {tool_names}",
            )

            # Find the successful GetQueriesAlertsV2 call with correct parameters
            # (LLMs may retry with corrected params, so search all calls)
            search_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "GetQueriesAlertsV2":
                    params = call[1].get("parameters", {})
                    filter_str = params.get("filter", "").lower()

                    # Check if this call has valid high severity filtering
                    is_numeric_high = ">=60" in filter_str and "<80" in filter_str
                    is_named_high = "severity_name" in filter_str and "high" in filter_str

                    if (is_numeric_high or is_named_high) and params.get("limit") == 3:
                        search_call = call
                        break

            self.assertIsNotNone(
                search_call,
                "Expected GetQueriesAlertsV2 call with High severity filter and limit=3",
            )

            # Validate search API call parameters from the successful call
            search_params = search_call[1].get("parameters", {})
            filter_str = search_params.get("filter", "").lower()

            # Validate "high severity only" filtering (accept both numeric and name-based)
            is_numeric_high = ">=60" in filter_str and "<80" in filter_str
            is_named_high = "severity_name" in filter_str and "high" in filter_str
            self.assertTrue(
                is_numeric_high or is_named_high,
                f"Expected High severity filtering. Got: {filter_str}",
            )

            self.assertEqual(search_params.get("limit"), 3, "Expected limit of 3")

            # Validate "latest" sorting (accept both timestamp options with . or | separator)
            sort_param = search_params.get("sort", "")
            sort_pattern = r"(timestamp|created_timestamp)[.|]desc"
            self.assertTrue(
                re.search(sort_pattern, sort_param, re.IGNORECASE),
                f"Expected descending timestamp sort. Got: {sort_param}",
            )

            # Find the PostEntitiesAlertsV2 call with the expected detection IDs
            details_call = None
            expected_ids = ["detection-1", "detection-2", "detection-3"]
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "PostEntitiesAlertsV2":
                    body = call[1].get("body", {})
                    if body.get("composite_ids") == expected_ids:
                        details_call = call
                        break

            self.assertIsNotNone(
                details_call,
                "Expected PostEntitiesAlertsV2 call with detection IDs",
            )

            # Validate final result contains all expected detections
            for detection_id in expected_ids:
                self.assertIn(detection_id, result, f"Expected {detection_id} in final result")

        self.run_test_with_retries(
            "test_get_top_3_high_severity_detections",
            test_logic,
            assertions,
        )

    def test_get_highest_detection_for_ip(self):
        """Verify the agent can find the highest-severity detection for a specific IP."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetQueriesAlertsV2",
                    "validator": lambda kwargs: "10.0.0.1"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {"resources": ["detection-4"]},
                    },
                },
                {
                    "operation": "PostEntitiesAlertsV2",
                    "validator": lambda kwargs: "detection-4"
                    in kwargs.get("body", {}).get("composite_ids", []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "detection-4",
                                    "composite_id": "detection-4",
                                    "status": "new",
                                    "severity": 90,
                                    "severity_name": "Critical",
                                    "confidence": 95,
                                    "description": "A critical detection on a specific IP.",
                                    "created_timestamp": "2024-01-20T11:00:00Z",
                                    "agent_id": "test-agent-004",
                                    "local_ip": "10.0.0.1",
                                }
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Search for detections on the device with local_ip 10.0.0.1 and return the highest severity detection id"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Validate tool execution - search_detections must be called (may have extra calls)
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertIn(
                "falcon_search_detections",
                tool_names,
                f"Expected falcon_search_detections in tool calls. Got: {tool_names}",
            )

            # Validate API call sequence (at least 2 calls: search + get details)
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                2,
                "Expected at least 2 API calls (search + details)",
            )

            # Find the successful GetQueriesAlertsV2 call with device.local_ip filter
            search_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "GetQueriesAlertsV2":
                    params = call[1].get("parameters", {})
                    filter_str = params.get("filter", "")
                    if "device.local_ip" in filter_str and "10.0.0.1" in filter_str:
                        search_call = call
                        break

            self.assertIsNotNone(
                search_call, "Expected GetQueriesAlertsV2 call with device.local_ip filter"
            )

            # Validate search API call parameters
            search_params = search_call[1].get("parameters", {})
            filter_str = search_params.get("filter", "")
            self.assertIn(
                "device.local_ip",
                filter_str,
                "Expected 'device.local_ip' filter in search API call",
            )
            self.assertIn(
                "10.0.0.1", filter_str, "Expected IP address filtering in search API call"
            )

            # Validate "highest" detection sorting (should sort by severity descending)
            sort_param = search_params.get("sort", "")
            if sort_param:  # Only validate if sorting is provided
                severity_sort_pattern = r"severity[.|]desc"
                self.assertTrue(
                    re.search(severity_sort_pattern, sort_param, re.IGNORECASE),
                    f"Expected severity descending sort for 'highest' detection. Got: {sort_param}",
                )

            # Find the PostEntitiesAlertsV2 call with detection-4
            details_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "PostEntitiesAlertsV2":
                    body = call[1].get("body", {})
                    if "detection-4" in body.get("composite_ids", []):
                        details_call = call
                        break

            self.assertIsNotNone(
                details_call, "Expected PostEntitiesAlertsV2 call with detection-4"
            )

            # Validate final result contains expected detection and excludes others
            self.assertIn("detection-4", result, "Expected detection-4 in final result")
            self.assertNotIn("detection-1", result, "Expected detection-1 NOT in final result")

        self.run_test_with_retries("test_get_highest_detection_for_ip", test_logic, assertions)

    def test_complex_fql_with_field_reference_table(self):
        """Verify the agent can use fields from the complete field reference table with complex FQL syntax."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetQueriesAlertsV2",
                    "validator": lambda kwargs: (
                        # Validate FQL filter uses device.product_type_desc field from field reference table
                        (filter_str := kwargs.get("parameters", {}).get("filter", "").lower())
                        and "device.product_type_desc" in filter_str
                        and "workstation" in filter_str
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {"resources": ["detection-5", "detection-6", "detection-7"]},
                    },
                },
                {
                    "operation": "PostEntitiesAlertsV2",
                    "validator": lambda kwargs: "detection-5"
                    in kwargs.get("body", {}).get("composite_ids", []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "detection-5",
                                    "composite_id": "detection-5",
                                    "status": "new",
                                    "severity": 65,
                                    "severity_name": "High",
                                    "confidence": 85,
                                    "description": "Malware detection on workstation.",
                                    "created_timestamp": "2024-01-20T12:00:00Z",
                                    "agent_id": "test-agent-005",
                                    "device": {
                                        "product_type_desc": "Workstation",
                                        "hostname": "WS-001",
                                    },
                                },
                                {
                                    "id": "detection-6",
                                    "composite_id": "detection-6",
                                    "status": "new",
                                    "severity": 70,
                                    "severity_name": "High",
                                    "confidence": 90,
                                    "description": "Suspicious activity on workstation.",
                                    "created_timestamp": "2024-01-20T11:45:00Z",
                                    "agent_id": "test-agent-006",
                                    "device": {
                                        "product_type_desc": "Workstation",
                                        "hostname": "WS-002",
                                    },
                                },
                                {
                                    "id": "detection-7",
                                    "composite_id": "detection-7",
                                    "status": "new",
                                    "severity": 75,
                                    "severity_name": "High",
                                    "confidence": 80,
                                    "description": "Threat detected on workstation endpoint.",
                                    "created_timestamp": "2024-01-20T11:30:00Z",
                                    "agent_id": "test-agent-007",
                                    "device": {
                                        "product_type_desc": "Workstation",
                                        "hostname": "WS-003",
                                    },
                                },
                            ]
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Find 5 endpoint detections from workstation devices only, sorted by most recent first."
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Validate tool execution - search_detections must be called (may have extra calls)
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            tool_names = [t["input"]["tool_name"] for t in tools]
            self.assertIn(
                "falcon_search_detections",
                tool_names,
                f"Expected falcon_search_detections in tool calls. Got: {tool_names}",
            )

            # Find the successful GetQueriesAlertsV2 call with correct filter
            search_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "GetQueriesAlertsV2":
                    params = call[1].get("parameters", {})
                    filter_str = params.get("filter", "").lower()
                    if (
                        "device.product_type_desc" in filter_str
                        and "workstation" in filter_str
                    ):
                        search_call = call
                        break

            self.assertIsNotNone(
                search_call,
                "Expected GetQueriesAlertsV2 call with device.product_type_desc filter",
            )

            # Validate search API call parameters
            search_params = search_call[1].get("parameters", {})

            # Validate complex FQL filter construction
            filter_str = search_params.get("filter", "").lower()

            # Should use device.product_type_desc field from the field reference table
            self.assertIn(
                "device.product_type_desc",
                filter_str,
                f"Expected 'device.product_type_desc' field from field reference table. Got filter: {filter_str}",
            )

            # Should filter for Workstation product type
            self.assertIn(
                "workstation",
                filter_str,
                f"Expected 'Workstation' value for product type filtering. Got filter: {filter_str}",
            )

            # Validate parameter separation (filter vs sort vs limit)
            # Model should use a reasonable limit for workstation query
            limit_used = search_params.get("limit")
            self.assertIsNotNone(
                limit_used,
                "Expected limit parameter to be properly separated from filter",
            )

            # Validate sort parameter properly separated from filter
            sort_param = search_params.get("sort", "")
            if sort_param:  # If sorting is used
                # Should NOT be in the filter string
                self.assertNotIn(
                    "sort",
                    filter_str,
                    f"Sort syntax should NOT be in filter parameter. Filter: {filter_str}, Sort: {sort_param}",
                )

                # Should use proper timestamp sorting for "most recent first"
                timestamp_sort_pattern = r"(timestamp|created_timestamp)[.|]desc"
                self.assertTrue(
                    re.search(timestamp_sort_pattern, sort_param, re.IGNORECASE),
                    f"Expected proper timestamp sorting for 'most recent first'. Got sort: {sort_param}",
                )

            # Validate final result contains expected detections
            expected_detections = ["detection-5", "detection-6", "detection-7"]
            for detection_id in expected_detections:
                self.assertIn(detection_id, result, f"Expected {detection_id} in final result")

        self.run_test_with_retries(
            "test_complex_fql_with_field_reference_table",
            test_logic,
            assertions,
        )


if __name__ == "__main__":
    unittest.main()
