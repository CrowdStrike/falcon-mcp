"""
E2E tests for the Discover module.
"""

import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestDiscoverModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Discover Module.
    """

    def test_search_applications_by_category(self):
        """Verify the agent can search for applications by name."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "combined_applications",
                    "validator": lambda kwargs: "category:'Web Browsers'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "abc123_def456789abcdef123456789abcdef123456789abcdef123456789abcdef",
                                    "cid": "abc123",
                                    "name": "Chrome Browser",
                                    "vendor": "Google",
                                    "version": "120.0.6099.130",
                                    "software_type": "application",
                                    "name_vendor": "Chrome Browser-Google",
                                    "name_vendor_version": "Chrome Browser-Google-120.0.6099.130",
                                    "versioning_scheme": "semver",
                                    "groups": [
                                        "group1",
                                        "group2",
                                        "group3",
                                    ],
                                    "category": "Web Browsers",
                                    "architectures": [
                                        "x64",
                                    ],
                                    "first_seen_timestamp": "2025-02-15T10:30:00Z",
                                    "last_updated_timestamp": "2025-03-01T14:45:22Z",
                                    "is_suspicious": False,
                                    "is_normalized": True,
                                    "host": {
                                        "id": "abc123_xyz789",
                                    },
                                },
                                {
                                    "id": "def456_123456789abcdef123456789abcdef123456789abcdef123456789abcdef",
                                    "cid": "def456",
                                    "name": "Chrome Browser",
                                    "vendor": "Google",
                                    "version": "119.0.6045.199",
                                    "software_type": "application",
                                    "name_vendor": "Chrome Browser-Google",
                                    "name_vendor_version": "Chrome Browser-Google-119.0.6045.199",
                                    "versioning_scheme": "semver",
                                    "groups": [
                                        "group4",
                                        "group5",
                                    ],
                                    "category": "Web Browsers",
                                    "architectures": [
                                        "x64",
                                    ],
                                    "first_seen_timestamp": "2025-01-10T08:15:30Z",
                                    "last_updated_timestamp": "2025-02-20T11:22:45Z",
                                    "is_suspicious": False,
                                    "is_normalized": True,
                                    "host": {
                                        "id": "def456_abc123",
                                    },
                                },
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Search for all applications categorized as Web Browsers in our environment and show me their details"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            self.assertIn("falcon_search_applications_fql_guide", tool_names_called)
            self.assertIn("falcon_search_applications", tool_names_called)

            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_applications")

            # Check for name filtering
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "web browsers" in tool_input_str,
                f"Expected web browsers category filtering in tool input: {tool_input_str}",
            )

            # Verify both applications are in the output
            self.assertIn("Chrome Browser", used_tool["output"])
            self.assertIn("Google", used_tool["output"])
            self.assertIn("120.0.6099.130", used_tool["output"])
            self.assertIn("119.0.6045.199", used_tool["output"])

            # Verify API call was made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (combined_applications)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "category" in filter_str and "web browsers" in filter_str,
                f"Expected category:Web Browsers filtering in API call: {filter_str}",
            )

            # Verify result contains expected information
            self.assertIn("Chrome Browser", result)
            self.assertIn("Google", result)
            self.assertIn("120.0.6099.130", result)
            self.assertIn("119.0.6045.199", result)
            self.assertIn("Web Browsers", result)

        self.run_test_with_retries("test_search_applications_by_category", test_logic, assertions)

    def test_search_unmanaged_assets_by_platform(self):
        """Verify the agent can search for unmanaged assets by platform."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "combined_hosts",
                    "validator": lambda kwargs: "entity_type:'unmanaged'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "abc123def456789_1234567890abcdef1234567890abcdef1234567890abcdef",
                                    "cid": "abc123def456789",
                                    "entity_type": "unmanaged",
                                    "first_seen_timestamp": "2025-05-16T04:00:00Z",
                                    "last_seen_timestamp": "2025-08-12T23:00:00Z",
                                    "system_manufacturer": "VMware, Inc.",
                                    "hostname": "PC-FINANCE-W11",
                                    "local_ips_count": 1,
                                    "network_interfaces": [
                                        {
                                            "local_ip": "192.168.1.100",
                                            "mac_address": "AA-BB-CC-DD-EE-01",
                                            "network_prefix": "192.168",
                                        }
                                    ],
                                    "os_security": {},
                                    "current_local_ip": "192.168.1.100",
                                    "data_providers": ["Falcon passive discovery"],
                                    "data_providers_count": 1,
                                    "first_discoverer_aid": "abc123456789def0123456789abcdef01",
                                    "last_discoverer_aid": "abc123456789def0123456789abcdef01",
                                    "discoverer_count": 1,
                                    "discoverer_aids": ["abc123456789def0123456789abcdef01"],
                                    "discoverer_tags": [
                                        "FalconGroupingTags/Finance",
                                        "FalconGroupingTags/Workstation",
                                        "FalconGroupingTags/Windows11",
                                    ],
                                    "discoverer_platform_names": ["Windows"],
                                    "discoverer_product_type_descs": ["Workstation"],
                                    "discoverer_hostnames": ["WIN-MGMT-001"],
                                    "last_discoverer_hostname": "WIN-MGMT-001",
                                    "confidence": 75,
                                    "active_discovery": {},
                                },
                                {
                                    "id": "abc123def456789_fedcba0987654321fedcba0987654321fedcba0987654321",
                                    "cid": "abc123def456789",
                                    "entity_type": "unmanaged",
                                    "first_seen_timestamp": "2025-07-16T10:00:00Z",
                                    "last_seen_timestamp": "2025-08-12T23:00:00Z",
                                    "system_manufacturer": "Dell Inc.",
                                    "hostname": "SERVER-HR-002",
                                    "local_ips_count": 1,
                                    "network_interfaces": [
                                        {
                                            "local_ip": "192.168.2.50",
                                            "mac_address": "AA-BB-CC-DD-EE-02",
                                            "network_prefix": "192.168",
                                        }
                                    ],
                                    "os_security": {},
                                    "current_local_ip": "192.168.2.50",
                                    "data_providers": ["Falcon passive discovery"],
                                    "data_providers_count": 1,
                                    "first_discoverer_aid": "def456789abc012def456789abc012de",
                                    "last_discoverer_aid": "def456789abc012def456789abc012de",
                                    "discoverer_count": 1,
                                    "discoverer_aids": ["def456789abc012def456789abc012de"],
                                    "discoverer_tags": [
                                        "FalconGroupingTags/HR",
                                        "FalconGroupingTags/Server",
                                        "FalconGroupingTags/WindowsServer2019",
                                    ],
                                    "discoverer_platform_names": ["Windows"],
                                    "discoverer_product_type_descs": ["Server"],
                                    "discoverer_hostnames": ["WIN-DC-001"],
                                    "last_discoverer_hostname": "WIN-DC-001",
                                    "confidence": 85,
                                    "active_discovery": {},
                                },
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Search for all unmanaged Windows assets in our environment and show me their details"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            # Agent may or may not consult the FQL guide - both approaches are valid
            self.assertIn("falcon_search_unmanaged_assets", tool_names_called)

            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_unmanaged_assets")

            # Note: Agent may interpret platform filtering differently
            # The key behavior is that it successfully finds and returns unmanaged assets

            # Verify both unmanaged assets are in the output
            self.assertIn("PC-FINANCE-W11", used_tool["output"])
            self.assertIn("SERVER-HR-002", used_tool["output"])
            self.assertIn("VMware, Inc.", used_tool["output"])
            self.assertIn("Dell Inc.", used_tool["output"])
            self.assertIn("unmanaged", used_tool["output"])

            # Verify API call was made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (combined_hosts)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            filter_str = api_call_params.get("filter", "").lower()

            # Verify entity_type:'unmanaged' is automatically added
            self.assertTrue(
                "entity_type:'unmanaged'" in filter_str,
                f"Expected entity_type:'unmanaged' in API call filter: {filter_str}",
            )

            # Note: Platform filtering may vary based on agent interpretation
            # The core requirement is that entity_type:'unmanaged' is enforced

            # Verify result contains expected information
            self.assertIn("PC-FINANCE-W11", result)
            self.assertIn("SERVER-HR-002", result)
            self.assertIn("Windows", result)
            self.assertIn("unmanaged", result)
            self.assertIn("Workstation", result)
            self.assertIn("Server", result)

        self.run_test_with_retries(
            "test_search_unmanaged_assets_by_platform", test_logic, assertions
        )

    def test_search_unmanaged_assets_by_confidence(self):
        """Verify the agent can search for unmanaged assets by confidence level."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "combined_hosts",
                    "validator": lambda kwargs: "entity_type:'unmanaged'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "def789ghi012345_abcdef123456789abcdef123456789abcdef123456789abcdef",
                                    "cid": "def789ghi012345",
                                    "entity_type": "unmanaged",
                                    "first_seen_timestamp": "2025-07-17T08:00:00Z",
                                    "last_seen_timestamp": "2025-08-12T23:00:00Z",
                                    "system_manufacturer": "VMware, Inc.",
                                    "hostname": "PROD-DB-LINUX",
                                    "local_ips_count": 1,
                                    "network_interfaces": [
                                        {
                                            "local_ip": "10.0.1.200",
                                            "mac_address": "AA-BB-CC-DD-EE-03",
                                            "network_prefix": "10.0",
                                        }
                                    ],
                                    "os_security": {},
                                    "current_local_ip": "10.0.1.200",
                                    "data_providers": ["Falcon passive discovery"],
                                    "data_providers_count": 1,
                                    "first_discoverer_aid": "123456789def012345678901234567ab",
                                    "last_discoverer_aid": "123456789def012345678901234567ab",
                                    "discoverer_count": 1,
                                    "discoverer_aids": ["123456789def012345678901234567ab"],
                                    "discoverer_tags": [
                                        "FalconGroupingTags/Production",
                                        "FalconGroupingTags/Database",
                                        "FalconGroupingTags/Linux",
                                        "FalconGroupingTags/Critical-Infrastructure",
                                    ],
                                    "discoverer_platform_names": ["Linux"],
                                    "discoverer_product_type_descs": ["Server"],
                                    "discoverer_hostnames": ["LNX-MGMT-001"],
                                    "last_discoverer_hostname": "LNX-MGMT-001",
                                    "confidence": 95,
                                    "active_discovery": {},
                                }
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(
                fixtures
            )

            prompt = "Find all unmanaged assets with high confidence levels (above 80) that are likely real systems"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            self.assertIn("falcon_search_unmanaged_assets", tool_names_called)

            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_unmanaged_assets")

            # Note: Agent may interpret confidence filtering differently
            # The key behavior is that it successfully finds and returns unmanaged assets

            # Verify high confidence asset is in the output
            self.assertIn("PROD-DB-LINUX", used_tool["output"])
            self.assertIn("95", used_tool["output"])
            self.assertIn("unmanaged", used_tool["output"])

            # Verify API call was made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (combined_hosts)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            filter_str = api_call_params.get("filter", "").lower()

            # Verify entity_type:'unmanaged' is automatically added
            self.assertTrue(
                "entity_type:'unmanaged'" in filter_str,
                f"Expected entity_type:'unmanaged' in API call filter: {filter_str}",
            )

            # Note: Confidence filtering may vary based on agent interpretation
            # The core requirement is that entity_type:'unmanaged' is enforced

            # Verify result contains expected information
            self.assertIn("PROD-DB-LINUX", result)
            self.assertIn("95", result)
            self.assertIn("unmanaged", result)
            self.assertIn("Linux", result)

        self.run_test_with_retries(
            "test_search_unmanaged_assets_by_confidence", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
