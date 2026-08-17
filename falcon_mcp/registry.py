"""
Module registry for Falcon MCP Server

This module provides a registry of available modules for the Falcon MCP server.
"""

from __future__ import annotations

import importlib
import os
import pkgutil
from typing import TYPE_CHECKING

from falcon_mcp.common.logging import get_logger

if TYPE_CHECKING:
    from falcon_mcp.modules.base import BaseModule

logger = get_logger(__name__)

# This will be populated by the discovery process
AVAILABLE_MODULES: dict[str, type[BaseModule]] = {}


def _register_from_module(import_path: str, log_context: str) -> None:
    """Import a module and register any *Module classes found in it."""
    submodule = importlib.import_module(import_path)
    for attr_name in dir(submodule):
        if not attr_name.endswith("Module") or attr_name == "BaseModule":
            continue
        module_class = getattr(submodule, attr_name)
        if module_class.__module__ != submodule.__name__:
            continue
        module_name = attr_name.lower().replace("module", "")
        AVAILABLE_MODULES[module_name] = module_class
        logger.debug("Discovered module: %s (%s)", module_name, log_context)


def discover_modules() -> None:
    """Discover available modules by scanning the modules directory."""
    current_dir = os.path.dirname(__file__)
    modules_path = os.path.join(current_dir, "modules")

    for _, name, is_pkg in pkgutil.iter_modules([modules_path]):
        if name == "base":
            continue

        if is_pkg:
            pkg_path = os.path.join(modules_path, name)
            for _, subname, sub_is_pkg in pkgutil.iter_modules([pkg_path]):
                if sub_is_pkg or subname == "__init__":
                    continue
                _register_from_module(
                    f"falcon_mcp.modules.{name}.{subname}",
                    f"from {name}.{subname}",
                )
        else:
            _register_from_module(f"falcon_mcp.modules.{name}", name)


def get_available_modules() -> dict[str, type[BaseModule]]:
    """Get available modules dict, discovering if needed (lazy loading).

    Returns:
        Dict mapping module names to module classes
    """
    if not AVAILABLE_MODULES:
        logger.debug("No modules discovered yet, performing lazy discovery")
        discover_modules()
    return AVAILABLE_MODULES


def get_module_names() -> list[str]:
    """Get the names of all registered modules, discovering if needed (lazy loading).

    Returns:
        List of module names
    """
    return list(get_available_modules().keys())


def get_tool_module_map() -> dict[str, str]:
    """Resolve which module to load for a given tool name, before any module loads.

    Serves the two startup decisions that must happen before a client exists:
    rejecting allow/deny-list names that match no tool, and pulling in the modules
    that own the names an operator allow-listed. Not a filtering input — which of a
    loaded module's tools survive is decided after registration, from the tools the
    server actually holds.

    Registration only wires bound methods onto a throwaway server, so this makes no
    Falcon API calls and needs no authenticated client.

    Returns:
        Dict mapping prefixed tool names to module names
    """
    # Imported here to keep registry out of the modules -> BaseModule -> client cycle.
    from mcp.server.fastmcp import FastMCP

    scratch = FastMCP("tool-name-probe")
    mapping: dict[str, str] = {}
    for module_name, module_class in get_available_modules().items():
        module = module_class(None)  # type: ignore[arg-type]
        module.register_tools(scratch)
        for tool_name in module.tools:
            mapping[tool_name] = module_name
    return mapping
