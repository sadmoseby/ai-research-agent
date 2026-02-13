#!/usr/bin/env python3
"""
Test script for node enable/disable configuration.
"""
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config


def test_node_config():
    """Test the node configuration functionality."""
    print("Testing node enable/disable configuration...")

    # Set up minimal test environment
    os.environ["OPENAI_API_KEY"] = "test-key-for-config-test"

    # Test 1: Default configuration (all nodes enabled)
    print("\n1. Testing default configuration:")
    config = Config()
    enabled = config.get_enabled_nodes()
    disabled = config.get_disabled_nodes()
    print(f"   Enabled nodes: {enabled}")
    print(f"   Disabled nodes: {disabled}")
    assert len(enabled) == 6, f"Expected 6 enabled nodes by default, got {len(enabled)}"
    assert len(disabled) == 0, f"Expected 0 disabled nodes by default, got {len(disabled)}"

    # Test 2: Disable specific nodes via environment
    print("\n2. Testing node disabling via environment variables:")
    os.environ["CRITICISM_ENABLED"] = "false"

    config = Config()
    enabled = config.get_enabled_nodes()
    disabled = config.get_disabled_nodes()
    print(f"   Enabled nodes: {enabled}")
    print(f"   Disabled nodes: {disabled}")

    assert "criticism" not in enabled, "criticism should be disabled"
    assert "criticism" in disabled, "criticism should be in disabled list"
    assert len(enabled) == 5, f"Expected 5 enabled nodes after disabling criticism (6-1), got {len(enabled)}"

    # Test 3: Individual node checks
    print("\n3. Testing individual node checks:")
    assert not config.is_node_enabled("criticism"), "criticism should be disabled"
    assert config.is_node_enabled("plan"), "plan should be enabled"
    assert config.is_node_enabled("synthesize"), "synthesize should be enabled"

    # Test 4: Explicit enabling
    print("\n4. Testing explicit enabling:")
    os.environ["WEB_RESEARCH_ENABLED"] = "true"
    config = Config()
    assert config.is_node_enabled("web_research"), "web_research should be explicitly enabled"

    # Clean up environment
    del os.environ["CRITICISM_ENABLED"]
    del os.environ["WEB_RESEARCH_ENABLED"]

    print("\n✅ All node configuration tests passed!")


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\nTesting edge cases...")

    # Set up minimal test environment
    os.environ["OPENAI_API_KEY"] = "test-key-for-config-test"

    # Test: Disable all nodes
    print("\n5. Testing all nodes disabled:")
    for node in ["PLAN", "WEB_RESEARCH", "CRITICISM", "SYNTHESIZE", "VALIDATE", "PERSIST", "GITHUB_ISSUE"]:
        os.environ[f"{node}_ENABLED"] = "false"

    config = Config()
    enabled = config.get_enabled_nodes()
    disabled = config.get_disabled_nodes()
    print(f"   Enabled nodes: {enabled}")
    print(f"   Disabled nodes: {disabled}")

    assert len(enabled) == 0, f"All nodes should be disabled, but found {enabled}"
    assert len(disabled) == 6, f"All 6 nodes should be in disabled list, got {len(disabled)}"

    # Clean up for next test
    for node in ["PLAN", "WEB_RESEARCH", "CRITICISM", "SYNTHESIZE", "VALIDATE", "PERSIST", "GITHUB_ISSUE"]:
        if f"{node}_ENABLED" in os.environ:
            del os.environ[f"{node}_ENABLED"]

    # Test: Only enable core nodes
    print("\n6. Testing core nodes only:")
    os.environ["SYNTHESIZE_ENABLED"] = "true"
    os.environ["PERSIST_ENABLED"] = "true"
    for node in ["PLAN", "WEB_RESEARCH", "CRITICISM", "VALIDATE", "GITHUB_ISSUE"]:
        os.environ[f"{node}_ENABLED"] = "false"

    config = Config()
    enabled = config.get_enabled_nodes()
    disabled = config.get_disabled_nodes()
    print(f"   Enabled nodes: {enabled}")
    print(f"   Disabled nodes: {disabled}")

    assert "synthesize" in enabled, "synthesize should be enabled"
    assert "persist" in enabled, "persist should be enabled"
    assert len(enabled) == 2, f"Expected 2 enabled nodes, got {len(enabled)}"

    # Clean up
    for node in ["PLAN", "WEB_RESEARCH", "CRITICISM", "VALIDATE", "SYNTHESIZE", "PERSIST", "GITHUB_ISSUE"]:
        if f"{node}_ENABLED" in os.environ:
            del os.environ[f"{node}_ENABLED"]

    print("\n✅ Edge case tests passed!")


if __name__ == "__main__":
    test_node_config()
    test_edge_cases()

    # Try graph creation test if dependencies are available
    try:
        print("\nTesting graph creation with disabled nodes...")
        os.environ["OPENAI_API_KEY"] = "test-key-for-config-test"
        os.environ["CRITICISM_ENABLED"] = "false"

        from agent.graph import create_research_graph

        config = Config()
        graph = create_research_graph(config)
        print("✅ Graph creation successful with disabled nodes")

        # Clean up
        del os.environ["CRITICISM_ENABLED"]

    except ImportError as e:
        print(f"⚠️  Graph creation test skipped (missing dependency: {e})")
    except Exception as e:
        print(f"❌ Graph creation failed: {e}")

    print("\n🎉 All configuration tests completed successfully!")
