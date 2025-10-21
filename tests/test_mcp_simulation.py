#!/usr/bin/env python3

"""
Test script that mimics exactly what the MCP execute_ngsiem_query does
to identify where the download logic is failing.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

from falcon_mcp.common.response_handler import handle_api_response

# Simulate the exact same data structure that comes from NG-SIEM
mock_results = {
    "results": {
        "events": [
            {
                "timestamp": "1760635987763",
                "ComputerName": "EC2AMAZ-O7QEC47",
                "UserName": "EC2AMAZ-O7QEC47$",
                "CommandLine": "/k echo {2997c41f-aaa8-11f0-bb12-06cbd97d3393}",
                "FileName": "cmd.exe",
            },
            {
                "timestamp": "1760636614884",
                "ComputerName": "EC2AMAZ-UUJS0A3",
                "UserName": "EC2AMAZ-UUJS0A3$",
                "CommandLine": '"C:\\Program Files\\LogScale Collector\\LogScale Collector.exe" --version',
                "FileName": "LogScale Collector.exe",
            },
        ]
    }
}


def test_mcp_simulation():
    print("=== Simulating MCP execute_ngsiem_query workflow ===")

    # Step 1: Extract events data (this is what the MCP function does)
    events_data = mock_results["results"]["events"]
    print(f"Events data extracted: {len(events_data)} events")

    # Step 2: Call handle_api_response exactly like the MCP function does

    print("\n--- Testing with export_behavior='always' ---")
    handled_response = handle_api_response(
        response=events_data,
        operation="execute_ngsiem_query",
        export_format="json",
        export_behavior="always",  # This should trigger download
        sample_events=3,
    )

    print(f"Response type: {type(handled_response)}")
    if isinstance(handled_response, dict):
        print(f"Response keys: {list(handled_response.keys())}")

        # Check the condition that MCP uses to detect handled responses
        has_response_summary = "response_summary" in handled_response
        has_download_action = (
            handled_response.get("response_summary", {}).get("action_taken")
            == "user_requested_download"
        )

        print(f"Has response_summary: {has_response_summary}")
        print(f"Has download action: {has_download_action}")

        if "download_info" in handled_response:
            download_info = handled_response["download_info"]
            print(f"Download info present: {download_info}")

            # Check if file exists
            file_path = download_info.get("file_path")
            if file_path and os.path.exists(file_path):
                print(f"✅ File created successfully: {file_path}")
                print(f"   File size: {os.path.getsize(file_path)} bytes")
            else:
                print(f"❌ File not found: {file_path}")
        else:
            print("❌ No download_info in response")
    else:
        print(f"❌ Response is not dict, it's: {type(handled_response)}")

    print("\n--- Testing with export_behavior='never' for comparison ---")
    handled_response_no_download = handle_api_response(
        response=events_data,
        operation="execute_ngsiem_query",
        export_format="json",
        export_behavior="never",
        sample_events=3,
    )

    print(f"No-download response type: {type(handled_response_no_download)}")
    if isinstance(handled_response_no_download, list):
        print(f"Returned list with {len(handled_response_no_download)} items")
    else:
        print(f"Returned dict with keys: {list(handled_response_no_download.keys())}")


if __name__ == "__main__":
    test_mcp_simulation()
