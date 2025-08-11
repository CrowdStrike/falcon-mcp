"""
E2E tests for the Serverless module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest, ensure_dict


@pytest.mark.e2e
class TestServerlessModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Serverless Module.
    """

    def test_search_serverless_vulnerabilities(self):
        """Verify the agent can search for high severity vulnerabilities in serverless environment"""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetCombinedVulnerabilitiesSARIF",
                    "validator": lambda kwargs: "severity:'HIGH'" in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "runs": [
                                {
                                    "tool": {
                                        "driver": {
                                            "name": "CrowdStrike",
                                            "informationUri": "https://www.crowdstrike.com/",
                                            "rules": [
                                                {
                                                    "id": "CVE-2023-45678",
                                                    "name": "PythonPackageVulnerability",
                                                    "shortDescription": {"text": "Security vulnerability in package xyz"},
                                                    "fullDescription": {"text": "A critical vulnerability was found in package xyz that could lead to remote code execution"},
                                                    "help": {"text": "Package: xyz\nInstalled Version: 1.2.3\nVulnerability: CVE-2023-45678\nSeverity: HIGH\nRemediation: [Upgrade to version 2.0.0]"},
                                                    "properties": {
                                                        "severity": "HIGH",
                                                        "cvssBaseScore": 8.5,
                                                        "remediations": ["Upgrade to version 2.0.0"],
                                                        "cloudProvider": "AWS",
                                                        "region": "us-west-2",
                                                        "functionName": "sample-lambda-function"
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "get vulnerabilities in my serverless environment with high severity"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            self.assertIn("falcon_serverless_vulnerabilities_fql_guide", tool_names_called)
            self.assertIn("falcon_search_serverless_vulnerabilities", tool_names_called)

            # Find the search_serverless_vulnerabilities tool call
            search_tool_call = None
            for tool in tools:
                if tool["input"]["tool_name"] == "falcon_search_serverless_vulnerabilities":
                    search_tool_call = tool
                    break
            
            self.assertIsNotNone(search_tool_call, "Expected falcon_search_serverless_vulnerabilities tool to be called")

            # Verify the tool input contains the filter parameter with proper FQL syntax
            tool_input = ensure_dict(search_tool_call["input"]["tool_input"])
            self.assertIn("filter", tool_input, "Tool input should contain a 'filter' parameter")
            self.assertIn("severity:'HIGH'", tool_input.get("filter", ""), "Filter should contain severity:'HIGH' in FQL syntax")

            # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_args = self._mock_api_instance.command.call_args_list[0]
            self.assertEqual(api_call_args[0][0], "GetCombinedVulnerabilitiesSARIF")
            api_call_params = api_call_args[1].get("parameters", {})
            self.assertIn("severity:'HIGH'", api_call_params.get("filter", ""))

            # Verify the result contains information about the vulnerability
            self.assertIn("CVE-2023-45678", result, "Result should mention the CVE ID")
            self.assertIn("HIGH", result, "Result should mention the severity")
            self.assertIn("AWS", result, "Result should mention the cloud provider")

        self.run_test_with_retries(
            "test_search_serverless_vulnerabilities", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
