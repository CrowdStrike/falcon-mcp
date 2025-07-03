"""
E2E tests for the Hosts module.
"""
import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestHostsModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Hosts Module.
    """

    def test_search_linux_servers(self):
        """Verify the agent can search for Linux servers and retrieve their details."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDevicesByFilter",
                    "validator": lambda kwargs: "linux" in kwargs.get('parameters', {}).get('filter', '').lower() and "server" in kwargs.get('parameters', {}).get('filter', '').lower(),
                    "response": {"status_code": 200, "body": {"resources": ["host-001", "host-002", "host-003"]}}
                },
                {
                    "operation": "PostDeviceDetailsV2",
                    "validator": lambda kwargs: "host-001" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "device_id": "host-001",
                                    "hostname": "linux-server-01",
                                    "platform_name": "Linux",
                                    "product_type_desc": "Server",
                                    "os_version": "Ubuntu 20.04.3 LTS",
                                    "agent_version": "7.26.17905.0",
                                    "status": "normal",
                                    "last_seen": "2024-01-20T10:00:00Z",
                                    "first_seen": "2024-01-15T08:30:00Z",
                                    "external_ip": "203.0.113.10",
                                    "local_ip": "192.168.1.10",
                                    "machine_domain": "company.local",
                                    "system_manufacturer": "Dell Inc.",
                                    "system_product_name": "PowerEdge R740"
                                },
                                {
                                    "device_id": "host-002",
                                    "hostname": "linux-server-02",
                                    "platform_name": "Linux",
                                    "product_type_desc": "Server",
                                    "os_version": "CentOS Linux 8.4",
                                    "agent_version": "7.26.17905.0",
                                    "status": "normal",
                                    "last_seen": "2024-01-20T09:45:00Z",
                                    "first_seen": "2024-01-10T14:20:00Z",
                                    "external_ip": "203.0.113.11",
                                    "local_ip": "192.168.1.11",
                                    "machine_domain": "company.local",
                                    "system_manufacturer": "HPE",
                                    "system_product_name": "ProLiant DL380"
                                },
                                {
                                    "device_id": "host-003",
                                    "hostname": "linux-server-03",
                                    "platform_name": "Linux",
                                    "product_type_desc": "Server",
                                    "os_version": "Red Hat Enterprise Linux 8.5",
                                    "agent_version": "7.25.16803.0",
                                    "status": "normal",
                                    "last_seen": "2024-01-20T09:30:00Z",
                                    "first_seen": "2024-01-12T11:15:00Z",
                                    "external_ip": "203.0.113.12",
                                    "local_ip": "192.168.1.12",
                                    "machine_domain": "company.local",
                                    "system_manufacturer": "Lenovo",
                                    "system_product_name": "ThinkSystem SR650"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all Linux servers in our environment and show me their hostnames, IP addresses, and agent versions"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_hosts")

            # Check for Linux and server filtering
            tool_input_str = json.dumps(used_tool['input']['tool_input']).lower()
            self.assertTrue(
                "linux" in tool_input_str and "server" in tool_input_str,
                f"Expected Linux server filtering in tool input: {tool_input_str}"
            )

            # Verify all three hosts are in the output
            self.assertIn("linux-server-01", used_tool['output'])
            self.assertIn("linux-server-02", used_tool['output'])
            self.assertIn("linux-server-03", used_tool['output'])

            # Verify API calls were made correctly
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")

            # Check first API call (QueryDevicesByFilter)
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            filter_str = api_call_1_params.get('filter', '').lower()
            self.assertTrue(
                "linux" in filter_str and "server" in filter_str,
                f"Expected Linux server filtering in API call: {filter_str}"
            )

            # Check second API call (PostDeviceDetailsV2)
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            expected_ids = ["host-001", "host-002", "host-003"]
            self.assertEqual(api_call_2_body.get('ids'), expected_ids)

            # Verify result contains expected information
            self.assertIn("linux-server-01", result)
            self.assertIn("linux-server-02", result)
            self.assertIn("linux-server-03", result)
            self.assertIn("192.168.1.", result)  # Should contain IP addresses
            self.assertIn("7.26.", result)  # Should contain agent versions

        self.run_test_with_retries(
            "test_search_linux_servers",
            test_logic,
            assertions
        )

    def test_get_specific_host_details(self):
        """Verify the agent can get details for specific host IDs."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "PostDeviceDetailsV2",
                    "validator": lambda kwargs: "host-windows-001" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [{
                                "device_id": "host-windows-001",
                                "hostname": "DESKTOP-WIN10-01",
                                "platform_name": "Windows",
                                "product_type_desc": "Workstation",
                                "os_version": "Windows 10 Enterprise",
                                "major_version": "10",
                                "minor_version": "0",
                                "agent_version": "7.26.17905.0",
                                "status": "normal",
                                "last_seen": "2024-01-20T11:15:00Z",
                                "first_seen": "2024-01-18T09:00:00Z",
                                "external_ip": "203.0.113.20",
                                "local_ip": "192.168.1.20",
                                "mac_address": "00:50:56:C0:00:08",
                                "machine_domain": "CORPORATE",
                                "system_manufacturer": "VMware, Inc.",
                                "system_product_name": "VMware Virtual Platform",
                                "bios_manufacturer": "Phoenix Technologies LTD",
                                "bios_version": "6.00",
                                "serial_number": "VMware-56-4d-xx-xx-xx-xx",
                                "reduced_functionality_mode": "no",
                                "filesystem_containment_status": "normal"
                            }]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Get detailed information for host ID 'host-windows-001', including its hostname, platform, and containment status"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_get_host_details")

            # Check that the specific host ID was used
            tool_input = used_tool['input']['tool_input']
            self.assertIn("host-windows-001", json.dumps(tool_input))

            # Verify host details are in the output
            self.assertIn("DESKTOP-WIN10-01", used_tool['output'])
            self.assertIn("Windows", used_tool['output'])
            self.assertIn("host-windows-001", used_tool['output'])

            # Verify API call was made correctly
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected 1 API call")

            # Check API call (PostDeviceDetailsV2)
            api_call_body = self._mock_api_instance.command.call_args_list[0][1].get('body', {})
            self.assertIn("host-windows-001", api_call_body.get('ids', []))

            # Verify result contains expected information
            self.assertIn("DESKTOP-WIN10-01", result)
            self.assertIn("Windows", result)
            self.assertIn("normal", result)  # Status and containment status
            self.assertIn("192.168.1.20", result)  # Local IP

        self.run_test_with_retries(
            "test_get_specific_host_details",
            test_logic,
            assertions
        )

    def test_search_azure_cloud_hosts(self):
        """Verify the agent can search for cloud hosts with complex filtering."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDevicesByFilter",
                    "validator": lambda kwargs: "azure" in kwargs.get('parameters', {}).get('filter', '').lower(),
                    "response": {"status_code": 200, "body": {"resources": ["azure-host-001"]}}
                },
                {
                    "operation": "PostDeviceDetailsV2",
                    "validator": lambda kwargs: "azure-host-001" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [{
                                "device_id": "azure-host-001",
                                "hostname": "azure-vm-debian",
                                "platform_name": "Linux",
                                "product_type_desc": "Server",
                                "os_version": "Debian GNU 12",
                                "kernel_version": "6.11.0-1015-azure",
                                "agent_version": "7.26.17905.0",
                                "status": "normal",
                                "last_seen": "2024-01-20T12:00:00Z",
                                "first_seen": "2024-01-19T10:30:00Z",
                                "external_ip": "20.45.123.45",
                                "connection_ip": "172.18.0.2",
                                "default_gateway_ip": "172.18.0.1",
                                "service_provider": "AZURE",
                                "service_provider_account_id": "99841e6a-b123-4567-8901-123456789abc",
                                "instance_id": "f9d3cef9-0123-4567-8901-123456789def",
                                "system_manufacturer": "Microsoft Corporation",
                                "system_product_name": "Virtual Machine",
                                "deployment_type": "DaemonSet",
                                "linux_sensor_mode": "User Mode",
                                "reduced_functionality_mode": "yes",
                                "k8s_cluster_id": "ecbb9795-9123-4567-8901-123456789ghi",
                                "tags": ["SensorGroupingTags/daemonset"]
                            }]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find Azure cloud hosts and show their deployment details including Kubernetes cluster information"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Find a search hosts tool call (may not be the last one)
            search_tool = None
            for tool in tools:
                if tool['input']['tool_name'] == "falcon_search_hosts":
                    search_tool = tool
                    break

            self.assertIsNotNone(search_tool, "Expected at least one falcon_search_hosts tool call")

            # Check for Azure filtering in any tool call
            found_azure_filtering = False
            for tool in tools:
                tool_input_str = json.dumps(tool['input']['tool_input']).lower()
                if "azure" in tool_input_str:
                    found_azure_filtering = True
                    break

            self.assertTrue(found_azure_filtering, f"Expected Azure filtering in tool inputs")

            # Verify Azure host is in the search tool output
            self.assertIn("azure-vm-debian", search_tool['output'])
            self.assertIn("AZURE", search_tool['output'])

            # Verify API calls were made correctly
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")

            # Check that we have QueryDevicesByFilter call with Azure filtering
            found_azure_query = False
            found_details_call = False

            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "QueryDevicesByFilter":
                    filter_str = call[1].get('parameters', {}).get('filter', '').lower()
                    if "azure" in filter_str:
                        found_azure_query = True
                elif call[0][0] == "PostDeviceDetailsV2":
                    if "azure-host-001" in call[1].get('body', {}).get('ids', []):
                        found_details_call = True

            self.assertTrue(found_azure_query, "Expected QueryDevicesByFilter call with Azure filtering")
            self.assertTrue(found_details_call, "Expected PostDeviceDetailsV2 call with azure-host-001")

            # Verify result contains expected Azure and Kubernetes information (more flexible matching)
            result_lower = result.lower()
            self.assertIn("azure-vm-debian", result_lower)
            self.assertIn("azure", result_lower)
            self.assertIn("daemonset", result_lower)
            # Check for Kubernetes info (could be "k8s" or "kubernetes")
            self.assertTrue(
                "k8s" in result_lower or "kubernetes" in result_lower,
                f"Expected Kubernetes cluster info in result: {result_lower[:500]}..."
            )

        self.run_test_with_retries(
            "test_search_azure_cloud_hosts",
            test_logic,
            assertions
        )


if __name__ == '__main__':
    unittest.main()
