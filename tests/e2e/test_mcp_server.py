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
import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use

from src.server import FalconMCPServer

# Models to test against
# MODELS_TO_TEST = ["gpt-4o", "gpt-4.1-mini", "gpt-4o-mini"]
MODELS_TO_TEST = ["gpt-4.1", "gpt-4o-mini"]
# Number of times to run each test
RUNS_PER_TEST = 2
# Success threshold for passing a test
SUCCESS_THRESHOLD = 0.7

# Load environment variables from .env file for local development
load_dotenv()

mcp_use.set_debug(0)

@pytest.mark.e2e
class TestFalconMCPServerE2E(unittest.TestCase):
    """
    End-to-end test suite for the Falcon MCP Server.

    This class sets up a live server in a separate thread, mocks the Falcon API,
    and then runs tests using an MCP client and agent to interact with the server.
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

        for model_name in MODELS_TO_TEST:
            self.llm = ChatOpenAI(model=model_name, temperature=0.4)
            self.agent = MCPAgent(llm=self.llm, client=self.client, max_steps=20, verbose=False, use_server_manager=True, memory_enabled=False)

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
            f"Success rate of {success_rate*100:.2f}% is below the required {SUCCESS_THRESHOLD*100:.2f}% threshold."
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

    def test_get_top_3_high_severity_detections(self):
        """Verify the agent can retrieve the top 3 high-severity detections."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDetects",
                    "validator": lambda kwargs: "high" in kwargs.get('parameters', {}).get('filter', '').lower() or "max_severity:5" in kwargs.get('parameters', {}).get('filter', '').lower(),
                    "response": {"status_code": 200, "body": {"resources": ["detection-1", "detection-2", "detection-3"]}}
                },
                {
                    "operation": "GetDetectSummaries",
                    "validator": lambda kwargs: "detection-1" in kwargs.get('body', {}).get('ids', []),
                    "response": {
                        "status_code": 200,
                        "body": {
                            "resources": [
                                {"id": "detection-1", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                                {"id": "detection-2", "status": "new", "severity": "high", "description": "A test detection for E2E."},
                                {"id": "detection-3", "status": "new", "severity": "high", "description": "A test detection for E2E."}
                            ]
                        }
                    }
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "Give me the details of the top 3 high severity detections, return only detection id and descriptions"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, "Expected 1 tool call")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_detections")
            self.assertIn("high", json.dumps(used_tool['input']['tool_input']).lower())
            self.assertIn("detection-1", used_tool['output'])
            self.assertIn("detection-2", used_tool['output'])
            self.assertIn("detection-3", used_tool['output'])

            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("high", api_call_1_params.get('filter').lower())
            self.assertEqual(api_call_1_params.get('limit'), 3)
            self.assertIn('max_severity.desc', api_call_1_params.get('sort', ''))
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-1", "detection-2", "detection-3"])

            self.assertIn("detection-1", result)
            self.assertIn("detection-2", result)
            self.assertIn("detection-3", result)

        self.run_test_with_retries(
            "test_get_top_3_high_severity_detections",
            test_logic,
            assertions
        )

    def test_get_highest_detection_for_ip(self):
        """Verify the agent can find the highest-severity detection for a specific IP."""
        async def test_logic():
            fixtures = [
                {
                    "operation": "QueryDetects",
                    "validator": lambda kwargs: "10.0.0.1" in kwargs.get('parameters', {}).get('filter', ''),
                    "response": {"status_code": 200, "body": {"resources": ["detection-4"]}}
                },
                {
                    "operation": "GetDetectSummaries",
                    "validator": lambda kwargs: "detection-4" in kwargs.get('body', {}).get('ids', []),
                    "response": {
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
                }
            ]

            self._mock_api_instance.command.side_effect = self._create_mock_api_side_effect(fixtures)

            prompt = "What is the highest detection for the device with local_ip 10.0.0.1? Return the detection id as well"
            return await self._run_agent_stream(prompt)

        def assertions(tools, result):
            self.assertGreaterEqual(len(tools), 1, f"Expected 1 tool call, but got {len(tools)}")
            used_tool = tools[len(tools) - 1]
            self.assertEqual(used_tool['input']['tool_name'], "falcon_search_detections")
            self.assertIn("10.0.0.1", json.dumps(used_tool['input']['tool_input']))
            self.assertIn("detection-4", used_tool['output'])

            self.assertGreaterEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
            api_call_1_params = self._mock_api_instance.command.call_args_list[0][1].get('parameters', {})
            self.assertIn("10.0.0.1", api_call_1_params.get('filter'))
            api_call_2_body = self._mock_api_instance.command.call_args_list[1][1].get('body', {})
            self.assertEqual(api_call_2_body.get('ids'), ["detection-4"])

            self.assertIn("detection-4", result)
            self.assertNotIn("detection-1", result)

        self.run_test_with_retries(
            "test_get_highest_detection_for_ip",
            test_logic,
            assertions
        )

if __name__ == '__main__':
    unittest.main() 
