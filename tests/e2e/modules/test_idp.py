"""
E2E tests for the Identity Protection (IDP) module.
"""
import json
import unittest

import pytest

from tests.e2e.utils.base_e2e_test import BaseE2ETest


@pytest.mark.e2e
class TestIdpModuleE2E(BaseE2ETest):
    """
    End-to-end test suite for the Falcon MCP Server Identity Protection Module.
    """

    def test_investigate_entity_basic(self):
        """Test basic entity investigation - simple question: What is Wallace Muniz's risk score?"""

        async def test_logic():
            # Single fixture for entity lookup
            fixtures = [
                {
                    "operation": "api_preempt_proxy_post_graphql",
                    "validator": lambda kwargs: "Wallace Muniz" in kwargs.get('body', {}).get('query', ''),
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
                                            "riskScore": 85.5,
                                            "riskScoreSeverity": "HIGH"
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            # Simple, direct question
            prompt = "What is Wallace Muniz's risk score?"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            # Basic checks - tool was called and we got a result
            self.assertGreaterEqual(len(tools), 1, "Expected at least 1 tool call")

            # Check that some IDP tool was used
            used_tool = tools[-1]  # Get the last tool used
            tool_name = used_tool['input']['tool_name']
            self.assertTrue(
                tool_name.startswith("falcon_idp") or "investigate" in tool_name.lower(),
                f"Expected an IDP investigation tool, got: {tool_name}"
            )

            # Check that the tool was called with Wallace Muniz
            tool_input = used_tool['input']['tool_input']
            tool_input_str = json.dumps(tool_input).lower()
            self.assertIn("wallace muniz", tool_input_str, "Tool should be called with Wallace Muniz")

            # Check that we got some result mentioning the entity
            self.assertIn("Wallace", result, "Result should mention Wallace")

            # Check that the mock API was called
            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 1, "API should be called")

        self.run_test_with_retries(
            "test_investigate_entity_basic",
            test_logic,
            assertions
        )


if __name__ == '__main__':
    unittest.main()
