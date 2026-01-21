"""
Pytest configuration file for the tests.
"""

import pytest


def pytest_addoption(parser):
    """
    Add the --run-e2e and --run-integration options to pytest.
    """
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="run e2e tests",
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests (requires real API credentials)",
    )


def pytest_configure(config):
    """
    Register the e2e and integration markers.
    """
    config.addinivalue_line("markers", "e2e: mark test as e2e to run")
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test requiring real API credentials",
    )


def pytest_collection_modifyitems(config, items):
    """
    Skip e2e and integration tests if their respective flags are not given.
    """
    if not config.getoption("--run-e2e"):
        skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)

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
