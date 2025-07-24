"""Base class for E2E tests."""

import asyncio
import atexit
import json
import os
import threading
import time
import unittest
from typing import Any
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

from falcon_mcp.server import FalconMCPServer

# Load environment variables from .env file for local development
load_dotenv()

# Default models to test against
DEFAULT_MODLES_TO_TEST = ["gpt-4.1-mini", "gpt-4o-mini"]
# Default number of times to run each test
DEFAULT_RUNS_PER_TEST = 2
# Default success threshold for passing a test
DEFAULT_SUCCESS_TRESHOLD = 0.7

# Models to test against
MODELS_TO_TEST = os.getenv("MODELS_TO_TEST", ",".join(DEFAULT_MODLES_TO_TEST)).split(
    ","
)
# Number of times to run each test
RUNS_PER_TEST = int(os.getenv("RUNS_PER_TEST", str(DEFAULT_RUNS_PER_TEST)))
# Success threshold for passing a test
SUCCESS_THRESHOLD = float(os.getenv("SUCCESS_TRESHOLD", str(DEFAULT_SUCCESS_TRESHOLD)))


# Module-level singleton for shared server resources
class SharedTestServer:
    """Singleton class to manage shared test server resources."""

    instance = None
    initialized = False

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if not self.initialized:
            # Group server-related attributes
            self.server_config = {
                "thread": None,
                "client": None,
                "loop": None,
            }

            # Group patching-related attributes
            self.patchers = {
                "env": None,
                "api": None,
                "mock_api_instance": None,
            }

            # Group test configuration
            self.test_config = {
                "results": [],
                "verbosity_level": 0,
                "base_url": os.getenv("OPENAI_BASE_URL"),
                "models_to_test": MODELS_TO_TEST,
            }

            self._cleanup_registered = False

    def initialize(self):
        """Initialize the shared server and test environment."""
        if self.initialized:
            return

        print("Initializing shared FalconMCP server for E2E tests...")

        self.server_config["loop"] = asyncio.new_event_loop()
        asyncio.set_event_loop(self.server_config["loop"])

        self.patchers["env"] = patch.dict(
            os.environ,
            {
                "FALCON_CLIENT_ID": "test-client-id",
                "FALCON_CLIENT_SECRET": "test-client-secret",
                "FALCON_BASE_URL": "https://api.test.crowdstrike.com",
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "test-openai-key"),
            },
        )
        self.patchers["env"].start()

        self.patchers["api"] = patch("falcon_mcp.client.APIHarnessV2")
        mock_apiharness_class = self.patchers["api"].start()

        self.patchers["mock_api_instance"] = MagicMock()
        self.patchers["mock_api_instance"].login.return_value = True
        self.patchers["mock_api_instance"].token_valid.return_value = True
        mock_apiharness_class.return_value = self.patchers["mock_api_instance"]

        server = FalconMCPServer(debug=False)
        self.server_config["thread"] = threading.Thread(
            target=server.run, args=("sse",)
        )
        self.server_config["thread"].daemon = True
        self.server_config["thread"].start()
        time.sleep(2)  # Wait for the server to initialize

        server_config = {"mcpServers": {"falcon": {"url": "http://127.0.0.1:8000/sse"}}}
        self.server_config["client"] = MCPClient(config=server_config)

        self.__class__.initialized = True

        # Register cleanup function to run when Python exits (only once)
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True

        print("Shared FalconMCP server initialized successfully.")

    def cleanup(self):
        """Clean up the shared server and test environment."""
        if not self.initialized:
            return

        print("Cleaning up shared FalconMCP server...")

        try:
            # Write test results to file
            with open("test_results.json", "w", encoding="utf-8") as f:
                json.dump(self.test_config["results"], f, indent=4)

            if self.patchers["api"]:
                try:
                    self.patchers["api"].stop()
                except (RuntimeError, AttributeError) as e:
                    print(f"Warning: API patcher cleanup error: {e}")

            if self.patchers["env"]:
                try:
                    self.patchers["env"].stop()
                except (RuntimeError, AttributeError) as e:
                    print(f"Warning: Environment patcher cleanup error: {e}")

            if (
                self.server_config["loop"]
                and not self.server_config["loop"].is_closed()
            ):
                try:
                    self.server_config["loop"].close()
                    asyncio.set_event_loop(None)
                except RuntimeError as e:
                    print(f"Warning: Event loop cleanup error: {e}")

            # Reset state
            self.__class__.initialized = False
            self._cleanup_registered = False

            print("Shared FalconMCP server cleanup completed.")
        except (IOError, OSError) as e:
            print(f"Error during cleanup: {e}")
            # Still reset the state even if cleanup partially failed
            self.__class__.initialized = False
            self._cleanup_registered = False


