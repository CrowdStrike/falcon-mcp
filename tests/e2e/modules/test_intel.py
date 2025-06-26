"""
E2E tests for the Intel module.
"""
import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


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
                    "validator": lambda kwargs: "name:'SPIDER*'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "actor-1",
                                    "name": "SPIDER 2141052507",
                                    "slug": "spider-2141052507",
                                    "url": "https://example.com/actors/spider",
                                    "short_description": "Spidery spider",
                                    "created_date": 1631210620,
                                    "last_modified_date": 1631210629,
                                    "motivations": [
                                        {"id": "motivation-1", "slug": "state-sponsored", "value": "State-Sponsored"}
                                    ],
                                    "target_countries": [
                                        {"id": "country-1", "value": "United States"},
                                        {"id": "country-2", "value": "United Kingdom"}
                                    ],
                                    "target_industries": [
                                        {"id": "industry-1", "value": "Government"},
                                        {"id": "industry-2", "value": "Defense"}
                                    ]
                                },
                                {
                                    "id": "actor-2",
                                    "name": "BEAR-2141756032",
                                    "slug": "bear-2141756032",
                                    "url": "https://example.com/actors/bear",
                                    "short_description": "Regression Testing",
                                    "created_date": 1747440814,
                                    "last_modified_date": 1747440814,
                                    "motivations": [
                                        {"id": "motivation-1", "value": "Intelligence Gathering"},
                                        {"id": "motivation-2", "value": "Disruption"}
                                    ],
                                    "target_countries": [
                                        {"id": "country-1", "value": "United States"},
                                        {"id": "country-3", "value": "Ukraine"}
                                    ],
                                    "target_industries": [
                                        {"id": "industry-1", "value": "Government"},
                                        {"id": "industry-3", "value": "Energy"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all threat actors with names starting with BEAR"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_actors")

            # Verify the tool input contains the filter
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("APT", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("name:'APT*'", api_call_params.get('filter', ''))

            # Verify result contains actor information
            self.assertIn("BEAR", result)
            self.assertIn("Regression Testing", result)
            self.assertIn("SPIDER", result)
            self.assertIn("Spidery spider", result)

        self.run_test_with_retries(
            "test_search_actors_with_filter",
            test_logic,
            assertions
        )

    def test_search_actors_with_query(self):
        """Verify the agent can search for actors with a free text query."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelActorEntities",
                    "validator": lambda kwargs: kwargs.get('parameters', {}).get('q') == "lazarus",
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "actor-1",
                                    "name": "SPIDER 2141052507",
                                    "slug": "spider-2141052507",
                                    "url": "https://example.com/actors/spider",
                                    "short_description": "Spidery spider",
                                    "created_date": 1631210620,
                                    "last_modified_date": 1631210629,
                                    "motivations": [
                                        {"id": "motivation-1", "slug": "state-sponsored", "value": "State-Sponsored"}
                                    ],
                                    "target_countries": [
                                        {"id": "country-1", "value": "United States"},
                                        {"id": "country-2", "value": "United Kingdom"}
                                    ],
                                    "target_industries": [
                                        {"id": "industry-1", "value": "Government"},
                                        {"id": "industry-2", "value": "Defense"}
                                    ]
                                },
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Tell me about the Lazarus threat actor"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_actors")

            # Verify the tool input contains the query
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertEqual(tool_input.get('q'), "lazarus")

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertEqual(api_call_params.get('q'), "lazarus")

            # Verify result contains actor information
            self.assertIn("SPIDER 2141052507", result)
            self.assertIn("Spidery spider", result)
            self.assertIn("Government", result)

        self.run_test_with_retries(
            "test_search_actors_with_query",
            test_logic,
            assertions
        )

    def test_search_indicators_with_filter(self):
        """Verify the agent can search for indicators with a filter."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelIndicatorEntities",
                    "validator": lambda kwargs: "type:'domain'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "indicator-1",
                                    "indicator": "malicious.example.com",
                                    "type": "domain",
                                    "published_date": 1631210620,
                                    "last_updated": 1631210629,
                                    "malicious_confidence": "high",
                                    "reports": [
                                        {"id": "report-1", "name": "Threat Report 1"}
                                    ],
                                    "labels": [
                                        {"name": "malware", "created_on": 1631210620, "last_valid_on": 1631210629}
                                    ]
                                },
                                {
                                    "id": "indicator-2",
                                    "indicator": "evil.example.org",
                                    "type": "domain",
                                    "published_date": 1631210620,
                                    "last_updated": 1631210629,
                                    "malicious_confidence": "medium",
                                    "reports": [
                                        {"id": "report-2", "name": "Threat Report 2"}
                                    ],
                                    "labels": [
                                        {"name": "phishing", "created_on": 1631210620, "last_valid_on": 1631210629}
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all domain indicators with high confidence"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_indicators")

            # Verify the tool input contains the filter
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("domain", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("type:'domain'", api_call_params.get('filter', ''))

            # Verify result contains indicator information
            self.assertIn("malicious.example.com", result)
            self.assertIn("evil.example.org", result)
            self.assertIn("high", result)
            self.assertIn("medium", result)

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
                    "validator": lambda kwargs: "type:'malware'" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "report-1",
                                    "name": "Malware Analysis Report 1",
                                    "slug": "malware-analysis-report-1",
                                    "url": "https://example.com/reports/malware-1",
                                    "short_description": "Analysis of a new ransomware variant",
                                    "created_date": 1631210620,
                                    "last_modified_date": 1631210629,
                                    "type": {
                                        "id": "type-1",
                                        "name": "Malware Analysis",
                                        "slug": "malware-analysis"
                                    },
                                    "tags": [
                                        {"id": "tag-1", "value": "Ransomware"},
                                        {"id": "tag-2", "value": "Windows"}
                                    ],
                                    "malware": [
                                        {"family_name": "Locky", "slug": "locky"}
                                    ]
                                },
                                {
                                    "id": "report-2",
                                    "name": "Malware Analysis Report 2",
                                    "slug": "malware-analysis-report-2",
                                    "url": "https://example.com/reports/malware-2",
                                    "short_description": "Analysis of a banking trojan",
                                    "created_date": 1631310620,
                                    "last_modified_date": 1631310629,
                                    "type": {
                                        "id": "type-1",
                                        "name": "Malware Analysis",
                                        "slug": "malware-analysis"
                                    },
                                    "tags": [
                                        {"id": "tag-3", "value": "Banking Trojan"},
                                        {"id": "tag-2", "value": "Windows"}
                                    ],
                                    "malware": [
                                        {"family_name": "Zeus", "slug": "zeus"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Find all malware analysis reports"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_reports")

            # Verify the tool input contains the filter
            tool_input = json.loads(used_tool['input']['tool_input'])
            self.assertIn("malware", tool_input.get('filter', ''))

            # Verify API call parameters
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "Expected at least 1 API call")
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("type:'malware'", api_call_params.get('filter', ''))

            # Verify result contains report information
            self.assertIn("Malware Analysis Report 1", result)
            self.assertIn("Analysis of a new ransomware variant", result)
            self.assertIn("Malware Analysis Report 2", result)
            self.assertIn("Analysis of a banking trojan", result)
            self.assertIn("Locky", result)
            self.assertIn("Zeus", result)

        self.run_test_with_retries(
            "test_search_reports_with_filter",
            test_logic,
            assertions
        )


if __name__ == '__main__':
    unittest.main()
