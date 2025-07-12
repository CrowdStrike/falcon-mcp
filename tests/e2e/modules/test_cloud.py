"""
E2E tests for the Cloud module.
"""

import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestCloudModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Cloud Module.
    """

    def test_search_kubernetes_containers_running(self):
        """Verify the agent can search for kubernetes containers that are running."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "ReadContainerCombined",
                    "validator": lambda kwargs: "running_status"
                    in kwargs.get("parameters", {}).get("filter", "").lower(),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "container_id": "container-001",
                                    "agents": [
                                        {
                                            "aid": "558ce490595748d6a67b16969797d655",
                                            "build": "0000",
                                            "type": "Falcon sensor for linux",
                                        },
                                    ],
                                    "cloud_name": "AWS",
                                    "cloud_account_id": "00001",
                                    "cloud_region": "ca-central-1",
                                    "cluster_name": "production",
                                    "first_seen": "2025-05-27T03:04:10Z",
                                    "image_registry": "docker.amazonaws.com",
                                    "image_repository": "myservice",
                                    "image_tag": "v1.0.0",
                                    "image_vulnerability_count": 361,
                                    "last_seen": "2025-07-13T19:53:07Z",
                                    "container_name": "myservice",
                                    "namespace": "default",
                                    "running_status": True,
                                },
                                {
                                    "container_id": "container-002",
                                    "agents": [
                                        {
                                            "aid": "523c3113363845d4a6da493a29caa924",
                                            "build": "0000",
                                            "type": "Falcon sensor for linux",
                                        },
                                    ],
                                    "cloud_name": "AWS",
                                    "cloud_account_id": "00001",
                                    "cloud_region": "us-1",
                                    "cluster_name": "production",
                                    "first_seen": "2025-06-27T03:04:10Z",
                                    "image_registry": "docker.amazonaws.com",
                                    "image_repository": "myservice",
                                    "image_tag": "v1.0.0",
                                    "image_vulnerability_count": 361,
                                    "last_seen": "2025-07-13T19:53:07Z",
                                    "container_name": "myservice",
                                    "namespace": "default",
                                    "running_status": True,
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Find all kubernetes containers that are running"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_kubernetes_containers"
            )

            # Check for the filter for running status
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "running_status" in tool_input_str,
                f"Expected running status filtering in tool input: {tool_input_str}",
            )

            self.assertIn("container-001", used_tool["output"])
            self.assertIn("container-002", used_tool["output"])

            # Verify API calls were made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (ReadContainerCombined)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "running_status" in filter_str,
                f"Expected running_status filtering in API call: {filter_str}",
            )

            # Verify result contains expected information
            self.assertIn("container-001", result)
            self.assertIn("container-002", result)

        self.run_test_with_retries(
            "test_search_kubernetes_containers_running", test_logic, assertions
        )

    def test_search_kubernetes_containers_top_10_with_vulnerabilities(self):
        """Verify the agent can search for kubernetes containers have image vulnerabilities and sort them
        by image_vulnerability_count in descending order.
        """

        async def test_logic():
            fixtures = [
                {
                    "operation": "ReadContainerCombined",
                    "validator": lambda kwargs: "image_vulnerability_count"
                    in kwargs.get("parameters", {}).get("filter", "").lower(),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "container_id": "container-001",
                                    "agents": [
                                        {
                                            "aid": "558ce490595748d6a67b16969797d655",
                                            "build": "0000",
                                            "type": "Falcon sensor for linux",
                                        },
                                    ],
                                    "cloud_name": "AWS",
                                    "cloud_account_id": "00001",
                                    "cloud_region": "ca-central-1",
                                    "cluster_name": "production",
                                    "first_seen": "2025-05-27T03:04:10Z",
                                    "image_registry": "docker.amazonaws.com",
                                    "image_repository": "myservice",
                                    "image_tag": "v1.0.0",
                                    "image_vulnerability_count": 361,
                                    "last_seen": "2025-07-13T19:53:07Z",
                                    "container_name": "myservice",
                                    "namespace": "default",
                                    "running_status": True,
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = (
                "Find top 10 kubernetes containers that have images vulnerabilities"
            )
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_kubernetes_containers"
            )

            # Check for the filter for image_vulnerability_count
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "image_vulnerability_count" in tool_input_str,
                f"Expected image_vulnerability_count filtering in tool input: {tool_input_str}",
            )

            self.assertIn("container-001", used_tool["output"])

            # Verify API calls were made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (ReadContainerCombined)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )

            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "image_vulnerability_count:>0" in filter_str,
                f"Expected image_vulnerability_count filtering in API call: {filter_str}",
            )

            sort_str = api_call_params.get("sort", "").lower()
            self.assertTrue(
                "image_vulnerability_count.desc" in sort_str
                or "image_vulnerability_count|desc" in sort_str,
                f"Expected correct sort in API call: {sort_str}",
            )

            limit_str = api_call_params.get("limit", "").lower()
            self.assertTrue(
                "10" in limit_str,
                f"Expected correct limit in API call: {limit_str}",
            )

            # Verify result contains expected information
            self.assertIn("container-001", result)
            self.assertIn("361", result)  # vulnerability count

        self.run_test_with_retries(
            "test_search_kubernetes_containers_top_10_with_vulnerabilities",
            test_logic,
            assertions,
        )

    def test_count_kubernetes_containers_by_cloud_name(self):
        """Verify the agent can aggregate kubernetes containers by cloud name."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "ReadContainerCount",
                    "validator": lambda kwargs: "cloud_name"
                    in kwargs.get("parameters", {}).get("filter", "").lower(),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "count": 333,
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "How many kubernetes containers do I have in cloud provider AWS?"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_kubernetes_containers"
            )

            # Check for the filter for cloud_name
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "cloud_name" in tool_input_str,
                f"Expected running status filtering in tool input: {tool_input_str}",
            )

            self.assertIn("333", used_tool["output"])

            # Verify API calls were made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (ReadContainerCount)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )

            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "cloud_name:'AWS'" in filter_str,
                f"Expected cloud_name filtering in API call: {filter_str}",
            )

            # Verify result contains expected information
            self.assertIn("AWS", result)  # cloud name
            self.assertIn("333", result)  # containers count

        self.run_test_with_retries(
            "test_count_kubernetes_containers_by_cloud_name",
            test_logic,
            assertions,
        )

    def test_search_images_vulnerabilities_by_container_id(self):
        """Verify the agent can search images vulnerabilities by container ID."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "ReadCombinedVulnerabilities",
                    "validator": lambda kwargs: "container_id"
                    in kwargs.get("parameters", {}).get("filter", "").lower(),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "cve_id": "CVE-2005-2541",
                                    "severity": "High",
                                    "cvss_score": 10,
                                    "cps_current_rating": "Low",
                                    "description": "Tar 1.15.1 does not properly warn the user when extracting setuid or setgid files, which may allow local users or remote attackers to gain privileges.\n",
                                    "exploit_found": False,
                                    "exploited_status": 0,
                                    "exploited_status_string": "Unproven",
                                    "published_date": "2005-08-10T04:00:00Z",
                                    "images_impacted": 284,
                                    "packages_impacted": 7,
                                    "containers_impacted": 46,
                                    "remediation_available": False,
                                },
                            ],
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = 'Search images vulnerabilities for the container "container-001"'
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_images_vulnerabilities"
            )

            # Check for the filter for container_id
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "container_id" in tool_input_str,
                f"Expected container_id filtering in tool input: {tool_input_str}",
            )

            # Check for the vulnerability from the API response
            self.assertIn("CVE-2005-2541", used_tool["output"])

            # Verify API calls were made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (ReadContainerCombined)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )

            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "container_id:'container-001'" in filter_str,
                f"Expected container_id filtering in API call: {filter_str}",
            )

            # Verify result contains expected information
            self.assertIn("CVE-2005-2541", result)

        self.run_test_with_retries(
            "test_search_images_vulnerabilities_by_container_id",
            test_logic,
            assertions,
        )


if __name__ == "__main__":
    unittest.main()
