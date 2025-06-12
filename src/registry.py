"""
Module registry for Falcon MCP Server

This module provides a registry of available modules for the Falcon MCP server.
"""
import importlib
import os
import pkgutil
from typing import Dict, Type, List

from .common.logging import get_logger

logger = get_logger(__name__)

# Forward reference for type hints
# Using string to avoid circular import
MODULE_TYPE = 'BaseModule'  # type: ignore


# This will be populated by the discovery process
AVAILABLE_MODULES: Dict[str, Type[MODULE_TYPE]] = {}


def discover_modules():
    """Discover available modules by scanning the modules directory."""
    # Get the path to the modules directory
    current_dir = os.path.dirname(__file__)
    modules_path = os.path.join(current_dir, 'modules')

    # Scan for module files
    for _, name, is_pkg in pkgutil.iter_modules([modules_path]):
        if not is_pkg and name != 'base':  # Skip base.py and packages
            # Import the module
            module = importlib.import_module(f'src.modules.{name}')

            # Look for *Module classes
            for attr_name in dir(module):
                if attr_name.endswith('Module') and attr_name != 'BaseModule':
                    # Get the class
                    module_class = getattr(module, attr_name)
                    # Register it
                    module_name = attr_name.lower().replace('module', '')
                    AVAILABLE_MODULES[module_name] = module_class
                    logger.debug("Discovered module: %s", module_name)


def register_module(name: str, module_class: Type[MODULE_TYPE]) -> None:
    """Register a module in the registry.

    Args:
        name: The name of the module
        module_class: The module class
    """
    AVAILABLE_MODULES[name] = module_class


def get_module_names() -> List[str]:
    """Get the names of all registered modules.

    Returns:
        List of module names
    """
    return list(AVAILABLE_MODULES.keys())
