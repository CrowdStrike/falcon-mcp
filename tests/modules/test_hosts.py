"""
Tests for the Hosts module.
"""

import unittest

from mcp.types import ToolAnnotations

from falcon_mcp.modules.hosts import HostsModule
from falcon_mcp.resources.hosts import SEARCH_HOSTS_FQL_DOCUMENTATION
from tests.modules.utils.test_modules import TestModules


class TestHostsModule(TestModules):
    """Test cases for the Hosts module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(HostsModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_search_hosts",
            "falcon_get_host_details",
            "falcon_manage_host_grouping_tags",
        ]
        self.assert_tools_registered(expected_tools)

    def test_manage_host_grouping_tags_annotations(self):
        """The tag tool is mutating but safe to retry (set semantics)."""
        self.module.register_tools(self.mock_server)
        self.assert_tool_annotations(
            "falcon_manage_host_grouping_tags",
            ToolAnnotations(
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=True,
            ),
        )

    def test_register_resources(self):
        """Test registering resources with the server."""
        expected_resources = [
            "falcon_search_hosts_fql_guide",
        ]
        self.assert_resources_registered(expected_resources)

    def test_search_hosts(self):
        """Test searching for hosts."""
        # Setup mock responses for both API calls
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["device1", "device2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [
                {"device_id": "device1", "hostname": "host1", "platform_name": "Windows"},
                {"device_id": "device2", "hostname": "host2", "platform_name": "Windows"},
            ]},
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'", limit=50)

        # Verify first call uses the new base method with correct parameters
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryDevicesByFilter")  # operation name
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Windows'")
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)

        # Verify second call for device details
        second_call = self.mock_client.command.call_args_list[1]
        self.assertEqual(second_call[0][0], "PostDeviceDetailsV2")
        self.assertEqual(second_call[1]["body"]["ids"], ["device1", "device2"])

        # Verify result envelope
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["device_id"], "device1")
        self.assertEqual(result["results"][1]["device_id"], "device2")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_hosts_with_details(self):
        """Test searching for hosts with details."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["device1", "device2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "device1",
                        "hostname": "TEST-HOST-1",
                        "platform_name": "Windows",
                    },
                    {
                        "device_id": "device2",
                        "hostname": "TEST-HOST-2",
                        "platform_name": "Linux",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'", limit=50)

        # Verify client commands were called correctly
        self.assertEqual(self.mock_client.command.call_count, 2)

        # Check that the first call was to QueryDevicesByFilter with the right filter and limit
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "QueryDevicesByFilter")
        self.assertEqual(
            first_call[1]["parameters"]["filter"], "platform_name:'Windows'"
        )
        self.assertEqual(first_call[1]["parameters"]["limit"], 50)
        self.mock_client.command.assert_any_call(
            "PostDeviceDetailsV2", body={"ids": ["device1", "device2"]}
        )

        # Verify result envelope
        self.assertIn("results", result)
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["device_id"], "device1")
        self.assertEqual(result["results"][1]["device_id"], "device2")
        self.assertEqual(result["pagination"]["total"], 2)

    def test_search_hosts_error(self):
        """Test searching for hosts with a filter error returns the FQL guide."""
        # Setup mock response with error
        mock_response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Invalid filter"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="invalid_filter")

        # Verify result contains the error wrapped alongside the FQL guide and hint
        self.assertIsInstance(result, dict)
        self.assertIn("results", result)
        self.assertIn("error", result["results"][0])
        self.assertIn("fql_guide", result)
        self.assertEqual(result["fql_guide"], SEARCH_HOSTS_FQL_DOCUMENTATION)
        self.assertIn("hint", result)
        self.assertEqual(result["filter_used"], "invalid_filter")

    def test_search_hosts_no_results(self):
        """Test searching for hosts with no results."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": [], "meta": {"pagination": {"offset": 0, "limit": 100, "total": 0}}}}
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="hostname:'NONEXISTENT'")

        # Verify result is empty envelope
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("pagination", result)
        # Only one API call should be made (QueryDevicesByFilter)
        self.assertEqual(self.mock_client.command.call_count, 1)

    def test_search_hosts_with_all_parameters(self):
        """Test searching for hosts with all parameters."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call search_hosts with all parameters
        result = self.module.search_hosts(
            filter="platform_name:'Linux'", limit=25, offset=10, sort="hostname.desc"
        )

        # Verify API call with all parameters
        self.mock_client.command.assert_called_once_with(
            "QueryDevicesByFilter",
            parameters={
                "filter": "platform_name:'Linux'",
                "limit": 25,
                "offset": 10,
                "sort": "hostname.desc",
            },
        )

        # Verify result
        self.assertIsInstance(result, dict)
        self.assertEqual(result["results"], [])
        self.assertIn("pagination", result)

    def test_search_hosts_reorders_to_match_sorted_ids(self):
        """When PostDeviceDetailsV2 returns devices out of order, the result is
        reordered to match the sorted ID order from QueryDevicesByFilter.

        Live API validated: the details endpoint preserves order today, so this
        guards against regressions and future endpoint behavior changes. Entities
        carry their ID in the ``device_id`` field.
        """
        query_response = {
            "status_code": 200,
            "body": {"resources": ["device2", "device1"]},
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"device_id": "device1", "hostname": "alpha"},
                    {"device_id": "device2", "hostname": "bravo"},
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        result = self.module.search_hosts(sort="last_seen.desc")

        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["device_id"], "device2")
        self.assertEqual(result["results"][1]["device_id"], "device1")

    def test_get_host_details(self):
        """Test getting host details."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "device1",
                        "hostname": "TEST-HOST-1",
                        "platform_name": "Windows",
                    }
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["device1"])

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostDeviceDetailsV2", body={"ids": ["device1"]}
        )

        # Verify result
        expected_result = [
            {
                "device_id": "device1",
                "hostname": "TEST-HOST-1",
                "platform_name": "Windows",
            }
        ]
        self.assertEqual(result, expected_result)

    def test_get_host_details_multiple_ids(self):
        """Test getting host details for multiple IDs."""
        # Setup mock response
        mock_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "device1",
                        "hostname": "TEST-HOST-1",
                        "platform_name": "Windows",
                    },
                    {
                        "device_id": "device2",
                        "hostname": "TEST-HOST-2",
                        "platform_name": "Linux",
                    },
                ]
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["device1", "device2"])

        # Verify client command was called correctly
        self.mock_client.command.assert_called_once_with(
            "PostDeviceDetailsV2", body={"ids": ["device1", "device2"]}
        )

        # Verify result
        expected_result = [
            {
                "device_id": "device1",
                "hostname": "TEST-HOST-1",
                "platform_name": "Windows",
            },
            {
                "device_id": "device2",
                "hostname": "TEST-HOST-2",
                "platform_name": "Linux",
            },
        ]
        self.assertEqual(result, expected_result)

    def test_get_host_details_not_found(self):
        """Test getting host details for non-existent host."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": []}}
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["nonexistent"])

        # For empty resources, handle_api_response returns the default_result (empty list)
        self.assertEqual(result, [])

    def test_get_host_details_error(self):
        """Test getting host details with API error."""
        # Setup mock response with error
        mock_response = {
            "status_code": 404,
            "body": {"errors": [{"message": "Device not found"}]},
        }
        self.mock_client.command.return_value = mock_response

        # Call get_host_details
        result = self.module.get_host_details(["invalid-id"])

        # Verify result contains error
        self.assertIsInstance(result, dict)
        self.assertIn("error", result)
        self.assertIn("details", result)

    def test_get_host_details_empty_list(self):
        """Test getting host details with empty ID list."""
        # Call get_host_details with empty list
        result = self.module.get_host_details([])

        # Should return empty list without making API call
        self.assertEqual(result, [])
        self.mock_client.command.assert_not_called()

    def test_search_hosts_windows_platform(self):
        """Test searching for Windows hosts."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["win-host-1", "win-host-2"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 2}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "win-host-1",
                        "platform_name": "Windows",
                        "hostname": "WIN-01",
                    },
                    {
                        "device_id": "win-host-2",
                        "platform_name": "Windows",
                        "hostname": "WIN-02",
                    },
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Windows'")

        # Verify result envelope
        self.assertEqual(len(result["results"]), 2)
        self.assertEqual(result["results"][0]["platform_name"], "Windows")
        self.assertEqual(result["results"][1]["platform_name"], "Windows")

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(
            first_call[1]["parameters"]["filter"], "platform_name:'Windows'"
        )

    def test_search_hosts_linux_platform(self):
        """Test searching for Linux hosts."""
        # Setup mock responses
        query_response = {
            "status_code": 200,
            "body": {
                "resources": ["linux-host-1"],
                "meta": {"pagination": {"offset": 0, "limit": 100, "total": 1}},
            },
        }
        details_response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {
                        "device_id": "linux-host-1",
                        "platform_name": "Linux",
                        "hostname": "LINUX-01",
                    }
                ]
            },
        }
        self.mock_client.command.side_effect = [query_response, details_response]

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Linux'")

        # Verify result envelope
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["platform_name"], "Linux")

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Linux'")

    def test_search_hosts_mac_platform_no_results(self):
        """Test searching for Mac hosts with no results."""
        # Setup mock response with empty resources
        mock_response = {"status_code": 200, "body": {"resources": [], "meta": {"pagination": {"offset": 0, "limit": 100, "total": 0}}}}
        self.mock_client.command.return_value = mock_response

        # Call search_hosts
        result = self.module.search_hosts(filter="platform_name:'Mac'")

        # Verify result envelope
        self.assertEqual(len(result["results"]), 0)

        # Verify filter was applied correctly
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[1]["parameters"]["filter"], "platform_name:'Mac'")

    # ----------------------------------------------------------------- #
    # manage_host_grouping_tags
    # ----------------------------------------------------------------- #
    def _tag_success_response(self):
        return {
            "status_code": 202,
            "body": {"resources": [{"device_id": "device1", "updated": True}]},
        }

    def test_manage_host_grouping_tags_add(self):
        """Add sends the Uber-class body shape: action/device_ids/tags."""
        self.mock_client.command.return_value = self._tag_success_response()

        result = self.module.manage_host_grouping_tags(
            ids=["device1"],
            action="add",
            tags=["FalconGroupingTags/Quarantined"],
        )

        self.mock_client.command.assert_called_once_with(
            "UpdateDeviceTags",
            body={
                "action": "add",
                "device_ids": ["device1"],
                "tags": ["FalconGroupingTags/Quarantined"],
            },
        )
        self.assertEqual(result, [{"device_id": "device1", "updated": True}])

    def test_manage_host_grouping_tags_remove(self):
        """Remove passes action through unchanged."""
        self.mock_client.command.return_value = self._tag_success_response()

        self.module.manage_host_grouping_tags(
            ids=["device1", "device2"],
            action="remove",
            tags=["FalconGroupingTags/Quarantined"],
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["action"], "remove")
        self.assertEqual(body["device_ids"], ["device1", "device2"])

    def test_manage_host_grouping_tags_normalizes_bare_tags(self):
        """Bare tag names get the FalconGroupingTags/ prefix added."""
        self.mock_client.command.return_value = self._tag_success_response()

        self.module.manage_host_grouping_tags(
            ids=["device1"],
            action="add",
            tags=["Quarantined", "FalconGroupingTags/IR-2026-07"],
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(
            body["tags"],
            ["FalconGroupingTags/Quarantined", "FalconGroupingTags/IR-2026-07"],
        )

    def test_manage_host_grouping_tags_strips_whitespace(self):
        """Surrounding whitespace is trimmed before prefixing."""
        self.mock_client.command.return_value = self._tag_success_response()

        self.module.manage_host_grouping_tags(
            ids=["device1"], action="add", tags=["  Quarantined  "]
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(body["tags"], ["FalconGroupingTags/Quarantined"])

    def test_manage_host_grouping_tags_rejects_sensor_tags(self):
        """Sensor grouping tags are read-only and must not be silently re-prefixed."""
        result = self.module.manage_host_grouping_tags(
            ids=["device1"],
            action="add",
            tags=["SensorGroupingTags/Production"],
        )

        self.assertIsInstance(result, list)
        self.assertIn("error", result[0])
        self.assertIn("SensorGroupingTags/Production", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_miscased_sensor_tags(self):
        """The sensor guard is case-insensitive.

        Matching the prefix exactly would let 'sensorgroupingtags/x' through to be
        prefixed into 'FalconGroupingTags/sensorgroupingtags/x' — a tag the API
        accepts, so the junk lands on the host instead of erroring.
        """
        for spelling in (
            "sensorgroupingtags/Production",
            "SENSORGROUPINGTAGS/Production",
            "SensorGroupingtags/Production",
        ):
            with self.subTest(spelling=spelling):
                self.mock_client.command.reset_mock()
                result = self.module.manage_host_grouping_tags(
                    ids=["device1"], action="add", tags=[spelling]
                )

                self.assertIn("error", result[0])
                self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_canonicalizes_miscased_prefix(self):
        """A miscased grouping prefix is rewritten to canonical casing.

        The API compares the prefix exactly and 400s on anything else, so passing
        it through unchanged fails and blindly prepending doubles it up. Only
        rewriting the prefix reaches the tag the caller meant. The tag name after
        the prefix keeps its casing, which the API is case-sensitive about.
        """
        self.mock_client.command.return_value = self._tag_success_response()

        self.module.manage_host_grouping_tags(
            ids=["device1"],
            action="add",
            tags=[
                "falcongroupingtags/Quarantined",
                "FALCONGROUPINGTAGS/IR-2026-07",
                "FalconGroupingTags/Already-Fine",
            ],
        )

        body = self.mock_client.command.call_args[1]["body"]
        self.assertEqual(
            body["tags"],
            [
                "FalconGroupingTags/Quarantined",
                "FalconGroupingTags/IR-2026-07",
                "FalconGroupingTags/Already-Fine",
            ],
        )

    def test_manage_host_grouping_tags_rejects_too_many_ids(self):
        """Over 5000 device IDs is a 400 from the API; catch it before the call."""
        result = self.module.manage_host_grouping_tags(
            ids=[f"device{i}" for i in range(5001)],
            action="add",
            tags=["Quarantined"],
        )

        self.assertIn("error", result[0])
        self.assertIn("5000", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_too_many_tags(self):
        """Over 50 tags in one call returns an opaque 500 with nothing applied."""
        result = self.module.manage_host_grouping_tags(
            ids=["device1"],
            action="add",
            tags=[f"bulk-{i}" for i in range(51)],
        )

        self.assertIn("error", result[0])
        self.assertIn("50", result[0]["error"])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_invalid_action(self):
        """Only add and remove are valid actions."""
        result = self.module.manage_host_grouping_tags(
            ids=["device1"], action="update", tags=["Quarantined"]
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_empty_ids(self):
        """An empty id list would PATCH nothing; fail loudly instead."""
        result = self.module.manage_host_grouping_tags(
            ids=[], action="add", tags=["Quarantined"]
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_empty_tags(self):
        """An empty tag list would report success while changing nothing."""
        result = self.module.manage_host_grouping_tags(
            ids=["device1"], action="add", tags=[]
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_rejects_blank_tag(self):
        """A whitespace-only tag normalizes to a bare prefix; reject it."""
        result = self.module.manage_host_grouping_tags(
            ids=["device1"], action="add", tags=["   "]
        )

        self.assertIn("error", result[0])
        self.mock_client.command.assert_not_called()

    def test_manage_host_grouping_tags_api_error(self):
        """API failures come back in the module's standard error shape."""
        self.mock_client.command.return_value = {
            "status_code": 403,
            "body": {"errors": [{"message": "access denied"}]},
        }

        result = self.module.manage_host_grouping_tags(
            ids=["device1"], action="add", tags=["Quarantined"]
        )

        self.assertIn("error", result[0])
        self.assertIn("required_scopes", result[0])


if __name__ == "__main__":
    unittest.main()
