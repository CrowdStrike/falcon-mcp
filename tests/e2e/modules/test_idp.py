"""
E2E tests for the Identity Protection (IDP) module.
"""

import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestIdpModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Identity Protection Module.
    """

    def test_investigate_entity_comprehensive(self):
        """Test comprehensive entity investigation - What can you tell me about the user 'Wallace Muniz'?"""

        async def test_logic():
            fixtures = [
                # First call: Entity name resolution (search for Wallace Muniz)
                {
                    "operation": "api_preempt_proxy_post_graphql",
                    "validator": lambda kwargs: (
                        "primaryDisplayNames" in kwargs.get("body", {}).get("query", "")
                        and "Wallace Muniz" in kwargs.get("body", {}).get("query", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "data": {
                                "entities": {
                                    "nodes": [
                                        {
                                            "entityId": "wallace-muniz-001",
                                            "primaryDisplayName": "Wallace Muniz",
                                        }
                                    ]
                                }
                            }
                        },
                    },
                },
                # Second call: Comprehensive entity details (default investigation includes entity_details)
                {
                    "operation": "api_preempt_proxy_post_graphql",
                    "validator": lambda kwargs: (
                        "entityIds" in kwargs.get("body", {}).get("query", "")
                        and "wallace-muniz-001"
                        in kwargs.get("body", {}).get("query", "")
                        and "riskFactors" in kwargs.get("body", {}).get("query", "")
                    ),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "data": {
                                "entities": {
                                    "nodes": [
                                        {
                                            "entityId": "wallace-muniz-001",
                                            "primaryDisplayName": "Wallace Muniz",
                                            "secondaryDisplayName": "wmuniz@corp.local",
                                            "type": "USER",
                                            "riskScore": 85.5,
                                            "riskScoreSeverity": "HIGH",
                                            "riskFactors": [
                                                {
                                                    "type": "EXCESSIVE_PRIVILEGES",
                                                    "severity": "HIGH",
                                                },
                                                {
                                                    "type": "SUSPICIOUS_ACTIVITY",
                                                    "severity": "MEDIUM",
                                                },
                                            ],
                                            "associations": [
                                                {
                                                    "bindingType": "MEMBER_OF",
                                                    "entity": {
                                                        "entityId": "admin-group-001",
                                                        "primaryDisplayName": "Domain Admins",
                                                        "secondaryDisplayName": "CORP.LOCAL\\Domain Admins",
                                                        "type": "ENTITY_CONTAINER",
                                                    },
                                                }
                                            ],
                                            "accounts": [
                                                {
                                                    "domain": "CORP.LOCAL",
                                                    "samAccountName": "wmuniz",
                                                    "passwordAttributes": {
                                                        "lastChange": "2024-01-10T08:30:00Z",
                                                        "strength": "STRONG",
                                                    },
                                                }
                                            ],
                                            "openIncidents": {
                                                "nodes": [
                                                    {
                                                        "type": "SUSPICIOUS_LOGIN",
                                                        "startTime": "2024-01-15T10:30:00Z",
                                                        "compromisedEntities": [
                                                            {
                                                                "entityId": "wallace-muniz-001",
                                                                "primaryDisplayName": "Wallace Muniz",
                                                            }
                                                        ],
                                                    }
                                                ]
                                            },
                                        }
                                    ]
                                }
                            }
                        },
                    },
                },
            ]

            self._mock_api_instance.command.side_effect = (
                self._create_mock_api_side_effect(fixtures)
            )

            # Comprehensive question that should trigger entity investigation
            prompt = "What can you tell me about the user Wallace Muniz?"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Basic checks - tool was called and we got a result
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Check that the IDP investigate entity tool was used
            used_tool = tools[-1]  # Get the last tool used
            tool_name = used_tool["input"]["tool_name"]
            self.assertEqual(
                tool_name,
                "falcon_idp_investigate_entity",
                f"Expected idp_investigate_entity tool, got: {tool_name}",
            )

            # Check that the tool was called with Wallace Muniz in entity_names
            tool_input = used_tool["input"]["tool_input"]
            self.assertIn(
                "entity_names",
                tool_input,
                "Tool should be called with entity_names parameter",
            )

            entity_names = tool_input.get("entity_names", [])
            self.assertTrue(
                any("Wallace Muniz" in name for name in entity_names),
                f"Tool should be called with Wallace Muniz in entity_names: {entity_names}",
            )

            # Check that we got comprehensive result mentioning the entity details
            result_lower = result.lower()
            self.assertIn("wallace", result_lower, "Result should mention Wallace")

            # Should mention some key details from the comprehensive response
            self.assertTrue(
                any(
                    keyword in result_lower
                    for keyword in ["risk", "high", "privileges", "admin"]
                ),
                "Result should mention risk-related information",
            )

            # Check that the mock API was called at least twice (entity resolution + details)
            self.assertGreaterEqual(
                self._mock_api_instance.command.call_count,
                2,
                "API should be called at least twice for comprehensive investigation",
            )

            # Verify the API calls were made with expected GraphQL queries
            api_calls = self._mock_api_instance.command.call_args_list

            # First call should be entity name search
            first_call_query = api_calls[0][1].get("body", {}).get("query", "")
            self.assertIn(
                "primaryDisplayNames",
                first_call_query,
                "First call should search by primaryDisplayNames",
            )
            self.assertIn(
                "Wallace Muniz",
                first_call_query,
                "First call should search for Wallace Muniz",
            )

            # Second call should be detailed entity lookup
            second_call_query = api_calls[1][1].get("body", {}).get("query", "")
            self.assertIn(
                "entityIds", second_call_query, "Second call should lookup by entityIds"
            )
            self.assertIn(
                "riskFactors",
                second_call_query,
                "Second call should include risk factors",
            )

        self.run_test_with_retries(
            "test_investigate_entity_comprehensive", test_logic, assertions
        )


if __name__ == "__main__":
    unittest.main()
