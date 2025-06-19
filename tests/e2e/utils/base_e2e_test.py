"""Base class for E2E tests."""
import asyncio
import os
import threading
import time
import unittest
from unittest.mock import MagicMock, patch
import json
import pytest

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use

from src.server import FalconMCPServer

# Models to test against
MODELS_TO_TEST = ["gpt-4.1-mini", "gpt-4o-mini"]
# Number of times to run each test
RUNS_PER_TEST = 2
# Success threshold for passing a test
SUCCESS_THRESHOLD = 0.7

# Load environment variables from .env file for local development
load_dotenv()


class BaseE2ETest(unittest.TestCase):
    """
    Base class for end-to-end tests for the Falcon MCP Server.

    This class sets up a live server in a separate thread, mocks the Falcon API,
    and provides helper methods for running tests with an MCP client and agent.
    """

    test_results = []
    _server_thread: threading.Thread = None
    _env_patcher = None
    _api_patcher = None
    _mock_api_instance: MagicMock = None
    client = None
    agent = None
    llm = None
    loop = None
    verbosity_level = 0  # Default verbosity level
    base_url = None  # Base URL for LLM API
    models_to_test = None  # Models to test against

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, verbosity_level):
        """Inject pytest fixtures into the test class."""
        self.verbosity_level = verbosity_level

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for the entire class."""
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

        # Read optional base_url from environment
        cls.base_url = os.getenv('OPENAI_BASE_URL')

        # Optionally override models from environment
        models_env = os.getenv('MODELS_TO_TEST')
        if models_env:
            cls.models_to_test = models_env.split(',')
        else:
            cls.models_to_test = MODELS_TO_TEST

        cls._env_patcher = patch.dict(
            os.environ,
            {
                'FALCON_CLIENT_ID': 'test-client-id',
                'FALCON_CLIENT_SECRET': 'test-client-secret',
                'FALCON_BASE_URL': 'https://api.test.crowdstrike.com',
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'test-openai-key'),
            },
        )
        cls._env_patcher.start()

        cls._api_patcher = patch('src.client.APIHarnessV2')
        mock_apiharness_class = cls._api_patcher.start()

        cls._mock_api_instance = MagicMock()
        cls._mock_api_instance.login.return_value = True
        cls._mock_api_instance.token_valid.return_value = True
        mock_apiharness_class.return_value = cls._mock_api_instance

        server = FalconMCPServer(debug=False)
        cls._server_thread = threading.Thread(target=server.run, args=("sse",))
        cls._server_thread.daemon = True
        cls._server_thread.start()
        time.sleep(2)  # Wait for the server to initialize

        server_config = {"mcpServers": {"falcon": {"url": "http://127.0.0.1:8000/sse"}}}
        cls.client = MCPClient(config=server_config)

    @classmethod
    def tearDownClass(cls):
        """Tear down the test environment for the entire class."""
        with open('test_results.json', 'w', encoding='utf-8') as f:
            json.dump(cls.test_results, f, indent=4)

        cls.loop.run_until_complete(cls.client.close_all_sessions())
        cls._api_patcher.stop()
        cls._env_patcher.stop()
        cls.loop.close()
        asyncio.set_event_loop(None)

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.assertTrue(self._server_thread.is_alive(), "Server thread did not start correctly.")
        self._mock_api_instance.reset_mock()

    async def _run_agent_stream(self, prompt: str) -> tuple[list, str]:
        """
        Run the agent stream for a given prompt and return the tools used and the final result.

        Args:
            prompt: The input prompt to send to the agent.

        Returns:
            A tuple containing the list of tool calls and the final string result from the agent.
        """
        # Only print detailed info if verbose mode is enabled
        if self.verbosity_level > 0:
            print("\n=== PROMPT ===")
            print(prompt)
            print("==============\n")

        result = ""
        tools = []
        await self.agent.initialize()
        async for event in self.agent.astream(prompt, manage_connector=False):
            event_type = event.get("event")
            data = event.get("data", {})
            name = event.get("name")

            # Log events if in extra verbose mode
            if self.verbosity_level > 1 and event_type:  # Extra verbose with -vv
                print(f"EVENT: {event_type}, NAME: {name}")

            if event_type == "on_tool_end" and name == "use_tool_from_server":
                tools.append(data)
                if self.verbosity_level > 0:  # Standard verbose with -v
                    print("\n=== TOOL CALL ===")
                    print(f"Tool: {data['input']['tool_name']}")
                    print(f"Input: {data['input']['tool_input']}")
                    print("=================\n")
            elif event_type == "on_chat_model_stream" and data.get('chunk'):
                chunk = str(data['chunk'].content)
                result += chunk
                if self.verbosity_level > 0:
                    print(f"{chunk}", end="", flush=True)

        # Always print result and tools for debugging, but format based on verbosity
        if self.verbosity_level > 0:
            print("\n\n=== RESULT ===")
            print(result)
            print("==============\n")
            print("=== TOOLS ===")
            print(tools)
            print("=============\n")
        else:
            # Just print minimal info in non-verbose mode
            print("RESULT", result)
            print("TOOLS", tools)

        return tools, result

    def run_test_with_retries(self, test_name: str, test_logic_coro: callable, assertion_logic: callable):
        """
        Run a given test logic multiple times against different models and check for a success threshold.

        Args:
            test_name: The name of the test being run.
            test_logic_coro: An asynchronous function that runs the agent and returns tools and result.
            assertion_logic: A function that takes tools and result and performs assertions.
        """
        success_count = 0
        total_runs = len(MODELS_TO_TEST) * RUNS_PER_TEST

        # Set debug level based on verbosity
        if self.verbosity_level > 0:
            mcp_use.set_debug(self.verbosity_level)
        else:
            mcp_use.set_debug(0)

        for model_name in self.models_to_test:
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
                verbose=verbose_mode,  # Only verbose if -v is passed
                use_server_manager=True,
                memory_enabled=False,
            )

            for i in range(RUNS_PER_TEST):
                print(f"Running test {test_name} with model {model_name}, try {i+1}/{RUNS_PER_TEST}")
                run_result = {
                    'test_name': test_name,
                    'model_name': model_name,
                    'run_number': i + 1,
                    'status': 'failure',
                    'failure_reason': None,
                    'tools_used': None,
                    'agent_result': None,
                }
                try:
                    # Each test logic run needs a clean slate.
                    self._mock_api_instance.reset_mock()
                    tools, result = self.loop.run_until_complete(test_logic_coro())
                    run_result['tools_used'] = tools
                    run_result['agent_result'] = result

                    assertion_logic(tools, result)

                    run_result['status'] = 'success'
                    success_count += 1
                except AssertionError as e:
                    run_result['failure_reason'] = str(e)
                    print(f"Assertion failed with model {model_name}, try {i+1}: {e}")
                finally:
                    self.__class__.test_results.append(run_result)

        success_rate = success_count / total_runs if total_runs > 0 else 0
        print(f"Success rate: {success_rate * 100:.2f}% ({success_count}/{total_runs})")
        self.assertGreaterEqual(
            success_rate,
            SUCCESS_THRESHOLD,
            f"Success rate of {success_rate*100:.2f}% is below the required {SUCCESS_THRESHOLD*100:.2f}% threshold.",
        )

    def _create_mock_api_side_effect(self, fixtures: list) -> callable:
        """Create a side effect function for the mock API based on a list of fixtures."""

        def mock_api_side_effect(operation: str, **kwargs: dict) -> dict:
            print(f"Mock API called with: operation={operation}, kwargs={kwargs}")
            for fixture in fixtures:
                if fixture["operation"] == operation and fixture["validator"](kwargs):
                    print(f"Found matching fixture for {operation}, returning {fixture['response']}")
                    return fixture["response"]
            print(f"No matching fixture found for {operation}")
            return {"status_code": 200, "body": {"resources": []}}

        return mock_api_side_effect
