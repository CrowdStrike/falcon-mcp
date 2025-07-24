"""
Pytest configuration file for the tests.
"""

import pytest


def pytest_addoption(parser):
    """
    Add the --run-e2e option to pytest.
    """
    parser.addoption(
        "--run-e2e", action="store_true", default=False, help="run e2e tests"
    )


def pytest_configure(config):
    """
    Register the e2e marker.
    """
    config.addinivalue_line("markers", "e2e: mark test as e2e to run")


def pytest_collection_modifyitems(config, items):
    """
    Skip e2e tests if --run-e2e is not given.
    """
    if config.getoption("--run-e2e"):
        return
    skip_e2e = pytest.mark.skip(reason="need --run-e2e option to run")
    for item in items:
        if "e2e" in item.keywords:
            item.add_marker(skip_e2e)


@pytest.fixture
def verbosity_level(request):
    """Return the verbosity level from pytest config."""
    return request.config.option.verbose
