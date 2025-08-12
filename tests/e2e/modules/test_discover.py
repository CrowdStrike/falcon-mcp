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
                    "validator": lambda kwargs: "category:'Web Browsers'" in kwargs.get("parameters", {}).get("filter", ""),
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
                                        "group3"
                                    ],
                                    "category": "Web Browsers",
                                    "architectures": [
                                        "x64"
                                    ],
                                    "first_seen_timestamp": "2025-02-15T10:30:00Z",
                                    "last_updated_timestamp": "2025-03-01T14:45:22Z",
                                    "is_suspicious": False,
                                    "is_normalized": True,
                                    "host": {
                                        "id": "abc123_xyz789"
                                    }
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
                                        "group5"
                                    ],
                                    "category": "Web Browsers",
                                    "architectures": [
                                        "x64"
                                    ],
                                    "first_seen_timestamp": "2025-01-10T08:15:30Z",
                                    "last_updated_timestamp": "2025-02-20T11:22:45Z",
                                    "is_suspicious": False,
                                    "is_normalized": True,
                                    "host": {
                                        "id": "def456_abc123"
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

            prompt = "Search for all applications categorized as Web Browsers in our environment and show me their details"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            tool_names_called = [tool["input"]["tool_name"] for tool in tools]
            self.assertIn("falcon_search_applications_fql_guide", tool_names_called)
            self.assertIn("falcon_search_applications", tool_names_called)
        
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_applications"
            )

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

        self.run_test_with_retries(
            "test_search_applications_by_category", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
