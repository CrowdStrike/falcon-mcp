"""Tests for the Triage module."""

import unittest
from unittest.mock import MagicMock

from falcon_mcp.client import FalconClient
from falcon_mcp.modules.triage import TriageModule


class TestHostTriageContext(unittest.TestCase):
    """Test cases for get_host_triage_context."""

    def setUp(self):
        self.mock_client = MagicMock(spec=FalconClient)
        self.module = TriageModule(self.mock_client)

    def test_host_triage_by_hostname(self):
        """Resolve hostname, fetch host details, and count recent detections."""
        # Mock 3 API calls: QueryDevicesByFilter, PostDeviceDetailsV2, GetQueriesAlertsV2
        query_response = {
            "status_code": 200,
            "body": {"resources": ["device-abc-123"]},
        }
        details_response = {
            "status_code": 200,
            "body": {"resources": [{
                "device_id": "device-abc-123",
                "hostname": "WORKSTATION-01",
                "local_ip": "10.0.0.5",
                "platform_name": "Windows",
                "os_version": "Windows 11",
                "status": "normal",
                "last_seen": "2025-05-20T10:00:00Z",
                "extra_field": "should_be_filtered",
                "some_other_field": "also_filtered",
            }]},
        }
        alerts_response = {
            "status_code": 200,
            "body": {"resources": ["alert1", "alert2", "alert3"]},
        }
        self.mock_client.command.side_effect = [query_response, details_response, alerts_response]

        result = self.module.get_host_triage_context(hostname="WORKSTATION-01")

        # Verify result has expected fields
        self.assertEqual(result["hostname"], "WORKSTATION-01")
        self.assertEqual(result["device_id"], "device-abc-123")
        self.assertEqual(result["recent_detection_count"], 3)

        # Verify extra fields are filtered out
        self.assertNotIn("extra_field", result)
        self.assertNotIn("some_other_field", result)

    def test_host_triage_requires_at_least_one_identifier(self):
        """Calling with no hostname and no device_id returns an error."""
        result = self.module.get_host_triage_context()

        self.assertIn("error", result)
        self.assertIn("at least one", result["error"].lower())

    def test_host_triage_by_device_id(self):
        """Skip hostname resolution when device_id is provided directly."""
        # Mock 2 API calls: PostDeviceDetailsV2, GetQueriesAlertsV2 (no QueryDevicesByFilter)
        details_response = {
            "status_code": 200,
            "body": {"resources": [{
                "device_id": "device-xyz-789",
                "hostname": "SERVER-02",
                "local_ip": "10.0.1.10",
                "platform_name": "Linux",
                "status": "contained",
                "last_seen": "2025-05-19T08:00:00Z",
            }]},
        }
        alerts_response = {
            "status_code": 200,
            "body": {"resources": []},
        }
        self.mock_client.command.side_effect = [details_response, alerts_response]

        result = self.module.get_host_triage_context(device_id="device-xyz-789")

        # Should only make 2 calls (no hostname resolution)
        self.assertEqual(self.mock_client.command.call_count, 2)
        first_call = self.mock_client.command.call_args_list[0]
        self.assertEqual(first_call[0][0], "PostDeviceDetailsV2")

        self.assertEqual(result["device_id"], "device-xyz-789")
        self.assertEqual(result["hostname"], "SERVER-02")
        self.assertEqual(result["recent_detection_count"], 0)


if __name__ == "__main__":
    unittest.main()
