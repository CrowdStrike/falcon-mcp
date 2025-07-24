"""
Tests for the logging utilities.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch

from falcon_mcp.common.logging import configure_logging, get_logger


class TestLoggingUtils(unittest.TestCase):
    """Test cases for the logging utilities."""

    @patch("falcon_mcp.common.logging.logging.basicConfig")
    @patch("falcon_mcp.common.logging.logging.getLogger")
    def test_configure_logging_debug(self, mock_get_logger, mock_basic_config):
        """Test configuring logging with debug enabled."""
        # Setup mock
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call configure_logging with debug=True
        logger = configure_logging(debug=True, name="test_logger")

        # Verify basicConfig was called with DEBUG level
        mock_basic_config.assert_called_once()
        _args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs["level"], logging.DEBUG)

        # Verify logger was configured correctly
        mock_get_logger.assert_called_with("test_logger")
        mock_logger.setLevel.assert_called_with(logging.DEBUG)

        # Verify logger was returned
        self.assertEqual(logger, mock_logger)

    @patch("falcon_mcp.common.logging.logging.basicConfig")
    @patch("falcon_mcp.common.logging.logging.getLogger")
    def test_configure_logging_info(self, mock_get_logger, mock_basic_config):
        """Test configuring logging with debug disabled."""
        # Setup mock
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call configure_logging with debug=False
        logger = configure_logging(debug=False, name="test_logger")

        # Verify basicConfig was called with INFO level
        mock_basic_config.assert_called_once()
        _args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs["level"], logging.INFO)

        # Verify logger was configured correctly
        mock_get_logger.assert_called_with("test_logger")
        mock_logger.setLevel.assert_called_with(logging.INFO)

        # Verify logger was returned
        self.assertEqual(logger, mock_logger)

    @patch("falcon_mcp.common.logging.logging.getLogger")
    def test_get_logger_with_name(self, mock_get_logger):
        """Test getting a logger with a specific name."""
        # Setup mock
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call get_logger with a name
        logger = get_logger("test_logger")

        # Verify getLogger was called with the correct name
        mock_get_logger.assert_called_with("test_logger")

        # Verify logger was returned
        self.assertEqual(logger, mock_logger)

    @patch("falcon_mcp.common.logging.logging.getLogger")
    def test_get_logger_default_name(self, mock_get_logger):
        """Test getting a logger with the default name."""
        # Setup mock
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call get_logger without a name
        logger = get_logger()

        # Verify getLogger was called with the default name
        mock_get_logger.assert_called_with("falcon_mcp")

        # Verify logger was returned
        self.assertEqual(logger, mock_logger)


if __name__ == "__main__":
    unittest.main()
