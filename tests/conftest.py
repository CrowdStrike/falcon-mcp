"""
Pytest configuration file for the tests.
"""

import pytest


def pytest_addoption(parser):
    """
    Add the --run-integration option to pytest.
    """
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests (requires real API credentials)",
    )


def pytest_configure(config):
    """
    Register the integration marker.
    """
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring real API credentials",
    )


def pytest_collection_modifyitems(config, items):
    """
    Skip integration tests if --run-integration flag is not given.
    """
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="need --run-integration option to run"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


@pytest.fixture
def verbosity_level(request):
    """Return the verbosity level from pytest config."""
    return request.config.option.verbose
