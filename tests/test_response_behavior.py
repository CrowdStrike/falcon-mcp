#!/usr/bin/env python3
"""
Test script to verify the new token-based response handling behavior.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from falcon_mcp.common.response_handler import ResponseSizeConfig, handle_api_response


def test_token_thresholds():
    """Test that token-based decisions work correctly."""
    config = ResponseSizeConfig()

    # Test small response (should return directly)
    small_data = {"events": [{"id": i, "msg": "test"} for i in range(10)]}
    char_count = len(json.dumps(small_data))
    token_count = config.estimate_tokens(char_count)
    action = config.get_export_action(token_count)

    print(f"Small data: {char_count} chars, ~{token_count} tokens -> {action}")
    assert action == "direct_return", f"Expected direct_return, got {action}"

    # Test medium response (should warn)
    medium_data = {"events": [{"id": i, "msg": "x" * 100} for i in range(1000)]}
    char_count = len(json.dumps(medium_data))
    token_count = config.estimate_tokens(char_count)
    action = config.get_export_action(token_count)

    print(f"Medium data: {char_count} chars, ~{token_count} tokens -> {action}")
    assert action == "return_with_warning", f"Expected return_with_warning, got {action}"

    # Test large response (should force export)
    large_data = {
        "events": [
            {"id": i, "msg": "x" * 1000, "details": {"field": "x" * 500}} for i in range(5000)
        ]
    }
    char_count = len(json.dumps(large_data))
    token_count = config.estimate_tokens(char_count)
    action = config.get_export_action(token_count)

    print(f"Large data: {char_count} chars, ~{token_count} tokens -> {action}")
    assert action == "force_export", f"Expected force_export, got {action}"

    print("✅ All token threshold tests passed!")


def test_export_behaviors():
    """Test the different export behaviors."""

    # Small test data
    test_data = {"events": [{"id": i, "msg": "test"} for i in range(5)]}

    # Test "never" behavior
    result = handle_api_response(test_data, "test_op", export_behavior="never")
    assert result == test_data, "Never export should return original data"
    print("✅ 'never' export behavior works")

    # Test "smart" behavior with small data (should return directly)
    result = handle_api_response(test_data, "test_op", export_behavior="smart")
    assert result == test_data, "Smart export with small data should return original"
    print("✅ 'smart' export behavior works for small data")

    # Test "always" behavior (should export even small data)
    result = handle_api_response(test_data, "test_op", export_behavior="always")
    assert isinstance(result, dict) and result.get("handled"), "Always export should handle data"
    print("✅ 'always' export behavior works")


if __name__ == "__main__":
    print("Testing new token-based response handling...")

    try:
        test_token_thresholds()
        test_export_behaviors()
        print("\n🎉 All tests passed! The new token-based system is working correctly.")

        print("\n📊 Token Thresholds:")
        print(f"  Safe: ≤ {ResponseSizeConfig.MCP_SAFE_TOKEN_THRESHOLD:,} tokens")
        print(f"  Warning: ≤ {ResponseSizeConfig.MCP_WARNING_TOKEN_THRESHOLD:,} tokens")
        print(f"  Force Export: > {ResponseSizeConfig.MCP_WARNING_TOKEN_THRESHOLD:,} tokens")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
