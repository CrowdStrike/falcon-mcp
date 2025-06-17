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

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

from src.server import FalconMCPServer

# Load environment variables from .env file for local development
load_dotenv()


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

        server = FalconMCPServer(debug=True)
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
        cls.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        cls.agent = MCPAgent(llm=cls.llm, client=cls.client, verbose=True, use_server_manager=True, memory_enabled=False)


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
        return tools, result

    def test_get_top_3_high_severity_detections(self):
        """Verify the agent can retrieve the top 3 high-severity detections."""
        
        prompt = "Give me the details of the top 3 high severity detections, return only detection id and descriptions"
        tools, result = self.loop.run_until_complete(self._run_agent_stream(prompt))
        
        self.assertEqual(len(tools), 1, "Expected 1 tool call")
        self.assertEqual(tools[0]['input']['tool_name'], "falcon_search_detections")
        self.assertIn("high", tools[0]['input']['tool_input'].lower())
        self.assertIn("detection-1", tools[0]['output'])
        self.assertIn("detection-2", tools[0]['output'])
        self.assertIn("detection-3", tools[0]['output'])

        self.assertEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
        api_call_1_params = self._mock_api_instance.command.call_args_list[0][1]['parameters']
        self.assertIn("high", api_call_1_params['filter'].lower())
        self.assertEqual(api_call_1_params['limit'], 3)
        self.assertEqual(api_call_1_params['sort'], 'max_severity|desc')
        api_call_2_body = self._mock_api_instance.command.call_args_list[1][1]['body']
        self.assertEqual(api_call_2_body['ids'], ["detection-1", "detection-2", "detection-3"])

        self.assertIn("detection-1", result)
        self.assertIn("detection-2", result)
        self.assertIn("detection-3", result)
        
    def test_get_highest_detection_for_ip(self):
        """Verify the agent can find the highest-severity detection for a specific IP."""
        
        prompt = "What is the highest detection for the device with local_ip 10.0.0.1? Return the detection id as well"
        tools, result = self.loop.run_until_complete(self._run_agent_stream(prompt))

        self.assertEqual(len(tools), 1, f"Expected 1 tool call, but got {len(tools)}")
        self.assertEqual(tools[0]['input']['tool_name'], "falcon_search_detections")
        self.assertIn("10.0.0.1", tools[0]['input']['tool_input'])
        self.assertIn("detection-4", tools[0]['output'])

        self.assertEqual(self._mock_api_instance.command.call_count, 2, "Expected 2 API calls")
        api_call_1_params = self._mock_api_instance.command.call_args_list[0][1]['parameters']
        self.assertIn("10.0.0.1", api_call_1_params['filter'])
        api_call_2_body = self._mock_api_instance.command.call_args_list[1][1]['body']
        self.assertEqual(api_call_2_body['ids'], ["detection-4"])

        self.assertIn("detection-4", result)
        self.assertNotIn("detection-1", result)

if __name__ == '__main__':
    unittest.main() 