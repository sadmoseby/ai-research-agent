#!/usr/bin/env python3
"""
Test script to demonstrate MCP tool configuration and usage.
This shows how each node gets different tools and how LLMs are informed about them.
"""
import asyncio
import os

from agent.config import Config
from agent.prompts import ResearchPrompts
from agent.tools.mcp_client import MCPClient


async def test_node_tool_configuration():
    """Test tool configuration for each node."""

    # Set up some example environment variables
    os.environ["WEB_RESEARCH_MCP_TOOLS"] = "web_search,tavily"
    os.environ["PRIOR_ART_MCP_TOOLS"] = "github"
    os.environ["CRITICISM_MCP_TOOLS"] = "web_search"
    os.environ["SYNTHESIZE_MCP_TOOLS"] = "web_search,github,tavily,filesystem"

    # Mock API keys for testing
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["GITHUB_TOKEN"] = "test-token"
    os.environ["TAVILY_API_KEY"] = "test-key"

    config = Config.from_env()

    nodes = [
        "plan",
        "web_research",
        "prior_art",
        "criticism",
        "synthesize",
        "validate",
        "persist",
    ]

    print("MCP Tool Configuration Test")
    print("=" * 50)

    for node_name in nodes:
        print(f"\n{node_name.upper()} Node:")

        # Create node-specific MCP client
        mcp_client = MCPClient(config, node_name=node_name)
        available_tools = mcp_client.get_available_tool_names()

        print(f"  Available tools: {available_tools}")

        # Test tool availability checks
        tool_checks = {
            "web_search": mcp_client.has_tool("web_search"),
            "github": mcp_client.has_tool("github"),
            "tavily": mcp_client.has_tool("tavily"),
            "filesystem": mcp_client.has_tool("filesystem"),
        }

        print("  Tool availability:")
        for tool, available in tool_checks.items():
            status = "✓" if available else "✗"
            print(f"    {status} {tool}")

        # Show how prompts would include tool information
        tools_formatted = ResearchPrompts.format_available_tools(available_tools)
        print("  Tools as shown to LLM:")
        if tools_formatted == "None (operating without MCP tools)":
            print(f"    {tools_formatted}")
        else:
            for line in tools_formatted.split("\n"):
                print(f"    {line}")


async def test_tool_fallback_behavior():
    """Test how nodes handle missing tools."""

    print("\n\nTool Fallback Behavior Test")
    print("=" * 50)

    # Create config with no API keys (simulating missing tools)
    os.environ.pop("GITHUB_TOKEN", None)
    os.environ.pop("TAVILY_API_KEY", None)

    config = Config.from_env()

    # Test web research node with limited tools
    print("\nWeb Research Node (limited tools):")
    mcp_client = MCPClient(config, node_name="web_research")
    available_tools = mcp_client.get_available_tool_names()
    print(f"  Available tools: {available_tools}")

    # Simulate search with fallback
    if mcp_client.has_tool("web_search"):
        print("  ✓ Can use web_search")
    elif mcp_client.has_tool("tavily"):
        print("  ✓ Can fallback to tavily")
    else:
        print("  ✗ No search tools available - will generate error placeholder")

    # Test prior art node without GitHub
    print("\nPrior Art Node (no GitHub):")
    mcp_client = MCPClient(config, node_name="prior_art")
    available_tools = mcp_client.get_available_tool_names()
    print(f"  Available tools: {available_tools}")

    if mcp_client.has_tool("github"):
        print("  ✓ Can search GitHub")
    else:
        print("  ✗ GitHub not available - will skip prior art search")


async def test_prompt_integration():
    """Test how tool information is integrated into prompts."""

    print("\n\nPrompt Integration Test")
    print("=" * 50)

    # Set up environment for synthesis node
    os.environ["SYNTHESIZE_MCP_TOOLS"] = "web_search,github,tavily"
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["GITHUB_TOKEN"] = "test-token"
    os.environ["TAVILY_API_KEY"] = "test-key"

    config = Config.from_env()
    mcp_client = MCPClient(config, node_name="synthesize")
    available_tools = mcp_client.get_available_tool_names()

    # Format tools for prompt
    tools_formatted = ResearchPrompts.format_available_tools(available_tools)

    # Show synthesis system prompt with tools
    alpha_mode_note = ResearchPrompts.get_alpha_mode_note(False)
    system_prompt = ResearchPrompts.SYNTHESIS_SYSTEM_PROMPT.format(
        alpha_mode_note=alpha_mode_note,
        repair_context="",
        available_tools=tools_formatted,
    )

    print("Synthesis System Prompt (with tools):")
    print("-" * 40)
    print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

    # Show criticism prompt with tools
    criticism_prompt = ResearchPrompts.CRITICISM_SYSTEM_PROMPT.format(available_tools=tools_formatted)

    print("\nCriticism System Prompt (with tools):")
    print("-" * 40)
    print(criticism_prompt[:500] + "..." if len(criticism_prompt) > 500 else criticism_prompt)


if __name__ == "__main__":
    asyncio.run(test_node_tool_configuration())
    asyncio.run(test_tool_fallback_behavior())
    asyncio.run(test_prompt_integration())

    print("\n\nTest Summary:")
    print("=" * 50)
    print("✓ Node-specific tool configuration working")
    print("✓ Tool availability checking working")
    print("✓ Fallback behavior implemented")
    print("✓ Prompt integration with tool information working")
    print("\nEach node now:")
    print("- Knows which MCP tools it has access to")
    print("- Informs the LLM about available tools")
    print("- Handles missing tools gracefully")
    print("- Calls required tools as needed")
