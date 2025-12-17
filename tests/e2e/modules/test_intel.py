"""
E2E tests for the Intel module.
"""

import json
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
                    "validator": lambda kwargs: "animal_classifier:'BEAR'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "actor-1",
                                    "animal_classifier": "BEAR",
                                    "short_description": "Actor ELDERLY BEAR",
                                },
                                {
                                    "id": "actor-2",
                                    "animal_classifier": "BEAR",
                                    "short_description": "Actor CONSTANT BEAR",
                                },
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Find all threat actors with animal_classifier BEAR"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_actors")

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("animal_classifier", tool_input.get("filter", ""))

            # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertIn("animal_classifier:'BEAR'", api_call_params.get("filter", ""))

            # Verify result contains actor information
            self.assertIn("BEAR", result)
            self.assertIn("ELDERLY BEAR", result)
            self.assertIn("Actor CONSTANT BEAR", result)

        self.run_test_with_retries(
            "test_search_actors_with_filter", test_logic, assertions
        )

    def test_search_indicators_with_filter(self):
        """Verify the agent can search for indicators with a filter."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelIndicatorEntities",
                    "validator": lambda kwargs: "type:'hash_sha256'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {"id": "indicator-1", "type": "hash_sha256"},
                                {"id": "indicator-2", "type": "hash_sha256"},
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Find all indicators of type hash_sha256"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(
                used_tool["input"]["tool_name"], "falcon_search_indicators"
            )

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("hash_sha256", tool_input.get("filter", ""))

            # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertIn("type:'hash_sha256'", api_call_params.get("filter", ""))

            # Verify result contains indicator information
            self.assertIn("indicator-1", result)
            self.assertIn("indicator-2", result)
            self.assertIn("hash_sha256", result)

        self.run_test_with_retries(
            "test_search_indicators_with_filter", test_logic, assertions
        )

    def test_search_reports_with_filter(self):
        """Verify the agent can search for reports with a filter."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryIntelReportEntities",
                    "validator": lambda kwargs: "slug:'malware-analysis-report-1'"
                    in kwargs.get("parameters", {}).get("filter", ""),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "report-1",
                                    "name": "Malware Analysis Report 1",
                                    "slug": "malware-analysis-report-1",
                                },
                            ]
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Find report with slug malware-analysis-report-1"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_search_reports")

            # Verify the tool input contains the filter
            tool_input = ensure_dict(used_tool["input"]["tool_input"])
            self.assertIn("slug", tool_input.get("filter", ""))

            # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertIn(
                "slug:'malware-analysis-report-1'", api_call_params.get("filter", "")
            )

            # Verify result contains report information
            self.assertIn("Malware Analysis Report 1", result)

        self.run_test_with_retries(
            "test_search_reports_with_filter", test_logic, assertions
        )

    def test_get_mitre_report_by_actor_id(self):
        """Verify the agent can get MITRE report for a specific actor."""

        async def test_logic():
            fixtures = [
                {
                    "operation": "GetMitreReport",
                    "validator": lambda kwargs: (
                        kwargs.get("parameters", {}).get("actor_id") == "123456" and
                        kwargs.get("parameters", {}).get("format") == "csv"
                    ),
                    "response": {
                        "status_code": 200,
                        "body": '''id,tactic_id,tactic_name,technique_id,technique_name,reports,observables
fake_id_1,fake_tactic_001,Fake Initial Tactic,fake_technique_001,Fake Cloud Technique,FAKE-REPORT-001,"Fake threat actor has used fake cloud techniques for testing purposes."
fake_id_2,fake_tactic_002,Fake Secondary Tactic,fake_technique_002,Fake Application Exploit,FAKE-REPORT-002,"Fake threat actor has exploited fake applications during testing."'''.encode('utf-8'),
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Get MITRE ATT&CK report for actor ID 123456 in CSV format"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_get_mitre_report")

            # Verify the tool input contains the correct actor parameter
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertIn("123456", tool_input_str)

            # Verify API call parameters
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected at least 1 API call",
            )
            api_call_params = self._mock_api_instance.command.call_args_list[0][1].get(
                "parameters", {}
            )
            self.assertEqual(api_call_params.get("actor_id"), "123456")
            self.assertEqual(api_call_params.get("format"), "csv")

            # Verify result contains MITRE information in CSV format
            self.assertIn("fake initial tactic", result.lower())
            self.assertIn("fake_technique_002", result.lower())
            self.assertIn("fake cloud technique", result.lower())
            self.assertIn("csv", result.lower())  # Should mention CSV format

        self.run_test_with_retries(
            "test_get_mitre_report_by_actor_id", test_logic, assertions
        )

    def test_get_mitre_report_by_actor_name(self):
        """Verify the agent can get MITRE report using actor name."""

        async def test_logic():
            fixtures = [
                # Search for actor by name (internal to get_mitre_report method)
                {
                    "operation": "QueryIntelActorEntities",
                    "validator": lambda kwargs: (
                        "name:'FAKE BEAR'" in kwargs.get("parameters", {}).get("filter", "") and
                        kwargs.get("parameters", {}).get("limit") == 1
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {
                                    "id": "123456",
                                    "name": "FAKE BEAR",
                                    "short_description": "FAKE BEAR is a fictional test adversary group for testing purposes...",
                                    "animal_classifier": "BEAR",
                                },
                            ]
                        },
                    },
                },
                # Get MITRE report using the resolved numeric actor ID
                {
                    "operation": "GetMitreReport",
                    "validator": lambda kwargs: (
                        kwargs.get("parameters", {}).get("actor_id") == "123456"
                    ),
                    "response": {
                        "status_code": 200,
                        "body": '''[
                            {
                                "id": "fake_id_3",
                                "tactic_id": "fake_tactic_003",
                                "tactic_name": "Fake Persistence Tactic",
                                "technique_id": "fake_technique_003",
                                "technique_name": "Fake Registry Technique",
                                "reports": ["FAKE-REPORT-003"],
                                "observables": ["FAKE BEAR has modified fake registry keys for testing purposes."]
                            },
                            {
                                "id": "fake_id_4",
                                "tactic_id": "fake_tactic_004",
                                "tactic_name": "Fake Exfiltration Tactic",
                                "technique_id": "fake_technique_004",
                                "technique_name": "Fake Network Exfiltration",
                                "reports": ["FAKE-REPORT-004"],
                                "observables": ["FAKE BEAR has exfiltrated fake data over fake network channels."]
                            }
                        ]'''.encode('utf-8'),
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Get MITRE ATT&CK report for actor FAKE BEAR"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Should only have 1 tool call since get_mitre_report handles the search internally
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_get_mitre_report")

            # Verify the tool input contains the actor name (not ID)
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertIn("fake bear", tool_input_str)

            # Verify API calls were made (both search and MITRE report)
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                2,
                "Expected at least 2 API calls (search + MITRE report)",
            )

            # Verify the search API call was made correctly
            search_call = None
            mitre_call = None
            for call in self._mock_api_instance.command.call_args_list:
                if call[0][0] == "QueryIntelActorEntities":
                    search_call = call
                elif call[0][0] == "GetMitreReport":
                    mitre_call = call

            self.assertIsNotNone(search_call, "Expected QueryIntelActorEntities API call")
            self.assertIsNotNone(mitre_call, "Expected GetMitreReport API call")

            # Verify search parameters
            search_params = search_call[1].get("parameters", {})
            self.assertIn("name:'FAKE BEAR'", search_params.get("filter", ""))
            self.assertEqual(search_params.get("limit"), 1)

            # Verify MITRE report parameters
            mitre_params = mitre_call[1].get("parameters", {})
            self.assertEqual(mitre_params.get("actor_id"), "123456")

            # Verify result contains MITRE information (case-insensitive)
            result_lower = result.lower()
            self.assertIn("fake bear", result_lower)
            # Check for formatted content rather than raw field names
            self.assertIn("persistence", result_lower)
            self.assertIn("exfiltration", result_lower)
            self.assertIn("registry technique", result_lower)
            self.assertIn("network exfiltration", result_lower)

        self.run_test_with_retries(
            "test_get_mitre_report_by_actor_name", test_logic, assertions
        )

    def test_get_mitre_report_actor_not_found(self):
        """Verify the agent handles case when actor is not found."""

        async def test_logic():
            fixtures = [
                # Search for non-existent actor (internal to get_mitre_report method)
                {
                    "operation": "QueryIntelActorEntities",
                    "validator": lambda kwargs: (
                        "name:'NONEXISTENT ACTOR'" in kwargs.get("parameters", {}).get("filter", "") and
                        kwargs.get("parameters", {}).get("limit") == 1
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": []  # No results found
                        },
                    },
                }
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            prompt = "Get MITRE ATT&CK report for actor NONEXISTENT ACTOR"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Should have 1 tool call that results in an error
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool["input"]["tool_name"], "falcon_get_mitre_report")

            # Verify the tool input contains the actor name
            tool_input_str = json.dumps(used_tool["input"]["tool_input"]).lower()
            self.assertIn("nonexistent actor", tool_input_str)

            # Should only have 1 API call (just the search, no MITRE report)
            self.assertEqual(
                self._mock_api_instance.command.call_count,
                1,
                "Expected exactly 1 API call (actor search only)",
            )

            # Verify result contains error information
            result_lower = result.lower()
            self.assertIn("not found", result_lower)
            self.assertIn("nonexistent actor", result_lower)

        self.run_test_with_retries(
            "test_get_mitre_report_actor_not_found", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