# Global singleton instance
_shared_server = SharedTestServer()


def ensure_dict(data: Any) -> dict:
    """
    Return input if it is a dict, otherwise, attempt to convert it to a dict using json.loads
    """
    if isinstance(data, dict):
        return data
    return json.loads(data)


class BaseE2ETest(unittest.TestCase):
    """
    Base class for end-to-end tests for the Falcon MCP Server.

    This class sets up a live server in a separate thread, mocks the Falcon API,
    and provides helper methods for running tests with an MCP client and agent.

    The server is shared across all test classes that inherit from this base class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = None
        self.agent = None

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for the entire class."""
        # Initialize the shared server
        _shared_server.initialize()

        # Set instance variables to point to shared resources
        cls.test_results = _shared_server.test_config["results"]
        cls._server_thread = _shared_server.server_config["thread"]
        cls._env_patcher = _shared_server.patchers["env"]
        cls._api_patcher = _shared_server.patchers["api"]
        cls._mock_api_instance = _shared_server.patchers["mock_api_instance"]
        cls.models_to_test = _shared_server.test_config["models_to_test"]
        cls.base_url = _shared_server.test_config["base_url"]
        cls.verbosity_level = _shared_server.test_config["verbosity_level"]
        cls.client = _shared_server.server_config["client"]
        cls.loop = _shared_server.server_config["loop"]

    @classmethod
    def tearDownClass(cls):
        """Tear down the test environment for the current class."""
        # Don't cleanup here - let atexit handle it

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.assertTrue(
            self._server_thread.is_alive(), "Server thread did not start correctly."
        )
        self._mock_api_instance.reset_mock()

    async def _run_agent_stream(self, prompt: str) -> tuple[list, str]:
        """
        Run the agent stream for a given prompt and return the tools used and the final result.

        Args:
            prompt: The input prompt to send to the agent.

        Returns:
            A tuple containing the list of tool calls and the final string result from the agent.
        """
        result = ""
        tools = []
        await self.agent.initialize()
        async for event in self.agent.stream_events(prompt, manage_connector=False):
            event_type = event.get("event")
            data = event.get("data", {})
            name = event.get("name")

            if event_type == "on_tool_end" and name == "use_tool_from_server":
                tools.append(data)
            elif event_type == "on_chat_model_stream" and data.get("chunk"):
                result += str(data["chunk"].content)
        return tools, result

    def run_test_with_retries(self, test_name: str, test_logic_coro: callable, assertion_logic: callable):  # fmt: skip
        """
        Run a given test logic multiple times against different models and check for a success threshold.

        Args:
            test_name: The name of the test being run.
            test_logic_coro: An asynchronous function that runs the agent and returns tools and result.
            assertion_logic: A function that takes tools and result and performs assertions.
        """
        # Extract module name from the test class name
        module_name = self._get_module_name()
        success_count = 0
        total_runs = len(self.models_to_test) * RUNS_PER_TEST

        for model_name in self.models_to_test:
            self._setup_model_and_agent(model_name)
            success_count += self._run_model_tests(
                test_name, module_name, model_name, test_logic_coro, assertion_logic
            )

        self._assert_success_threshold(success_count, total_runs)

    def _setup_model_and_agent(self, model_name: str):
        """Set up the LLM and agent for a specific model."""
        # Initialize ChatOpenAI with base_url only if it's provided
        kwargs = {"model": model_name, "temperature": 0.7}
        if self.base_url:
            kwargs["base_url"] = self.base_url

        self.llm = ChatOpenAI(**kwargs)

        # Set agent verbosity based on pytest verbosity
        verbose_mode = self.verbosity_level > 0
        self.agent = MCPAgent(
            llm=self.llm,
            client=self.client,
            max_steps=20,
            verbose=verbose_mode,
            use_server_manager=True,
            memory_enabled=False,
        )

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _run_model_tests(
        self,
        test_name: str,
        module_name: str,
        model_name: str,
        test_logic_coro: callable,
        assertion_logic: callable,
    ) -> int:
        """Run tests for a specific model and return success count."""
        model_success_count = 0

        for i in range(RUNS_PER_TEST):
            print(
                f"Running test {test_name} with model {model_name}, try {i + 1}/{RUNS_PER_TEST}"
            )
            run_result = {
                "test_name": test_name,
                "module_name": module_name,
                "model_name": model_name,
                "run_number": i + 1,
                "status": "failure",
                "failure_reason": None,
                "tools_used": None,
                "agent_result": None,
            }

            try:
                # Each test logic run needs a clean slate.
                self._mock_api_instance.reset_mock()
                tools, result = self.loop.run_until_complete(test_logic_coro())
                run_result.update(
                    {
                        "tools_used": tools,
                        "agent_result": result,
                    }
                )

                assertion_logic(tools, result)
                run_result["status"] = "success"
                model_success_count += 1
            except AssertionError as e:
                run_result["failure_reason"] = f"Assertion failed: {str(e)}"
                print(f"Assertion failed with model {model_name}, try {i + 1}: {e}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Catch any other exception that might occur during agent streaming or test execution
                # fmt: off
                run_result["failure_reason"] = f"Test execution failed: {type(e).__name__}: {str(e)}"
                print(f"Test execution failed with model {model_name}, try {i + 1}: {type(e).__name__}: {e}")
            finally:
                self.test_results.append(run_result)

        return model_success_count

    def _assert_success_threshold(self, success_count: int, total_runs: int):
        """Assert that the success rate meets the threshold."""
        success_rate = success_count / total_runs if total_runs > 0 else 0
        print(f"Success rate: {success_rate * 100:.2f}% ({success_count}/{total_runs})")
        self.assertGreaterEqual(
            success_rate,
            SUCCESS_THRESHOLD,
            f"Success rate of {success_rate * 100:.2f}% is below the required {SUCCESS_THRESHOLD * 100:.2f}% threshold.",
        )

    def _get_module_name(self) -> str:
        """
        Extract the module name from the test class name.
        Expected pattern: Test{ModuleName}ModuleE2E -> {ModuleName}
        """
        class_name = self.__class__.__name__
        # Remove 'Test' prefix and 'ModuleE2E' suffix
        if class_name.startswith("Test") and class_name.endswith("ModuleE2E"):
            module_name = class_name[
                4:-9
            ]  # Remove 'Test' (4 chars) and 'ModuleE2E' (9 chars)
            return module_name

        # Fallback: use the class name as-is if it doesn't match the expected pattern
        return class_name

    def _create_mock_api_side_effect(self, fixtures: list) -> callable:
        """Create a side effect function for the `mock API` based on a list of fixtures."""

        def mock_api_side_effect(operation: str, **kwargs: dict) -> dict:
            print(f"Mock API called with: operation={operation}, kwargs={kwargs}")
            for fixture in fixtures:
                if fixture["operation"] == operation and fixture["validator"](kwargs):
                    print(
                        f"Found matching fixture for {operation}, returning {fixture['response']}"
                    )
                    return fixture["response"]
            print(f"No matching fixture found for {operation}")
            return {"status_code": 200, "body": {"resources": []}}

        return mock_api_side_effect
