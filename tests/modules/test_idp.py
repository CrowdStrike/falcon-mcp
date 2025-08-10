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
                                "riskScoreSeverity": "MEDIUM",
                            }
                        ]
                    }
                }
            },
        }
        self.mock_client.command.return_value = mock_response

        # Call investigate_entity with basic parameters
        result = self.module.investigate_entity(
            entity_names=["Test User"],
            investigation_types=["entity_details"],
            limit=10,
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
                                    "secondaryDisplayName": "admin@example.com",
                                }
                            ]
                        }
                    }
                },
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
                                        {
                                            "type": "PRIVILEGED_ACCESS",
                                            "severity": "HIGH",
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                },
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
                                    "timestamp": "2024-01-01T12:00:00Z",
                                }
                            ],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                },
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
                                                "primaryDisplayName": "Test Server",
                                            },
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                },
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
                                        {
                                            "type": "PRIVILEGED_ACCESS",
                                            "severity": "HIGH",
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                },
            },
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with multiple investigation types
        result = self.module.investigate_entity(
            email_addresses=["admin@example.com"],
            investigation_types=[
                "entity_details",
                "timeline_analysis",
                "relationship_analysis",
                "risk_assessment",
            ],
            limit=50,
            include_associations=True,
            include_accounts=True,
            include_incidents=True,
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
        self.assertEqual(result["investigation_summary"]["status"], "failed")
        self.assertEqual(result["investigation_summary"]["entity_count"], 0)

        # Verify no API calls were made
        self.assertFalse(self.mock_client.command.called)

    def test_investigate_entity_no_entities_found(self):
        """Test handling when no entities are found matching criteria."""
        # Setup mock response with no entities
        mock_response = {
            "status_code": 200,
            "body": {"data": {"entities": {"nodes": []}}},
        }
        self.mock_client.command.return_value = mock_response

        # Call investigate_entity
        result = self.module.investigate_entity(entity_names=["NonExistent User"])

        # Verify result indicates no entities found
        self.assertIn("error", result)
        self.assertIn("investigation_summary", result)
        self.assertEqual(result["investigation_summary"]["status"], "failed")
        self.assertEqual(result["investigation_summary"]["entity_count"], 0)
        self.assertIn("search_criteria", result)


    def test_investigate_entity_with_geographic_location_data(self):
        """Test entity investigation includes geographic location data in timeline analysis."""
        # Setup mock GraphQL responses with geographic location data
        mock_responses = [
            # Entity resolution response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-geo-123",
                                    "primaryDisplayName": "Global User",
                                    "secondaryDisplayName": "global@example.com",
                                }
                            ]
                        }
                    }
                },
            },
            # Timeline response with geographic location data
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "timeline": {
                            "nodes": [
                                {
                                    "eventId": "auth-event-123",
                                    "eventType": "AUTHENTICATION",
                                    "eventSeverity": "MEDIUM",
                                    "timestamp": "2024-01-01T12:00:00Z",
                                    "sourceEntity": {
                                        "entityId": "test-entity-geo-123",
                                        "primaryDisplayName": "Global User",
                                    },
                                    "targetEntity": {
                                        "entityId": "server-456",
                                        "primaryDisplayName": "Corporate Server",
                                    },
                                    "geoLocation": {
                                        "country": "United States",
                                        "countryCode": "US",
                                        "city": "New York",
                                        "cityCode": "NYC",
                                        "latitude": 40.7128,
                                        "longitude": -74.0060,
                                    },
                                    "locationAssociatedWithUser": True,
                                    "userDisplayName": "Global User",
                                    "endpointDisplayName": "NYC-Workstation-01",
                                    "ipAddress": "192.168.1.100",
                                },
                                {
                                    "eventId": "auth-event-456",
                                    "eventType": "AUTHENTICATION",
                                    "eventSeverity": "HIGH",
                                    "timestamp": "2024-01-02T08:30:00Z",
                                    "sourceEntity": {
                                        "entityId": "test-entity-geo-123",
                                        "primaryDisplayName": "Global User",
                                    },
                                    "targetEntity": {
                                        "entityId": "server-789",
                                        "primaryDisplayName": "Remote Server",
                                    },
                                    "geoLocation": {
                                        "country": "Germany",
                                        "countryCode": "DE",
                                        "city": "Berlin",
                                        "cityCode": "BER",
                                        "latitude": 52.5200,
                                        "longitude": 13.4050,
                                    },
                                    "locationAssociatedWithUser": True,
                                    "userDisplayName": "Global User",
                                    "endpointDisplayName": "BER-Laptop-02",
                                    "ipAddress": "10.0.0.50",
                                },
                            ],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                },
            },
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with timeline analysis to get geographic data
        result = self.module.investigate_entity(
            entity_names=["Global User"],
            investigation_types=["timeline_analysis"],
            timeline_start_time="2024-01-01T00:00:00Z",
            timeline_end_time="2024-01-02T23:59:59Z",
            limit=50,
        )

        # Verify result structure
        self.assertIn("investigation_summary", result)
        self.assertIn("timeline_analysis", result)
        self.assertEqual(result["investigation_summary"]["status"], "completed")

        # Verify geographic location data is present in timeline events
        timeline_data = result["timeline_analysis"]["timelines"][0]["timeline"]
        self.assertGreater(len(timeline_data), 0)

        # Check first event has geographic location data
        first_event = timeline_data[0]
        self.assertIn("geoLocation", first_event)
        self.assertIn("country", first_event["geoLocation"])
        self.assertIn("countryCode", first_event["geoLocation"])
        self.assertIn("city", first_event["geoLocation"])
        self.assertIn("cityCode", first_event["geoLocation"])
        self.assertIn("latitude", first_event["geoLocation"])
        self.assertIn("longitude", first_event["geoLocation"])

        # Verify geographic location values
        self.assertEqual(first_event["geoLocation"]["country"], "United States")
        self.assertEqual(first_event["geoLocation"]["countryCode"], "US")
        self.assertEqual(first_event["geoLocation"]["city"], "New York")
        self.assertEqual(first_event["geoLocation"]["cityCode"], "NYC")

        # Check additional location fields
        self.assertIn("locationAssociatedWithUser", first_event)
        self.assertIn("userDisplayName", first_event)
        self.assertIn("endpointDisplayName", first_event)
        self.assertIn("ipAddress", first_event)

        # Verify second event has different country (multi-location user)
        second_event = timeline_data[1]
        self.assertEqual(second_event["geoLocation"]["country"], "Germany")
        self.assertEqual(second_event["geoLocation"]["countryCode"], "DE")

    def test_investigate_entity_with_geo_location_associations(self):
        """Test entity investigation includes geographic location associations."""
        # Setup mock GraphQL responses with geographic location associations
        mock_responses = [
            # Entity resolution response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-assoc-456",
                                    "primaryDisplayName": "Travel User",
                                    "secondaryDisplayName": "travel@example.com",
                                }
                            ]
                        }
                    }
                },
            },
            # Entity details response with geographic associations
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "test-entity-assoc-456",
                                    "primaryDisplayName": "Travel User",
                                    "secondaryDisplayName": "travel@example.com",
                                    "type": "USER",
                                    "riskScore": 60,
                                    "riskScoreSeverity": "MEDIUM",
                                    "associations": [
                                        {
                                            "bindingType": "LOCATION_ACCESS",
                                            "geoLocation": {
                                                "country": "France",
                                                "countryCode": "FR",
                                                "city": "Paris",
                                                "cityCode": "PAR",
                                                "latitude": 48.8566,
                                                "longitude": 2.3522,
                                            },
                                        },
                                        {
                                            "bindingType": "LOCATION_ACCESS",
                                            "geoLocation": {
                                                "country": "Japan",
                                                "countryCode": "JP",
                                                "city": "Tokyo",
                                                "cityCode": "TYO",
                                                "latitude": 35.6762,
                                                "longitude": 139.6503,
                                            },
                                        },
                                    ],
                                }
                            ]
                        }
                    }
                },
            },
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with entity details to get geographic associations
        result = self.module.investigate_entity(
            entity_names=["Travel User"],
            investigation_types=["entity_details"],
            include_associations=True,
            limit=50,
        )

        # Verify result structure
        self.assertIn("investigation_summary", result)
        self.assertIn("entity_details", result)
        self.assertEqual(result["investigation_summary"]["status"], "completed")

        # Verify geographic location associations are present
        entity_data = result["entity_details"]["entities"][0]
        self.assertIn("associations", entity_data)
        associations = entity_data["associations"]
        self.assertGreater(len(associations), 0)

        # Check geographic location associations
        geo_associations = [
            assoc for assoc in associations if "geoLocation" in assoc
        ]
        self.assertGreater(len(geo_associations), 0)

        # Verify first geographic association
        first_geo_assoc = geo_associations[0]
        self.assertIn("geoLocation", first_geo_assoc)
        geo_location = first_geo_assoc["geoLocation"]
        self.assertIn("country", geo_location)
        self.assertIn("countryCode", geo_location)
        self.assertIn("city", geo_location)
        self.assertIn("cityCode", geo_location)
        self.assertIn("latitude", geo_location)
        self.assertIn("longitude", geo_location)

        # Verify geographic location values
        self.assertEqual(geo_location["country"], "France")
        self.assertEqual(geo_location["countryCode"], "FR")

    def test_investigate_entity_multi_country_detection(self):
        """Test detection of users active in multiple countries."""
        # Setup mock GraphQL responses simulating user activity in 4+ countries
        mock_responses = [
            # Entity resolution response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "multi-country-user-789",
                                    "primaryDisplayName": "Global Executive",
                                    "secondaryDisplayName": "executive@example.com",
                                }
                            ]
                        }
                    }
                },
            },
            # Timeline response with activities from multiple countries
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "timeline": {
                            "nodes": [
                                {
                                    "eventId": "event-us-001",
                                    "eventType": "SUCCESSFUL_AUTHENTICATION",
                                    "timestamp": "2024-01-01T09:00:00Z",
                                    "geoLocation": {
                                        "country": "United States",
                                        "countryCode": "US",
                                        "city": "San Francisco",
                                        "cityCode": "SFO",
                                    },
                                    "locationAssociatedWithUser": True,
                                },
                                {
                                    "eventId": "event-uk-002",
                                    "eventType": "SUCCESSFUL_AUTHENTICATION",
                                    "timestamp": "2024-01-02T14:30:00Z",
                                    "geoLocation": {
                                        "country": "United Kingdom",
                                        "countryCode": "GB",
                                        "city": "London",
                                        "cityCode": "LDN",
                                    },
                                    "locationAssociatedWithUser": True,
                                },
                                {
                                    "eventId": "event-sg-003",
                                    "eventType": "SUCCESSFUL_AUTHENTICATION",
                                    "timestamp": "2024-01-03T22:15:00Z",
                                    "geoLocation": {
                                        "country": "Singapore",
                                        "countryCode": "SG",
                                        "city": "Singapore",
                                        "cityCode": "SIN",
                                    },
                                    "locationAssociatedWithUser": True,
                                },
                                {
                                    "eventId": "event-au-004",
                                    "eventType": "SUCCESSFUL_AUTHENTICATION",
                                    "timestamp": "2024-01-04T05:45:00Z",
                                    "geoLocation": {
                                        "country": "Australia",
                                        "countryCode": "AU",
                                        "city": "Sydney",
                                        "cityCode": "SYD",
                                    },
                                    "locationAssociatedWithUser": True,
                                },
                            ],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                },
            },
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with timeline analysis
        result = self.module.investigate_entity(
            entity_names=["Global Executive"],
            investigation_types=["timeline_analysis"],
            timeline_start_time="2024-01-01T00:00:00Z",
            timeline_end_time="2024-01-04T23:59:59Z",
            limit=100,
        )

        # Verify result structure
        self.assertIn("timeline_analysis", result)
        timeline_events = result["timeline_analysis"]["timelines"][0]["timeline"]
        self.assertEqual(len(timeline_events), 4)

        # Extract unique countries from timeline events
        countries = set()
        for event in timeline_events:
            if "geoLocation" in event and "country" in event["geoLocation"]:
                countries.add(event["geoLocation"]["country"])

        # Verify user has been active in 4 different countries
        expected_countries = {"United States", "United Kingdom", "Singapore", "Australia"}
        self.assertEqual(countries, expected_countries)
        self.assertEqual(len(countries), 4)

        # Verify each event has proper geographic location structure
        for event in timeline_events:
            self.assertIn("geoLocation", event)
            geo_loc = event["geoLocation"]
            self.assertIn("country", geo_loc)
            self.assertIn("countryCode", geo_loc)
            self.assertIn("city", geo_loc)
            self.assertIn("cityCode", geo_loc)
            self.assertTrue(event.get("locationAssociatedWithUser", False))

    def test_investigate_entity_file_operation_geographic_data(self):
        """Test geographic location data in file operation events (targetEntity only)."""
        # Setup mock response for file operation event with geographic data
        mock_responses = [
            # Entity resolution response
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "entities": {
                            "nodes": [
                                {
                                    "entityId": "file-user-123",
                                    "primaryDisplayName": "File User",
                                }
                            ]
                        }
                    }
                },
            },
            # Timeline response with file operation event
            {
                "status_code": 200,
                "body": {
                    "data": {
                        "timeline": {
                            "nodes": [
                                {
                                    "eventId": "file-op-001",
                                    "eventType": "FILE_OPERATION",
                                    "timestamp": "2024-01-01T15:30:00Z",
                                    "targetEntity": {
                                        "entityId": "file-server-456",
                                        "primaryDisplayName": "Shared File Server",
                                    },
                                    "geoLocation": {
                                        "country": "Canada",
                                        "countryCode": "CA",
                                        "city": "Toronto",
                                        "cityCode": "YYZ",
                                        "latitude": 43.6532,
                                        "longitude": -79.3832,
                                    },
                                    "locationAssociatedWithUser": True,
                                    "userDisplayName": "File User",
                                    "endpointDisplayName": "TOR-Desktop-01",
                                    "ipAddress": "172.16.0.25",
                                }
                            ],
                            "pageInfo": {"hasNextPage": False},
                        }
                    }
                },
            },
        ]
        self.mock_client.command.side_effect = mock_responses

        # Call investigate_entity with timeline analysis
        result = self.module.investigate_entity(
            entity_names=["File User"],
            investigation_types=["timeline_analysis"],
            limit=50,
        )

        # Verify file operation event has geographic data
        timeline_events = result["timeline_analysis"]["timelines"][0]["timeline"]
        file_event = timeline_events[0]

        # Verify event structure (should have targetEntity but no sourceEntity for file operations)
        self.assertIn("targetEntity", file_event)
        self.assertNotIn("sourceEntity", file_event)

        # Verify geographic location data is present
        self.assertIn("geoLocation", file_event)
        geo_loc = file_event["geoLocation"]
        self.assertEqual(geo_loc["country"], "Canada")
        self.assertEqual(geo_loc["countryCode"], "CA")
        self.assertEqual(geo_loc["city"], "Toronto")

        # Verify additional location context
        self.assertIn("locationAssociatedWithUser", file_event)
        self.assertIn("userDisplayName", file_event)
        self.assertIn("endpointDisplayName", file_event)
        self.assertIn("ipAddress", file_event)


if __name__ == "__main__":
    unittest.main()
