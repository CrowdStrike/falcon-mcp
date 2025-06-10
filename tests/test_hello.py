"""Tests for hello world functionality."""

import pytest
from src.core.hello import generate_hello_message


def test_generate_hello_message_default():
    """Test hello message generation with default name."""
    result = generate_hello_message()
    expected = "Hello, World! This is a simple MCP server using FastMCP."
    assert result == expected


def test_generate_hello_message_custom_name():
    """Test hello message generation with custom name."""
    result = generate_hello_message("Alice")
    expected = "Hello, Alice! This is a simple MCP server using FastMCP."
    assert result == expected


def test_generate_hello_message_empty_name():
    """Test hello message generation with empty name."""
    result = generate_hello_message("")
    expected = "Hello, ! This is a simple MCP server using FastMCP."
    assert result == expected 