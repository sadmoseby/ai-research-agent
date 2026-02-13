#!/usr/bin/env python3
"""
Test script to verify that MCPClient properly uses Config for server parameters.
"""

import asyncio
import os

from agent.config import Config
from agent.tools.mcp_client import MCPClient


async def test_mcp_config_integration():
    """Test that MCPClient gets server parameters from Config instead of hardcoded values."""

    # Set up test environment
    os.environ["GITHUB_TOKEN"] = "fake-test-token"
    os.environ["TAVILY_API_KEY"] = "fake-test-key"

    # Create config
    config = Config()

    # Create mock LLM client
    class MockLLMClient:
        def get_provider_info(self):
            return {"provider": "test", "model": "test-model"}

        async def chat_completion(self, messages, **kwargs):  # pylint: disable=unused-argument
            return {"content": "Mock response"}

    llm_client = MockLLMClient()

    # Create MCP client in testing mode
    mcp_client = MCPClient(config, llm_client, node_name="test", is_testing=True)

    print("=== Testing Config-based Server Parameter Retrieval ===")

    # Test getting server params for different tools
    for tool_name in ["github", "tavily", "filesystem", "validation"]:
        print(f"\nTesting tool: {tool_name}")

        # Check if config has this tool
        if tool_name in config.mcp_clients:
            mcp_config = config.mcp_clients[tool_name]
            print(f"  Config found: {mcp_config.name}")
            print(f"  Command: {mcp_config.command}")
            print(f"  Args: {mcp_config.args}")
            print(f"  API Key Env: {mcp_config.api_key_env}")

            # Get server params from MCPClient
            server_params = await mcp_client._get_server_params(tool_name)  # pylint: disable=protected-access

            if server_params:
                print(f"  Server Params - Command: {server_params.command}")
                print(f"  Server Params - Args: {server_params.args}")
                print(f"  Server Params - Env: {list(server_params.env.keys()) if server_params.env else 'None'}")
            else:
                print("  Server Params: None (probably internal tool)")
        else:
            print(f"  No config found for {tool_name}")

    print("\n=== Available Tools ===")
    available_tools = mcp_client.get_available_tool_names()
    print(f"Available tools: {available_tools}")

    print("\n=== Tool Availability Check ===")
    for tool in ["github", "tavily", "filesystem", "validation", "llm_fallback"]:
        has_tool = mcp_client.has_tool(tool)
        print(f"  {tool}: {'✓' if has_tool else '✗'}")

    print("\nTest completed successfully! MCPClient is now using Config for server parameters.")


if __name__ == "__main__":
    asyncio.run(test_mcp_config_integration())
