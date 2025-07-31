"""
Tests for the utility functions.
"""

import unittest
from unittest.mock import patch

from falcon_mcp.common.utils import (
    extract_first_resource,
    extract_resources,
    filter_none_values,
    generate_table,
    prepare_api_parameters,
)


class TestUtilFunctions(unittest.TestCase):
    """Test cases for the utility functions."""

    def test_filter_none_values(self):
        """Test filter_none_values function."""
        # Dictionary with None values
        data = {
            "key1": "value1",
            "key2": None,
            "key3": 0,
            "key4": False,
            "key5": "",
            "key6": None,
        }

        filtered = filter_none_values(data)

        # Verify None values were removed
        self.assertEqual(
            filtered,
            {
                "key1": "value1",
                "key3": 0,
                "key4": False,
                "key5": "",
            },
        )

        # Empty dictionary
        self.assertEqual(filter_none_values({}), {})

        # Dictionary without None values
        data = {"key1": "value1", "key2": 2}
        self.assertEqual(filter_none_values(data), data)

    def test_prepare_api_parameters(self):
        """Test prepare_api_parameters function."""
        # Parameters with None values
        params = {
            "filter": "name:test",
            "limit": 100,
            "offset": None,
            "sort": None,
        }

        prepared = prepare_api_parameters(params)

        # Verify None values were removed
        self.assertEqual(prepared, {"filter": "name:test", "limit": 100})

        # Empty parameters
        self.assertEqual(prepare_api_parameters({}), {})

        # Parameters without None values
        params = {"filter": "name:test", "limit": 100}
        self.assertEqual(prepare_api_parameters(params), params)

    def test_extract_resources(self):
        """Test extract_resources function."""
        # Success response with resources
        response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"},
                ]
            },
        }

        resources = extract_resources(response)

        # Verify resources were extracted
        self.assertEqual(
            resources,
            [
                {"id": "resource1", "name": "Resource 1"},
                {"id": "resource2", "name": "Resource 2"},
            ],
        )

        # Success response with empty resources
        response = {"status_code": 200, "body": {"resources": []}}

        resources = extract_resources(response)

        # Verify empty list was returned
        self.assertEqual(resources, [])

        # Success response with empty resources and default
        default = [{"id": "default", "name": "Default Resource"}]
        resources = extract_resources(response, default=default)

        # Verify default was returned
        self.assertEqual(resources, default)

        # Error response
        response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        resources = extract_resources(response)

        # Verify empty list was returned
        self.assertEqual(resources, [])

        # Error response with default
        resources = extract_resources(response, default=default)

        # Verify default was returned
        self.assertEqual(resources, default)

    @patch("falcon_mcp.common.utils._format_error_response")
    def test_extract_first_resource(self, mock_format_error):
        """Test extract_first_resource function."""
        # Mock format_error_response
        mock_format_error.return_value = {"error": "Resource not found"}

        # Success response with resources
        response = {
            "status_code": 200,
            "body": {
                "resources": [
                    {"id": "resource1", "name": "Resource 1"},
                    {"id": "resource2", "name": "Resource 2"},
                ]
            },
        }

        resource = extract_first_resource(response, "TestOperation")

        # Verify first resource was returned
        self.assertEqual(resource, {"id": "resource1", "name": "Resource 1"})

        # Success response with empty resources
        response = {"status_code": 200, "body": {"resources": []}}

        resource = extract_first_resource(
            response, "TestOperation", not_found_error="Custom error"
        )

        # Verify error response was returned
        mock_format_error.assert_called_with("Custom error", operation="TestOperation")
        self.assertEqual(resource, {"error": "Resource not found"})

        # Error response
        response = {
            "status_code": 400,
            "body": {"errors": [{"message": "Bad request"}]},
        }

        resource = extract_first_resource(response, "TestOperation")

        # Verify error response was returned
        mock_format_error.assert_called_with(
            "Resource not found", operation="TestOperation"
        )
        self.assertEqual(resource, {"error": "Resource not found"})

    def test_generate_table(self):
        """Test generate_table function."""
        # Test data with headers as the first row
        data = [
            # Header row
            (" Name", "    Type", "Operators ", "Description    ", "Extra"),
            # Data rows
            (
                "test_string",
                "String",
                "Yes",
                """
This is a test description.
It has multiple lines.
For testing purposes.
"""
            ),
            (
                "test_bool",
                "\nBoolean", 
                "\nYes",
                "This is a test description.\nIt has multiple lines.\nFor testing purposes.",
                True,
            ),
            (
                "test_none",
                " None",
                "   No",
                """
                    Multi line description.
                    Hello
                """,
                None,
            ),
            (
                "test_number",
                "Number ",
                "No   ",
                "Single line description.",
                42,
            )
        ]

        # Generate table
        table = generate_table(data)

        # Expected table format (with exact spacing and formatting)
        expected_table = """|Name|Type|Operators|Description|Extra|
|-|-|-|-|-|
|test_string|String|Yes|This is a test description. It has multiple lines. For testing purposes.||
|test_bool|Boolean|Yes|This is a test description. It has multiple lines. For testing purposes.|true|
|test_none|None|No|Multi line description. Hello||
|test_number|Number|No|Single line description.|42|"""

        # Compare the generated table with the expected table
        self.assertEqual(table, expected_table)

        # Split into lines for easier assertion
        lines = table.split('\n')

        # Check basic structure
        self.assertEqual(len(lines), 6)  # header + separator + 4 data rows

        # Check header row exists and contains all headers (stripped of spaces)
        header_row = lines[0]
        for header in data[0]:
            self.assertIn(header.strip(), header_row)

        # Check for multi-line handling - descriptions should be combined with spaces
        self.assertIn("This is a test description. It has multiple lines. For testing purposes.", lines[2])

        # Check for proper pipe character usage
        for i in range(6):  # Check all lines
            self.assertTrue(lines[i].startswith('|'))
            self.assertTrue(lines[i].endswith('|'))
            # Should have exactly 6 | characters (start, end, and 4 column separators)
            self.assertEqual(lines[i].count('|'), 6)

    def test_generate_table_with_non_string_headers(self):
        """Test generate_table function with non-string headers."""
        # Test data with non-string headers
        data = [
            # Header row with a non-string value
            ("Name", 123, "Operators", "Description", "Extra"),
            # Data rows
            (
                "test_string",
                "String",
                "Yes",
                "This is a test description.",
                None,
            ),
        ]

        # Verify that TypeError is raised
        with self.assertRaises(TypeError) as context:
            generate_table(data)

        # Check the error message
        self.assertIn("Header values must be strings", str(context.exception))
        self.assertIn("got int", str(context.exception))

    def test_generate_table_with_single_column(self):
        """Test generate_table function with a single column."""
        # Test data with a single column
        data = [
            # Header row with a single value
            ("Name",),
            # Data rows with a single value
            ("test_string",),
            ("test_bool",),
            ("test_none",),
        ]

        # Generate table
        table = generate_table(data)

        # Expected table format (with exact spacing and formatting)
        expected_table = """|Name|
|-|
|test_string|
|test_bool|
|test_none|"""

        # Compare the generated table with the expected table
        self.assertEqual(table, expected_table)

        # Split into lines for easier assertion
        lines = table.split('\n')

        # Check basic structure
        self.assertEqual(len(lines), 5)  # header + separator + 3 data rows

        # Check header row exists and contains the header
        header_row = lines[0]
        self.assertEqual(header_row, "|Name|")

        # Check separator row
        self.assertEqual(lines[1], "|-|")

        # Check data rows exist with correct content
        self.assertEqual(lines[2], "|test_string|")
        self.assertEqual(lines[3], "|test_bool|")
        self.assertEqual(lines[4], "|test_none|")

        # Check for proper pipe character usage
        for i in range(5):  # Check all lines
            self.assertTrue(lines[i].startswith('|'))
            self.assertTrue(lines[i].endswith('|'))
            # Should have exactly 2 | characters (start and end)
            self.assertEqual(lines[i].count('|'), 2)
            
    def test_generate_table_with_empty_header_row(self):
        """Test generate_table function with an empty header row."""
        # Test data with an empty header row
        data = [
            # Empty header row
            (),
            # Data rows
            ("test_string",),
        ]

        # Verify that ValueError is raised
        with self.assertRaises(ValueError) as context:
            generate_table(data)
        
        # Check the error message
        self.assertIn("Header row cannot be empty", str(context.exception))
        
    def test_generate_table_with_insufficient_data(self):
        """Test generate_table function with insufficient data."""
        # Test data with only a header row and no data rows
        data = [
            # Header row
            ("Name", "Type"),
        ]

        # Verify that TypeError is raised
        with self.assertRaises(TypeError) as context:
            generate_table(data)
        
        # Check the error message
        self.assertIn("Need at least 2 items", str(context.exception))
        
        # Test with empty data
        with self.assertRaises(TypeError) as context:
            generate_table([])
        
        # Check the error message
        self.assertIn("Need at least 2 items", str(context.exception))


if __name__ == "__main__":
    unittest.main()
