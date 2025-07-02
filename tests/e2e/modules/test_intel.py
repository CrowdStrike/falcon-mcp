"""
E2E tests for the Intel module.
"""
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest, ensure_dict


@pytest.mark.e2e
class TestIntelModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Intel Module.
    """

    def test_search_actors_with_filter(self):
        """Verify the agent can search for actors with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelActorEntities",
                    "validator": lambda kwargs: "animal_classifier:'BEAR'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "actor-1",
                                    "animal_classifier": "BEAR",
                                    "short_description": "Actor ELDERLY BEAR"
                                },
                                {
                                    "id": "actor-2",
                                    "animal_classifier": "BEAR",
                                    "short_description": "Actor CONSTANT BEAR"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all threat actors with animal_classifier BEAR"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_actors")

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool['input']['tool_input'])
            self.assertIn("animal_classifier", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("animal_classifier:'BEAR'", api_call_params.get('filter', ''))

            # Verify result contains actor information
            self.assertIn("BEAR", result)
            self.assertIn("ELDERLY BEAR", result)
            self.assertIn("Actor CONSTANT BEAR", result)

        self.run_test_with_retries(
            "test_search_actors_with_filter",
            test_logic,
            assertions
        )

    def test_search_indicators_with_filter(self):
        """Verify the agent can search for indicators with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelIndicatorEntities",
                    "validator": lambda kwargs: "type:'hash_sha256'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "indicator-1",
                                    "type": "hash_sha256"
                                },
                                {
                                    "id": "indicator-2",
                                    "type": "hash_sha256"
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all indicators of type hash_sha256"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_indicators")

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool['input']['tool_input'])
            self.assertIn("hash_sha256", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("type:'hash_sha256'", api_call_params.get('filter', ''))

            # Verify result contains indicator information
            self.assertIn("indicator-1", result)
            self.assertIn("indicator-2", result)
            self.assertIn("hash_sha256", result)

        self.run_test_with_retries(
            "test_search_indicators_with_filter",
            test_logic,
            assertions
        )

    def test_search_reports_with_filter(self):
        """Verify the agent can search for reports with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelReportEntities",
                    "validator": lambda kwargs: "slug:'malware-analysis-report-1'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "report-1",
                                    "name": "Malware Analysis Report 1",
                                    "slug": "malware-analysis-report-1"
                                },
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find report with slug malware-analysis-report-1"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_reports")

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool['input']['tool_input'])
            self.assertIn("slug", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("slug:'malware-analysis-report-1'", api_call_params.get('filter', ''))

            # Verify result contains report information
            self.assertIn("Malware Analysis Report 1", result)

        self.run_test_with_retries(
            "test_search_reports_with_filter",
            test_logic,
            assertions
        )


if __name__ == '__main__':
    unittest.main()
