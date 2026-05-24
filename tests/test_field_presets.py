"""Tests for SOC field preset constants."""
from falcon_mcp.common.field_presets import (
    AWS_CLOUDTRAIL_FIELDS, AWS_GUARDDUTY_FIELDS,
    DETECTION_SUMMARY_FIELDS, ENTRA_SIGNIN_FIELDS,
    FILE_DETECTION_CONTEXT_FIELDS, HOST_SUMMARY_FIELDS,
    LOGON_TELEMETRY_FIELDS, NETWORK_TELEMETRY_FIELDS, PE_METADATA_FIELDS,
    PROCESS_TELEMETRY_FIELDS, ZSCALER_ZIA_FIELDS,
)

ALL_PRESETS = {
    "DETECTION_SUMMARY_FIELDS": DETECTION_SUMMARY_FIELDS,
    "HOST_SUMMARY_FIELDS": HOST_SUMMARY_FIELDS,
    "PROCESS_TELEMETRY_FIELDS": PROCESS_TELEMETRY_FIELDS,
    "LOGON_TELEMETRY_FIELDS": LOGON_TELEMETRY_FIELDS,
    "NETWORK_TELEMETRY_FIELDS": NETWORK_TELEMETRY_FIELDS,
    "FILE_DETECTION_CONTEXT_FIELDS": FILE_DETECTION_CONTEXT_FIELDS,
    "PE_METADATA_FIELDS": PE_METADATA_FIELDS,
    "ENTRA_SIGNIN_FIELDS": ENTRA_SIGNIN_FIELDS,
    "ZSCALER_ZIA_FIELDS": ZSCALER_ZIA_FIELDS,
    "AWS_CLOUDTRAIL_FIELDS": AWS_CLOUDTRAIL_FIELDS,
    "AWS_GUARDDUTY_FIELDS": AWS_GUARDDUTY_FIELDS,
}

class TestFieldPresets:
    def test_all_presets_are_non_empty_lists(self):
        for name, preset in ALL_PRESETS.items():
            assert isinstance(preset, list), f"{name} is not a list"
            assert len(preset) > 0, f"{name} is empty"

    def test_all_presets_contain_strings(self):
        for name, preset in ALL_PRESETS.items():
            for field in preset:
                assert isinstance(field, str), f"{name} contains non-string: {field}"

    def test_no_duplicate_fields(self):
        for name, preset in ALL_PRESETS.items():
            assert len(preset) == len(set(preset)), f"{name} has duplicate fields"

    def test_detection_has_expected_count(self):
        assert len(DETECTION_SUMMARY_FIELDS) == 25

    def test_host_has_expected_count(self):
        assert len(HOST_SUMMARY_FIELDS) == 24

    def test_host_contains_key_soc_fields(self):
        for field in ["hostname", "device_id", "last_seen", "filesystem_containment_status"]:
            assert field in HOST_SUMMARY_FIELDS, f"Missing key SOC field: {field}"

    def test_detection_contains_key_soc_fields(self):
        for field in ["severity_name", "cmdline", "device.hostname", "pattern_disposition_description"]:
            assert field in DETECTION_SUMMARY_FIELDS, f"Missing key SOC field: {field}"
