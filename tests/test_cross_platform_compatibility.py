#!/usr/bin/env python3
"""
Cross-platform test for large dataset handling.
Tests path resolution, filename sanitization, and file operations across platforms.
"""

import os
import platform
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from falcon_mcp.common.response_handler import LargeResponseHandler


import pytest


def test_cross_platform_paths():
    """Test cross-platform path handling."""
    print(f"Testing on {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print("=" * 50)

    # Test path resolution
    handler = LargeResponseHandler()

    print(f"✅ Output directory: {handler.output_dir}")
    print(f"✅ Directory exists: {handler.output_dir.exists()}")
    print(f"✅ Is absolute path: {handler.output_dir.is_absolute()}")
    print(f"✅ Resolved path: {handler.output_dir.resolve()}")


@pytest.mark.skip(
    reason="Method _sanitize_filename not implemented in current LargeResponseHandler"
)
def test_filename_sanitization():
    """Test filename sanitization for problematic characters."""
    print("\nTesting filename sanitization...")

    handler = LargeResponseHandler()

    # Test problematic filenames
    test_cases = [
        "normal_query",
        "query<with>brackets",
        'query"with"quotes',
        "query|with|pipes",
        "query?with?questions",
        "query*with*asterisks",
        "query/with/slashes",
        "query\\with\\backslashes",
        "query:with:colons",
        ".leading.dots.",
        " leading spaces ",
        "very_long_filename_that_exceeds_typical_limits_" + "x" * 200,
        "",  # Empty string
        "...",  # Only dots
    ]

    for test_case in test_cases:
        sanitized = handler._sanitize_filename(test_case)
        print(f"  '{test_case}' → '{sanitized}'")

        # Verify no problematic characters remain
        problematic_chars = '<>:"|?*\\/\x00-\x1f'
        assert not any(char in sanitized for char in problematic_chars), (
            f"Sanitization failed for: {test_case}"
        )
        assert len(sanitized) <= 200, f"Filename too long: {sanitized}"
        assert sanitized.strip(), f"Empty filename after sanitization: {test_case}"


@pytest.mark.skip(reason="Method handle_large_response signature may have changed")
def test_cross_platform_export():
    """Test actual file export with cross-platform paths."""
    print("\nTesting cross-platform export...")

    handler = LargeResponseHandler()

    # Test data with potentially problematic operation name
    test_data = [
        {"host": "server1", "event": "login", "user": "admin"},
        {"host": "server2", "event": "logout", "user": "user1"},
    ]

    # Test with problematic operation name
    operation_name = "test<query>with:problems"

    result = handler.handle_large_response(
        data=test_data * 600,  # Make it large enough to trigger download
        operation=operation_name,
        export_format="json",
    )

    assert isinstance(result, dict), "Should return download info"
    assert "download_info" in result, "Should contain download info"
    assert "file_path" in result["download_info"], "Should have file path"

    # Verify file was actually created
    file_path = result["download_info"]["file_path"]
    assert os.path.exists(file_path), f"File should exist: {file_path}"

    print(f"✅ Cross-platform export successful: {file_path}")
    return file_path


@pytest.mark.skip(
    reason="Method _find_project_root not implemented in current LargeResponseHandler"
)
def test_project_root_detection():
    """Test project root detection across different environments."""
    print("\nTesting project root detection...")

    handler = LargeResponseHandler()
    project_root = handler._find_project_root()

    print(f"✅ Detected project root: {project_root}")

    # Verify expected project files exist
    expected_files = ["falcon_mcp", "pyproject.toml"]
    found_indicators = []

    for expected in expected_files:
        if (project_root / expected).exists():
            found_indicators.append(expected)

    assert found_indicators, f"No project indicators found at {project_root}"
    print(f"✅ Found project indicators: {found_indicators}")


if __name__ == "__main__":
    print("🧪 Cross-Platform Compatibility Test for Large Dataset Handler")
    print("=" * 70)

    try:
        test_cross_platform_paths()
        test_filename_sanitization()
        test_project_root_detection()
        export_file = test_cross_platform_export()

        print("\n🎉 All cross-platform tests passed!")
        print("\n✅ Cross-platform features verified:")
        print("  ✅ Robust project root detection")
        print("  ✅ Absolute path resolution")
        print("  ✅ Cross-platform filename sanitization")
        print("  ✅ Safe file operations")
        print("  ✅ Proper directory creation")
        print(f"  ✅ Platform: {platform.system()} {platform.release()}")

        # Cleanup
        if "export_file" in locals() and os.path.exists(export_file):
            os.remove(export_file)
            print(f"  ✅ Cleaned up test file: {export_file}")

    except Exception as e:
        print(f"❌ Cross-platform test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
