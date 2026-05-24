"""Tests for field filtering and truncation utilities."""
from falcon_mcp.common.utils import filter_fields, filter_records, truncate_string_fields

class TestFilterFields:
    def test_top_level_fields(self):
        record = {"hostname": "WS-1", "device_id": "abc", "extra": "noise"}
        result = filter_fields(record, ["hostname", "device_id"])
        assert result == {"hostname": "WS-1", "device_id": "abc"}

    def test_dot_notation_extracts_nested(self):
        record = {"device": {"hostname": "WS-1", "ip": "10.0.0.1"}, "status": "ok"}
        result = filter_fields(record, ["device.hostname", "status"])
        assert result == {"device": {"hostname": "WS-1"}, "status": "ok"}

    def test_deep_dot_notation(self):
        record = {"device_policies": {"sensor_update": {"uninstall_protection": "ENABLED"}}}
        result = filter_fields(record, ["device_policies.sensor_update.uninstall_protection"])
        assert result == {"device_policies": {"sensor_update": {"uninstall_protection": "ENABLED"}}}

    def test_unknown_fields_ignored(self):
        record = {"hostname": "WS-1"}
        result = filter_fields(record, ["hostname", "nonexistent", "also.missing"])
        assert result == {"hostname": "WS-1"}

    def test_empty_fields_list(self):
        record = {"hostname": "WS-1", "status": "ok"}
        result = filter_fields(record, [])
        assert result == {}

    def test_empty_record(self):
        result = filter_fields({}, ["hostname"])
        assert result == {}

    def test_multiple_nested_from_same_parent(self):
        record = {"device": {"hostname": "WS-1", "ip": "10.0.0.1", "mac": "aa:bb"}}
        result = filter_fields(record, ["device.hostname", "device.ip"])
        assert result == {"device": {"hostname": "WS-1", "ip": "10.0.0.1"}}

    def test_preserves_value_types(self):
        record = {"count": 42, "active": True, "tags": ["a", "b"], "meta": None}
        result = filter_fields(record, ["count", "active", "tags", "meta"])
        assert result == {"count": 42, "active": True, "tags": ["a", "b"], "meta": None}

class TestFilterRecords:
    def test_filters_each_record(self):
        records = [
            {"hostname": "WS-1", "extra": "a"},
            {"hostname": "WS-2", "extra": "b"},
        ]
        result = filter_records(records, ["hostname"])
        assert result == [{"hostname": "WS-1"}, {"hostname": "WS-2"}]

    def test_empty_list(self):
        assert filter_records([], ["hostname"]) == []


class TestTruncateStringFields:
    def test_truncates_long_string(self):
        record = {"cmd": "a" * 100}
        result = truncate_string_fields(record, max_length=50)
        assert result["cmd"] == "a" * 50 + " [truncated, full_len=100]"

    def test_preserves_short_string(self):
        record = {"cmd": "short"}
        result = truncate_string_fields(record, max_length=50)
        assert result["cmd"] == "short"

    def test_exact_boundary_not_truncated(self):
        record = {"cmd": "a" * 50}
        result = truncate_string_fields(record, max_length=50)
        assert result["cmd"] == "a" * 50

    def test_non_string_values_unchanged(self):
        record = {"count": 42, "active": True, "tags": ["a", "b"], "meta": None}
        result = truncate_string_fields(record, max_length=10)
        assert result == record

    def test_nested_dict_truncation(self):
        record = {"outer": {"cmd": "a" * 100, "ok": "short"}}
        result = truncate_string_fields(record, max_length=50)
        assert result["outer"]["cmd"] == "a" * 50 + " [truncated, full_len=100]"
        assert result["outer"]["ok"] == "short"

    def test_empty_record(self):
        assert truncate_string_fields({}, max_length=50) == {}
