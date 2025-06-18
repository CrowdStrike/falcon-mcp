"""
E2E tests for the Falcon MCP Server.

This module contains end-to-end tests for the Falcon MCP server, ensuring that
the server can handle requests from an MCP client, interact with a mocked Falcon API,
and return the expected results.
"""
import asyncio
import os
import threading
import time
import unittest
from unittest.mock import MagicMock, patch
import pytest

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use

from src.server import FalconMCPServer

# Models to test against
# MODELS_TO_TEST = ["gpt-4o", "gpt-4.1-mini", "gpt-4o-mini"]
MODELS_TO_TEST = ["gpt-4o-mini"]
# Number of times to run each test
RUNS_PER_TEST = 5
# Success threshold for passing a test
SUCCESS_THRESHOLD = 0.7

# Load environment variables from .env file for local development
load_dotenv()

mcp_use.set_debug(0)

def _mock_falcon_api_side_effect(operation: str, **kwargs: dict) -> dict:
    """
    Simulate the behavior of the Falcon API's `command` method.

    This function returns predefined responses based on the operation name and parameters,
    allowing for controlled testing of the MCP server's interaction with the Falcon API.

    Args:
        operation: The name of the API operation to mock.
        kwargs: The arguments passed to the API operation.

    Returns:
        A dictionary representing the mocked API response.
    """
    params = kwargs.get('parameters', {})
    body = kwargs.get('body', {})
    print("OPERATION", operation)
    print("PARAMS", params)
    print("BODY", body)

    if operation == "QueryDetects":
        filter_str = params.get('filter', '')
        if "10.0.0.1" in filter_str:
            return {"status_code": 200, "body": {"resources": ["detection-4"]}}
        if "high" in filter_str.lower() or "max_severity:5" in filter_str.lower():
            return {"status_code": 200, "body": {"resources": ["detection-1", "detection-2", "detection-3"]}}

    if operation == "GetDetectSummaries":
        ids = body.get('ids', [])
        if "detection-1" in ids:
            return {
                "status_code": 200,
                "body": {
                    "resources": [
                        {"id": "detection-1", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                        {"id": "detection-2", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                        {"id": "detection-3", "status": "new", "severity": "high", "description": "A test detection for E2E."}
                    ]
                }
            }
        if "detection-4" in ids:
            return {
                "status_code": 200,
                "body": {
                    "resources": [{
                        "id": "detection-4",
                        "status": "new",
                        "severity": "critical",
                        "description": "A critical detection on a specific IP."
                    }]
                }
            }

    return {"status_code": 200, "body": {"resources": []}}


@pytest.mark.e2e
class TestFalconMCPServerE2E(unittest.TestCase):
    """
    End-to-end test suite for the Falcon MCP Server.

    This class sets up a live server in a separate thread, mocks the Falcon API,
    and then runs tests using an MCP client and agent to interact with the server.
    """

    _server_thread: threading.Thread = None
    _env_patcher = None
    _api_patcher = None
    _mock_api_instance: MagicMock = None
    client = None
    agent = None
    llm = None
    loop = None

    @classmethod
    def setUpClass(cls):
        """Set up the test environment for the entire class."""
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

        cls._env_patcher = patch.dict(os.environ, {
            'FALCON_CLIENT_ID': 'test-client-id',
            'FALCON_CLIENT_SECRET': 'test-client-secret',
            'FALCON_BASE_URL': 'https://api.test.crowdstrike.com',
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'test-openai-key')
        })
        cls._env_patcher.start()

        cls._api_patcher = patch('src.client.APIHarnessV2')
        mock_apiharness_class = cls._api_patcher.start()

        cls._mock_api_instance = MagicMock()
        cls._mock_api_instance.login.return_value = True
        cls._mock_api_instance.token_valid.return_value = True
        cls._mock_api_instance.command.side_effect = _mock_falcon_api_side_effect
        mock_apiharness_class.return_value = cls._mock_api_instance

        server = FalconMCPServer(debug=False)
        cls._server_thread = threading.Thread(target=server.run, args=("sse",))
        cls._server_thread.daemon = True
        cls._server_thread.start()
        time.sleep(2)  # Wait for the server to initialize
        
        server_config = {
            "mcpServers": {
                "falcon": {
                    "url": "http://127.0.0.1:8000/sse"
                }
            }
        }
        cls.client = MCPClient(config=server_config)


    @classmethod
    def tearDownClass(cls):
        """Tear down the test environment for the entire class."""
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
        print("RESULT", result)
        print("TOOLS", tools)
        return tools, result

    def run_test_with_retries(self, test_logic_coro):
        """
        Run a given test logic multiple times against different models and check for a success threshold.

        Args:
            test_logic_coro: An asynchronous function containing the test's assertions.
        """
        success_count = 0
        total_runs = len(MODELS_TO_TEST) * RUNS_PER_TEST

        for model_name in MODELS_TO_TEST:
            self.llm = ChatOpenAI(model=model_name, temperature=0.4)
            self.agent = MCPAgent(llm=self.llm, client=self.client, verbose=False, use_server_manager=True, memory_enabled=False)

            for i in range(RUNS_PER_TEST):
                print(f"Running test with model {model_name}, try {i+1}/{RUNS_PER_TEST}")
                try:
                    # Each test logic run needs a clean slate.
                    self._mock_api_instance.reset_mock()
                    self.loop.run_until_complete(test_logic_coro())
                    success_count += 1
                except AssertionError as e:
                    print(f"Assertion failed with model {model_name}, try {i+1}: {e}")

        success_rate = success_count / total_runs if total_runs > 0 else 0
        print(f"Success rate: {success_rate * 100:.2f}% ({success_count}/{total_runs})")
        self.assertGreaterEqual(
            success_rate,
            SUCCESS_THRESHOLD,
            f"Success rate of {success_rate*100:.2f}% is below the required {SUCCESS_THRESHOLD*100:.2f}% threshold."
        )

    def test_get_top_3_high_severity_detections(self):
        """Verify the agent can retrieve the top 3 high-severity detections."""
        async def test_logic():
            prompt = "Give me the details of the top 3 high severity detections, return only detection id and descriptions"
            tools, result = await self._run_agent_stream(prompt)

            self.assertEqual(len(tools), 1, "Expected 1 tool call")
            self.assertEqual(tools[0]['input']['tool_name'], "falcon_search_detections")
            self.assertIn("high", tools[0]['input']['tool_input'].lower())
            self.assertIn("detection-1", tools[0]['output'])
            self.assertIn("detection-2", tools[0]['output'])
            self.assertIn("detection-3", tools[0]['output'])

            self.assertEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("high", api_call_1_params.get('filter').lower())
            self.assertEqual(api_call_1_params.get('limit'), 3)
            self.assertEqual(api_call_1_params.get('sort'), 'max_severity|desc')
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-1", "detection-2", "detection-3"])

            self.assertIn("detection-1", result)
            self.assertIn("detection-2", result)
            self.assertIn("detection-3", result)

        self.run_test_with_retries(test_logic)

    def test_get_highest_detection_for_ip(self):
        """Verify the agent can find the highest-severity detection for a specific IP."""
        async def test_logic():
            prompt = "What is the highest detection for the device with local_ip 10.0.0.1? Return the detection id as well"
            tools, result = await self._run_agent_stream(prompt)

            self.assertEqual(len(tools), 1, f"Expected 1 tool call, but got {len(tools)}")
            self.assertEqual(tools[0]['input']['tool_name'], "falcon_search_detections")
            self.assertIn("10.0.0.1", tools[0]['input']['tool_input'])
            self.assertIn("detection-4", tools[0]['output'])

            self.assertEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("10.0.0.1", api_call_1_params.get('filter'))
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-4"])

            self.assertIn("detection-4", result)
            self.assertNotIn("detection-1", result)

        self.run_test_with_retries(test_logic)

if __name__ == '__main__':
    unittest.main() 