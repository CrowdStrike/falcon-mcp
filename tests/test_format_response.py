"""Tests for format_response TOON wrapper."""
from falcon_mcp.common.utils import format_response

class TestFormatResponse:
    def test_json_format_returns_list_unchanged(self):
        records = [{"hostname": "WS-1"}, {"hostname": "WS-2"}]
        result = format_response(records, "json")
        assert result == records

    def test_toon_format_converts_list(self):
        records = [{"hostname": "WS-1", "status": "ok"}, {"hostname": "WS-2", "status": "ok"}]
        result = format_response(records, "toon")
        assert isinstance(result, str)
        assert "WS-1" in result
        assert "WS-2" in result

    def test_toon_single_record_stays_list(self):
        records = [{"hostname": "WS-1"}]
        result = format_response(records, "toon")
        assert isinstance(result, list)

    def test_toon_empty_list_stays_list(self):
        result = format_response([], "toon")
        assert result == []

    def test_non_list_input_passthrough(self):
        error = {"error": "something broke"}
        result = format_response(error, "json")
        assert result == error
