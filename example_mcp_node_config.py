#!/usr/bin/env python3
"""
Example configuration showing how to configure MCP tools per node.

This demonstrates how different nodes can have different MCP tools available.
"""
import os

# Example environment variables for per-node MCP tool configuration

# Planning node: Only needs basic tools
os.environ["PLAN_MCP_TOOLS"] = "filesystem"

# Web research node: Needs web search and academic search tools
os.environ["WEB_RESEARCH_MCP_TOOLS"] = "web_search,tavily"

# Prior art node: Needs GitHub for code search
os.environ["PRIOR_ART_MCP_TOOLS"] = "github,filesystem"

# Criticism node: Needs web search for additional verification
os.environ["CRITICISM_MCP_TOOLS"] = "web_search,tavily"

# Synthesis node: Needs all tools for comprehensive generation
os.environ["SYNTHESIZE_MCP_TOOLS"] = "web_search,github,tavily,filesystem"

# Validate node: Only needs filesystem for schema validation
os.environ["VALIDATE_MCP_TOOLS"] = "filesystem"

# Persist node: Only needs filesystem for saving
os.environ["PERSIST_MCP_TOOLS"] = "filesystem"

# Example of node-specific model configuration
os.environ["SYNTHESIZE_MODEL"] = "gpt-4o"  # Use more powerful model for synthesis
os.environ["CRITICISM_MODEL"] = "gpt-4o"  # Use more powerful model for criticism
os.environ["WEB_RESEARCH_MODEL"] = "gpt-4o-mini"  # Lighter model for web research

# Example of node-specific temperature settings
os.environ["SYNTHESIZE_TEMPERATURE"] = "0.3"  # Lower temperature for structured output
os.environ["CRITICISM_TEMPERATURE"] = "0.7"  # Higher temperature for creative criticism
os.environ["PLAN_TEMPERATURE"] = "0.5"  # Moderate temperature for planning

if __name__ == "__main__":
    from agent.config import Config

    # Load configuration
    config = Config.from_env()

    # Print configuration for each node
    nodes = [
        "plan",
        "web_research",
        "prior_art",
        "criticism",
        "synthesize",
        "validate",
        "persist",
    ]

    print("Node-specific MCP Tool Configuration:")
    print("=" * 50)

    for node in nodes:
        node_config = config.get_node_config(node)
        print(f"\n{node.upper()} Node:")
        print(f"  MCP Tools: {node_config['mcp_tools']}")
        print(f"  Model: {node_config['model']}")
        print(f"  Temperature: {node_config['temperature']}")
        print(f"  Use MCP: {node_config['use_mcp']}")

    print("\nGlobal MCP Clients Available:")
    for name, client in config.mcp_clients.items():
        status = "enabled" if client.enabled else "disabled"
        print(f"  {name}: {status} ({client.server_type})")
