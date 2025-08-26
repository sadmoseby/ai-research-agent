#!/usr/bin/env python3
"""
Example demonstrating the refactored MCP tool access configuration system.
"""

import os

from agent.config import Config, MCPClientConfig


def main():
    """Demonstrate MCP tool access configuration."""

    # Set some example environment variables
    os.environ["OPENAI_API_KEY"] = "fake-key-for-demo"
    os.environ["GITHUB_TOKEN"] = "fake-github-token"
    os.environ["TAVILY_API_KEY"] = "fake-tavily-token"

    # Configure specific MCP tools for different nodes
    os.environ["WEB_RESEARCH_MCP_TOOLS"] = "tavily,github"
    os.environ["SYNTHESIZE_MCP_TOOLS"] = "tavily"
    os.environ["PRIOR_ART_MCP_TOOLS"] = "github"

    # Override global MCP client settings
    os.environ["MCP_TAVILY_TIMEOUT"] = "60"
    os.environ["MCP_TAVILY_CONFIG"] = '{"search_depth": "deep", "include_raw_content": true}'

    # Create config from environment
    config = Config.from_env()

    print("=== Global MCP Clients ===")
    global_clients = config.get_global_mcp_clients()
    for name, client in global_clients.items():
        print(f"  {name}: {client.server_type} (enabled: {client.enabled})")
        print(f"    Command: {client.command} {' '.join(client.args)}")
        print(f"    Timeout: {client.timeout}s")
        print(f"    Config: {client.config_params}")
        print()

    print("=== Node MCP Tool Access ===")

    # Show node-specific MCP tool access
    for node_name in ["web_research", "synthesize", "prior_art", "plan"]:
        mcp_tools = config.get_node_mcp_tools(node_name)
        mcp_clients = config.get_node_mcp_clients(node_name)

        print(f"=== {node_name.upper()} Node ===")
        print(f"Available Tools: {mcp_tools}")
        print(f"Client Configurations: {len(mcp_clients)} clients")

        for client in mcp_clients:
            print(f"  - {client.name} ({client.server_type})")
        print()

    # Demonstrate programmatic tool management
    print("=== Programmatic Tool Management ===")

    # Add a custom global MCP client
    custom_client = MCPClientConfig(
        name="database",
        server_type="database",
        command="python",
        args=["-m", "mcp_servers.database"],
        config_params={
            "connection_string": "postgresql://localhost/research",
            "read_only": True,
        },
        timeout=45,
    )

    config.add_global_mcp_client(custom_client)
    print("Added global 'database' MCP client")

    # Add the database tool to the synthesize node
    config.add_mcp_tool_to_node("synthesize", "database")
    print("Added 'database' tool access to synthesize node")

    # Show updated synthesize node configuration
    synthesize_tools = config.get_node_mcp_tools("synthesize")
    print(f"Synthesize node tools: {synthesize_tools}")
    print()

    # Show complete node configuration including MCP access
    print("=== Complete Web Research Node Configuration ===")
    web_research_config = config.get_node_config("web_research")
    print(f"Model: {web_research_config['model']}")
    print(f"Use MCP: {web_research_config['use_mcp']}")
    print(f"Temperature: {web_research_config['temperature']}")
    print(f"MCP Tools: {web_research_config['mcp_tools']}")
    print(f"Available MCP Clients: {len(web_research_config['mcp_clients'])}")

    for client in web_research_config["mcp_clients"]:
        print(f"  - {client.name}: {client.config_params}")

    print()

    # Demonstrate removing access
    print("=== Removing Tool Access ===")
    removed = config.remove_mcp_tool_from_node("web_research", "tavily")
    print(f"Removed 'tavily' from web_research: {removed}")

    updated_tools = config.get_node_mcp_tools("web_research")
    print(f"Updated web_research tools: {updated_tools}")


if __name__ == "__main__":
    main()
