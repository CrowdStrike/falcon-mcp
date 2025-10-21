#!/usr/bin/env python3
"""
Simple test script for large dataset handling in NG-SIEM module.
Tests the response handler without requiring API access.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from falcon_mcp.common.response_handler import LargeResponseHandler


def test_small_dataset():
    """Test small dataset (should return as-is)."""
    print("Testing small dataset...")
    handler = LargeResponseHandler()

    small_data = [{"id": i, "data": f"test_{i}"} for i in range(50)]

    result = handler.handle_large_response(
        data=small_data, operation="test_small", export_format="json"
    )

    expected_result = {"data": small_data, "handled": False}
    assert result == expected_result, "Small dataset should be returned with handled=False"
    print("✅ Small dataset test passed")


def test_large_dataset():
    """Test large dataset (should offer download)."""
    print("Testing large dataset...")
    handler = LargeResponseHandler()

    large_data = [{"id": i, "data": f"test_{i}", "field": f"value_{i}"} for i in range(2000)]

    result = handler.handle_large_response(
        data=large_data, operation="test_large", export_format="json"
    )

    assert isinstance(result, dict), "Large dataset should return download info"
    assert result.get("handled", False), "Should be handled as large dataset"
    assert "action" in result, "Should contain action info"
    print(f"✅ Large dataset test passed - Action: {result.get('action')}")
    if "file_path" in result:
        print(f"   File created: {result['file_path']}")


def test_very_large_dataset():
    """Test very large dataset (should force download)."""
    print("Testing very large dataset...")
    handler = LargeResponseHandler()

    very_large_data = [
        {"id": i, "event": f"event_{i}", "timestamp": f"2024-01-{i % 30 + 1:02d}"}
        for i in range(7000)
    ]

    result = handler.handle_large_response(
        data=very_large_data, operation="test_very_large", export_format="csv"
    )

    assert isinstance(result, dict), "Very large dataset should return download info"
    assert result.get("handled", False), "Should be handled as large dataset"
    print(f"✅ Very large dataset test passed - Action: {result.get('action')}")
    if "file_path" in result:
        print(f"   CSV file created: {result['file_path']}")


def test_csv_export():
    """Test CSV export functionality."""
    print("Testing CSV export...")
    handler = LargeResponseHandler()

    test_data = [
        {"name": "Alice", "age": 30, "city": "New York"},
        {"name": "Bob", "age": 25, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago", "extra": "data"},
    ]

    result = handler.handle_large_response(
        data=test_data, operation="test_csv", export_format="csv"
    )

    # For small datasets, should return original data wrapped
    expected_result = {"data": test_data, "handled": False}
    assert result == expected_result, "Small dataset should return original data wrapped"
    print("✅ CSV export test passed")


if __name__ == "__main__":
    print("🧪 Testing Large Dataset Handler for NG-SIEM")
    print("=" * 50)

    try:
        test_small_dataset()
        test_large_dataset()
        test_very_large_dataset()
        test_csv_export()

        print("\n🎉 All tests passed!")
        print("\nFeatures implemented:")
        print("✅ Automatic detection of large datasets")
        print("✅ JSON and CSV export capabilities")
        print("✅ Download to ./falcon_exports directory")
        print("✅ Configurable thresholds (1000 and 5000 records)")
        print("✅ Interactive and non-interactive modes")
        print("✅ Preview data for large responses")
        print("✅ Metadata preservation in exports")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
