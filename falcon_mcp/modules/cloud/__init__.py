# ruff: noqa: F401
"""
Cloud Security package for Falcon MCP Server.

This __init__.py is required. The registry and doc generator use pkgutil.iter_modules()
to discover modules, which only recognises directories as packages when __init__.py
is present. Without it, the cloud package is silently skipped and no cloud tools are
registered.
"""
