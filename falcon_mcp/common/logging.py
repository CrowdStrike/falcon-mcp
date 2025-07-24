"""
Logging configuration for Falcon MCP Server

This module provides logging utilities for the Falcon MCP server.
"""

import logging
import sys
from typing import Optional


def configure_logging(debug: bool = False, name: str = "falcon_mcp") -> logging.Logger:
    """Configure logging for the Falcon MCP server.

    Args:
        debug: Enable debug logging
        name: Logger name

    Returns:
        logging.Logger: Configured logger
    """
    log_level = logging.DEBUG if debug else logging.INFO

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set third-party loggers to a higher level to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # Get and return the logger for this application
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the specified name.

    Args:
        name: Logger name (defaults to "falcon_mcp")

    Returns:
        logging.Logger: Logger instance
    """
    logger_name = name if name else "falcon_mcp"
    return logging.getLogger(logger_name)
