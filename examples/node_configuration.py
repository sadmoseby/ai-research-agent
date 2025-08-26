#!/usr/bin/env python3
"""
Example demonstrating per-node configuration usage.
"""

import os

from agent.config import Config


def main():
    """Demonstrate per-node configuration."""

    # Set some example environment variables
    os.environ["OPENAI_API_KEY"] = "fake-key-for-demo"
    os.environ["SYNTHESIZE_MODEL"] = "gpt-4o-mini"  # Use cheaper model for synthesis
    os.environ["CRITICISM_TEMPERATURE"] = "0.9"  # Higher creativity for criticism
    os.environ["WEB_RESEARCH_MAX_TOKENS"] = "8000"  # More tokens for web research
    os.environ["VALIDATE_USE_MCP"] = "false"  # Disable MCP for validation

    # Create config from environment
    config = Config.from_env()

    print("=== Global Configuration ===")
    print(f"Model: {config.default_config.llm_provider.model}")
    print(f"Use MCP: {config.default_config.mcp_enabled}")
    print(f"Temperature: {config.default_config.llm_provider.temperature}")
    print(f"Max Tokens: {config.default_config.llm_provider.max_tokens}")
    print()

    # Show node-specific configurations
    node_names = config.get_all_node_names()

    for node_name in node_names:
        node_config = config.get_node_config(node_name)
        print(f"=== {node_name.upper()} Node Configuration ===")
        print(f"Model: {node_config['model']}")
        print(f"Use MCP: {node_config['use_mcp']}")
        print(f"Temperature: {node_config['temperature']}")
        print(f"Max Tokens: {node_config['max_tokens']}")
        print()

    # Show current node configuration summary
    print("=== Node Configuration Summary ===")
    summary = config.get_effective_config_summary()
    print(f"Available providers: {summary['global']['available_providers']}")
    print(f"Global MCP clients: {summary['global']['global_mcp_clients']}")
    print()

    # Demonstrate the for_node method
    print("=== Using for_node method ===")
    synthesize_config = config.for_node("synthesize")
    print(f"Synthesize config model: {synthesize_config.default_config.llm_provider.model}")
    print(f"Original config model: {config.default_config.llm_provider.model}")


if __name__ == "__main__":
    main()
