"""Base class for E2E tests."""
import asyncio
import os
import threading
import time
import unittest
from unittest.mock import MagicMock, patch
import json
import atexit
import pytest

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

from src.server import FalconMCPServer
from src import registry

# Models to test against
MODELS_TO_TEST = ["gpt-4.1-mini", "gpt-4o-mini"]
# Number of times to run each test
RUNS_PER_TEST = 2
# Success threshold for passing a test
SUCCESS_THRESHOLD = 0.7

# Load environment variables from .env file for local development
load_dotenv()


# Module-level singleton for shared server resources
class SharedTestServer:
    """Singleton class to manage shared test server resources."""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.test_results = []
            self.server_thread = None
            self.env_patcher = None
            self.api_patcher = None
            self.mock_api_instance = None
            self.client = None
            self.loop = None
            self.verbosity_level = 0
            self.base_url = os.getenv('OPENAI_BASE_URL')
            self.models_to_test = MODELS_TO_TEST
            self._cleanup_registered = False
    
    def initialize(self):
        """Initialize the shared server and test environment."""
        if self._initialized:
            return
            
        print("Initializing shared FalconMCP server for E2E tests...")
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Optionally override models from environment
        models_env = os.getenv('MODELS_TO_TEST')
        if models_env:
            self.models_to_test = models_env.split(',')


        self.env_patcher = patch.dict(
            os.environ,
            {
                'FALCON_CLIENT_ID': 'test-client-id',
                'FALCON_CLIENT_SECRET': 'test-client-secret',
                'FALCON_BASE_URL': 'https://api.test.crowdstrike.com',
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'test-openai-key'),
            },
        )
        self.env_patcher.start()

        self.api_patcher = patch('src.client.APIHarnessV2')
        mock_apiharness_class = self.api_patcher.start()

        self.mock_api_instance = MagicMock()
        self.mock_api_instance.login.return_value = True
        self.mock_api_instance.token_valid.return_value = True
        mock_apiharness_class.return_value = self.mock_api_instance

        # Ensure modules are discovered before creating the server
        registry.discover_modules()

        server = FalconMCPServer(debug=False)
        self.server_thread = threading.Thread(target=server.run, args=("sse",))
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Wait for the server to initialize

        server_config = {"mcpServers": {"falcon": {"url": "http://127.0.0.1:8000/sse"}}}
        self.client = MCPClient(config=server_config)
        
        self.__class__._initialized = True
        
        # Register cleanup function to run when Python exits (only once)
        if not self._cleanup_registered:
            atexit.register(self.cleanup)
            self._cleanup_registered = True
        
        print("Shared FalconMCP server initialized successfully.")
    
    def cleanup(self):
        """Clean up the shared server and test environment."""
        if not self._initialized:
            return
            
        print("Cleaning up shared FalconMCP server...")
        
        try:
            # Write test results to file
            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=4)
            
            if self.api_patcher:
                try:
                    self.api_patcher.stop()
                except Exception as e:
                    print(f"Warning: API patcher cleanup error: {e}")
            
            if self.env_patcher:
                try:
                    self.env_patcher.stop()
                except Exception as e:
                    print(f"Warning: Environment patcher cleanup error: {e}")
                
            if self.loop and not self.loop.is_closed():
                try:
                    self.loop.close()
                    asyncio.set_event_loop(None)
                except Exception as e:
                    print(f"Warning: Event loop cleanup error: {e}")
            
            # Reset state
            self.__class__._initialized = False
            self._cleanup_registered = False
            
            print("Shared FalconMCP server cleanup completed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Still reset the state even if cleanup partially failed
            self.__class__._initialized = False
            self._cleanup_registered = False


# Global singleton instance
_shared_server = SharedTestServer()


class BaseE2ETest(unittest.TestCase):
    """
    Base class for end-to-end tests for the Falcon MCP Server.

    This class sets up a live server in a separate thread, mocks the Falcon API,
    and provides helper methods for running tests with an MCP client and agent.
    
    The server is shared across all test classes that inherit from this base class.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for the entire class."""
        # Initialize the shared server
        _shared_server.initialize()
        
        # Set instance variables to point to shared resources
        cls.test_results = _shared_server.test_results
        cls._server_thread = _shared_server.server_thread
        cls._env_patcher = _shared_server.env_patcher
        cls._api_patcher = _shared_server.api_patcher
        cls._mock_api_instance = _shared_server.mock_api_instance
        cls.models_to_test = _shared_server.models_to_test
        cls.base_url = _shared_server.base_url
        cls.verbosity_level = _shared_server.verbosity_level
        cls.client = _shared_server.client
        cls.loop = _shared_server.loop

    @classmethod
    def tearDownClass(cls):
        """Tear down the test environment for the current class."""
        # Don't cleanup here - let atexit handle it
        pass

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
        result = ""
        tools = []
        await self.agent.initialize()
        async for event in self.agent.astream(prompt, manage_connector=False):
            event_type = event.get("event")
            data = event.get("data", {})
            name = event.get("name")

            if event_type == "on_tool_end" and name == "use_tool_from_server":
                tools.append(data)
            elif event_type == "on_chat_model_stream" and data.get('chunk'):
                result += str(data['chunk'].content)
        return tools, result

    def run_test_with_retries(self, test_name: str, test_logic_coro: callable, assertion_logic: callable):
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

            for i in range(RUNS_PER_TEST):
                print(f"Running test {test_name} with model {model_name}, try {i+1}/{RUNS_PER_TEST}")
                run_result = {
                    'test_name': test_name,
                    'module_name': module_name,
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
                    self.test_results.append(run_result)

        success_rate = success_count / total_runs if total_runs > 0 else 0
        print(f"Success rate: {success_rate * 100:.2f}% ({success_count}/{total_runs})")
        self.assertGreaterEqual(
            success_rate,
            SUCCESS_THRESHOLD,
            f"Success rate of {success_rate*100:.2f}% is below the required {SUCCESS_THRESHOLD*100:.2f}% threshold.",
        )

    def _get_module_name(self) -> str:
        """
        Extract the module name from the test class name.
        Expected pattern: Test{ModuleName}ModuleE2E -> {ModuleName}
        """
        class_name = self.__class__.__name__
        # Remove 'Test' prefix and 'ModuleE2E' suffix
        if class_name.startswith('Test') and class_name.endswith('ModuleE2E'):
            module_name = class_name[4:-9]  # Remove 'Test' (4 chars) and 'ModuleE2E' (9 chars)
            return module_name
        else:
            # Fallback: use the class name as-is if it doesn't match the expected pattern
            return class_name

    def _create_mock_api_side_effect(self, fixtures: list) -> callable:
        """Create a side effect function for the `mock API` based on a list of fixtures."""

        def mock_api_side_effect(operation: str, **kwargs: dict) -> dict:
            print(f"Mock API called with: operation={operation}, kwargs={kwargs}")
            for fixture in fixtures:
                if fixture["operation"] == operation and fixture["validator"](kwargs):
                    print(f"Found matching fixture for {operation}, returning {fixture['response']}")
                    return fixture["response"]
            print(f"No matching fixture found for {operation}")
            return {"status_code": 200, "body": {"resources": []}}

        return mock_api_side_effect
