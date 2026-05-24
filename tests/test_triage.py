"""Tests for the Triage module."""

import asyncio
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
            "body": {
                "resources": ["alert1"],
                "meta": {"pagination": {"total": 3}},
            },
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
            "body": {
                "resources": [],
                "meta": {"pagination": {"total": 0}},
            },
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


class TestDetectionTriage(unittest.TestCase):
    """Test cases for get_detection_triage."""

    def setUp(self):
        self.mock_client = MagicMock(spec=FalconClient)
        self.module = TriageModule(self.mock_client)

    def test_detection_triage_filters_to_summary(self):
        """Fetch detection and verify it is filtered to DETECTION_SUMMARY_FIELDS."""
        detection_data = {
            "status_code": 200,
            "body": {"resources": [{
                "timestamp": "2025-05-20T12:00:00Z",
                "created_timestamp": "2025-05-20T12:00:01Z",
                "status": "new",
                "severity_name": "High",
                "confidence": 90,
                "display_name": "Suspicious PowerShell",
                "description": "PowerShell with encoded command",
                "device": {
                    "device_id": "dev-001",
                    "hostname": "WKS-01",
                    "local_ip": "10.0.0.1",
                    "external_ip": "1.2.3.4",
                    "os_version": "Windows 11",
                    "tags": ["critical"],
                },
                "user_name": "jdoe",
                "filename": "powershell.exe",
                "cmdline": "powershell -enc ...",
                "parent_details": {"filename": "cmd.exe", "cmdline": "cmd /c ..."},
                "pattern_disposition_description": "Process killed",
                # Fields that should be filtered out
                "behaviors_processed": ["b1"],
                "internal_tracking_id": "track-999",
                "raw_event_data": {"huge": "blob"},
            }]},
        }
        self.mock_client.command.return_value = detection_data

        result = self.module.get_detection_triage(detection_id="ldt:dev-001:12345")

        # Verify expected fields are present
        self.assertEqual(result["status"], "new")
        self.assertEqual(result["severity_name"], "High")
        self.assertEqual(result["device"]["hostname"], "WKS-01")
        self.assertEqual(result["parent_details"]["filename"], "cmd.exe")

        # Verify extra fields are filtered out
        self.assertNotIn("behaviors_processed", result)
        self.assertNotIn("internal_tracking_id", result)
        self.assertNotIn("raw_event_data", result)


class TestProcessVerdictContext(unittest.TestCase):
    """Test cases for get_process_verdict_context."""

    def setUp(self):
        self.mock_client = MagicMock(spec=FalconClient)
        self.module = TriageModule(self.mock_client)

    def test_process_verdict_by_name(self):
        """Search for process by name and verify filtering to PROCESS_TELEMETRY_FIELDS."""
        start_response = {
            "status_code": 200,
            "body": {"id": "job-abc-123"},
        }
        poll_response = {
            "status_code": 200,
            "body": {
                "done": True,
                "events": [{
                    "@timestamp": "2025-05-20T10:00:00Z",
                    "ComputerName": "WKS-01",
                    "aid": "device-001",
                    "TargetProcessId": "1234",
                    "FileName": "suspicious.exe",
                    "FilePath": "\\Device\\HarddiskVolume3\\Users\\jdoe\\Downloads\\",
                    "CommandLine": "suspicious.exe --flag",
                    "SHA256HashData": "abc123def456",
                    "ParentBaseFileName": "explorer.exe",
                    "UserName": "jdoe",
                    # Fields that should be filtered out
                    "extra_ngsiem_field": "should_go",
                    "aip": "10.0.0.1",
                    "cid": "customer-id-123",
                }],
            },
        }
        self.mock_client.command.side_effect = [start_response, poll_response]

        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                self.module.get_process_verdict_context(
                    device_id="device-001",
                    process_name="suspicious.exe",
                    start="2025-05-20T00:00:00Z",
                )
            )
        finally:
            loop.close()

        # Result should be a list of filtered events
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertEqual(event["FileName"], "suspicious.exe")
        self.assertEqual(event["SHA256HashData"], "abc123def456")
        self.assertEqual(event["ParentBaseFileName"], "explorer.exe")

        # Verify extra fields are filtered out
        self.assertNotIn("extra_ngsiem_field", event)
        self.assertNotIn("aip", event)
        self.assertNotIn("cid", event)

    def test_process_verdict_requires_device_id(self):
        """Calling without device_id returns an error."""
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                self.module.get_process_verdict_context(
                    device_id="",
                    process_name="test.exe",
                    start="2025-05-20T00:00:00Z",
                )
            )
        finally:
            loop.close()

        self.assertIn("error", result)

    def test_process_verdict_requires_process_identifier(self):
        """Calling without process_name or pid returns an error."""
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                self.module.get_process_verdict_context(
                    device_id="device-001",
                    start="2025-05-20T00:00:00Z",
                )
            )
        finally:
            loop.close()

        self.assertIn("error", result)
        self.assertIn("at least one", result["error"].lower())


if __name__ == "__main__":
    unittest.main()
