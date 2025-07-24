"""
E2E tests for the Spotlight module.
"""

import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestSpotlightModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Spotlight Module.
    """

    def test_search_high_severity_vulnerabilities(self):
        """Verify the agent can search for high severity vulnerabilities."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "combinedQueryVulnerabilities",
                    "validator": lambda kwargs: "high"
                    in kwargs.get("parameters", {}).get("filter", "").lower(),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "vuln-001",
                                    "cve": {
                                        "id": "CVE-2024-1234",
                                        "base_score": 8.5,
                                        "severity": "HIGH",
                                        "exprt_rating": "HIGH",
                                        "exploit_status": 60,
                                        "is_cisa_kev": True,
                                        "description": "Critical buffer overflow vulnerability in network service",
                                    },
                                    "status": "open",
                                    "created_timestamp": "2024-01-15T10:30:00Z",
                                    "updated_timestamp": "2024-01-20T14:15:00Z",
                                    "host_info": {
                                        "hostname": "web-server-01",
                                        "platform_name": "Linux",
                                        "asset_criticality": "Critical",
                                        "internet_exposure": "Yes",
                                        "managed_by": "Falcon sensor",
                                    },
                                    "apps": {
                                        "application_name": "Apache HTTP Server",
                                        "application_version": "2.4.41",
                                    },
                                },
                                {
                                    "id": "vuln-002",
                                    "cve": {
                                        "id": "CVE-2024-5678",
                                        "base_score": 7.8,
                                        "severity": "HIGH",
                                        "exprt_rating": "MEDIUM",
                                        "exploit_status": 30,
                                        "is_cisa_kev": False,
                                        "description": "Privilege escalation vulnerability in system service",
                                    },
                                    "status": "open",
                                    "created_timestamp": "2024-01-18T08:45:00Z",
                                    "updated_timestamp": "2024-01-19T16:20:00Z",
                                    "host_info": {
                                        "hostname": "db-server-02",
                                        "platform_name": "Windows",
                                        "asset_criticality": "High",
                                        "internet_exposure": "No",
                                        "managed_by": "Falcon sensor",
                                    },
                                    "apps": {
                                        "application_name": "Microsoft SQL Server",
                                        "application_version": "2019",
                                    },
                                },
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Find all high severity vulnerabilities in our environment and show me their CVE details and affected hosts"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_vulnerabilities"
            )

            # Check for high severity filtering
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertTrue(
                "high" in tool_input_str,
                f"Expected high severity filtering in tool input: {tool_input_str}",
            )

            # Verify both vulnerabilities are in the output
            self.assertIn("CVE-2024-1234", used_tool["output"])
            self.assertIn("CVE-2024-5678", used_tool["output"])
            self.assertIn("web-server-01", used_tool["output"])
            self.assertIn("db-server-02", used_tool["output"])

            # Verify API call was made correctly
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count, 1, "Expected 1 API call"
            )

            # Check API call (combinedQueryVulnerabilities)
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            filter_str = api_call_params.get("filter", "").lower()
            self.assertTrue(
                "high" in filter_str,
                f"Expected high severity filtering in API call: {filter_str}",
            )

            # Verify result contains expected information
            self.assertIn("CVE-2024-1234", result)
            self.assertIn("CVE-2024-5678", result)
            self.assertIn("web-server-01", result)
            self.assertIn("db-server-02", result)
            self.assertIn("8.5", result)  # Should contain CVSS scores
            self.assertIn("7.8", result)

        self.run_test_with_retries(
            "test_search_high_severity_vulnerabilities", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
