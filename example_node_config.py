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
    print(f"Model: {config.model}")
    print(f"Use MCP: {config.use_mcp}")
    print(f"Temperature: {config.temperature}")
    print(f"Max Tokens: {config.max_tokens}")
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

    # Show how to programmatically set node configs
    print("=== Setting Node Config Programmatically ===")
    config.set_node_config("plan", model="gpt-3.5-turbo", temperature=0.1)

    plan_config = config.get_node_config("plan")
    print(f"Plan node model: {plan_config['model']}")
    print(f"Plan node temperature: {plan_config['temperature']}")
    print()

    # Demonstrate the for_node method
    print("=== Using for_node method ===")
    synthesize_config = config.for_node("synthesize")
    print(f"Synthesize config model: {synthesize_config.model}")
    print(f"Original config model: {config.model}")


if __name__ == "__main__":
    main()
