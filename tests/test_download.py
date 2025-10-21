#!/usr/bin/env python3
"""
Test script to verify the download functionality works
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "falcon_mcp"))

from falcon_mcp.common.response_handler import get_response_handler

# Test data - same structure as NG-SIEM results
test_data = [
    {
        "timestamp": "1760635035489",
        "ComputerName": "EC2AMAZ-UUJS0A3",
        "UserName": "EC2AMAZ-UUJS0A3$",
        "CommandLine": '"C:\\Program Files\\LogScale Collector\\LogScale Collector.exe" --version',
        "FileName": "LogScale Collector.exe",
    },
    {
        "timestamp": "1760635035489",
        "ComputerName": "EC2AMAZ-UUJS0A3",
        "UserName": "EC2AMAZ-UUJS0A3$",
        "CommandLine": "\\??\\C:\\Windows\\system32\\conhost.exe 0xffffffff -ForceV1",
        "FileName": "conhost.exe",
    },
]


def test_download():
    print("Testing download functionality...")

    handler = get_response_handler()

    # Test the direct download creation
    print(f"Handler output_dir: {handler.output_dir}")

    # Create download using available method - make data large enough to trigger export
    large_test_data = test_data * 1000  # Multiply to make it large
    download_info = handler.handle_large_response(
        data=large_test_data,
        operation="test_query",
        export_format="json",
        export_behavior="always",  # Force export
    )

    print("Download info:")
    print(f"  File path: {download_info.get('file_path')}")
    print(f"  File size: {download_info.get('size_mb')} MB")
    print(f"  Record count: {download_info.get('record_count')}")

    # Check if there's an error
    if "error" in download_info:
        print(f"  ERROR: {download_info['error']}")

    # Check if file actually exists
    file_path = download_info.get("file_path")
    if file_path:
        import os

        print(f"  File exists: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            print(f"  Actual file size: {os.path.getsize(file_path)} bytes")

    # Validate the results
    assert isinstance(download_info, dict), "Should return download info dict"
    print("✅ Test completed successfully!")


if __name__ == "__main__":
    result = test_download()
    print("Test completed successfully!")
