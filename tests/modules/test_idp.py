"""
Tests for the IDP (Identity Protection) module.
"""
import unittest

from falcon_mcp.modules.idp import IdpModule
from tests.modules.utils.test_modules import TestModules


class TestIdpModule(TestModules):
    """Test cases for the IDP module."""

    def setUp(self):
        """Set up test fixtures."""
        self.setup_module(IdpModule)

    def test_register_tools(self):
        """Test registering tools with the server."""
        expected_tools = [
            "falcon_idp_investigate_entity",
        ]
        self.assert_tools_registered(expected_tools)

    def test_investigate_entity_basic_functionality(self):
        """Test basic entity investigation functionality."""
        # Setup mock GraphQL response for entity resolution
        mock_response = {
            "status_code": 200,
            "body": {
                "data": {
                    "entities": {
                        "nodes": [
                            {
                                "entityId": "test-entity-123",
                                "primaryDisplayName": "Test User",
                                "secondaryDisplayName": "test@example.com",
                                "type": "USER",
                                "riskScore": 75,
                                "riskScoreSeverity": "MEDIUM"
                            }
                        ]
                    }
                }
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call investigate_entity with basic parameters
        result = self.module.investigate_entity(
            entity_names=["Test User"],
            investigation_types=["entity_details"],
            limit=10
        )

        # Verify client command was called (at least for entity resolution)
        self.assertTrue(self.mock_client.command.called)

        # Verify result structure
        self.assertIn("investigation_summary", result)
        self.assertIn("entity_details", result)
        self.assertEqual(result["investigation_summary"]["status"], "completed")
        self.assertGreater(result["investigation_summary"]["entity_count"], 0)

    def test_investigate_entity_with_multiple_investigation_types(self):
        """Test entity investigation with multiple investigation types."""
        # Setup mock GraphQL responses for different investigation types
        mock_responses = [
            # Entity resolution response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-456",
                                    "primaryDisplayName": "Admin User",
                                    "secondaryDisplayName": "admin@example.com"
                                }
                            ]
                        }
                    }
                }
            },
            # Entity details response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-456",
                                    "primaryDisplayName": "Admin User",
                                    "secondaryDisplayName": "admin@example.com",
                                    "type": "USER",
                                    "riskScore": 85,
                                    "riskScoreSeverity": "HIGH",
                                    "riskFactors": [
                                        {"type": "PRIVILEGED_ACCESS", "severity": "HIGH"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
            # Timeline response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "timeline": {
                            "nodes": [
                                {
                                    "eventId": "event-123",
                                    "eventType": "AUTHENTICATION",
                                    "timestamp": "2024-01-01T12:00:00Z"
                                }
                            ],
                            "pageInfo": {"hasNextPage": False}
                        }
                    }
                }
            },
            # Relationship analysis response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-456",
                                    "primaryDisplayName": "Admin User",
                                    "associations": [
                                        {
                                            "bindingType": "OWNERSHIP",
                                            "entity": {
                                                "entityId": "server-789",
                                                "primaryDisplayName": "Test Server"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
            # Risk assessment response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-456",
                                    "primaryDisplayName": "Admin User",
                                    "riskScore": 85,
                                    "riskScoreSeverity": "HIGH",
                                    "riskFactors": [
                                        {"type": "PRIVILEGED_ACCESS", "severity": "HIGH"}
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with multiple investigation types
        result = self.module.investigate_entity(
            email_addresses=["admin@example.com"],
            investigation_types=["entity_details", "timeline_analysis", "relationship_analysis", "risk_assessment"],
            limit=50,
            include_associations=True,
            include_accounts=True,
            include_incidents=True
        )

        # Verify multiple client commands were called
        self.assertGreaterEqual(self.mock_client.command.call_count, 2)

        # Verify result structure contains all investigation types
        self.assertIn("investigation_summary", result)
        self.assertIn("entity_details", result)
        self.assertIn("timeline_analysis", result)
        self.assertIn("relationship_analysis", result)
        self.assertIn("risk_assessment", result)

        # Verify investigation summary
        self.assertEqual(result["investigation_summary"]["status"], "completed")
        self.assertGreater(result["investigation_summary"]["entity_count"], 0)
        self.assertEqual(len(result["investigation_summary"]["investigation_types"]), 4)

    def test_investigate_entity_no_identifiers_error(self):
        """Test error handling when no entity identifiers are provided."""
        # Call investigate_entity without any identifiers
        result = self.module.investigate_entity()

        # Verify error response
        self.assertIn("error", result)
        self.assertIn("investigation_summary", result)
        self.assertEqual(result["investigation_summary"]["status"], "no_entities_found")
        self.assertEqual(result["investigation_summary"]["entity_count"], 0)

        # Verify no API calls were made
        self.assertFalse(self.mock_client.command.called)

    def test_investigate_entity_no_entities_found(self):
        """Test handling when no entities are found matching criteria."""
        # Setup mock response with no entities
        mock_response = {
            "status_code": 200,
            "body": {
                "data": {
                    "entities": {
                        "nodes": []
                    }
                }
            }
        }
        self.mock_client.command.return_value = mock_response

        # Call investigate_entity
        result = self.module.investigate_entity(
            entity_names=["NonExistent User"]
        )

        # Verify result indicates no entities found
        self.assertIn("error", result)
        self.assertIn("investigation_summary", result)
        self.assertEqual(result["investigation_summary"]["status"], "no_entities_found")
        self.assertEqual(result["investigation_summary"]["entity_count"], 0)
        self.assertIn("search_criteria", result)


if __name__ == '__main__':
    unittest.main()
