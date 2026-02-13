#!/usr/bin/env python
"""Test script for node enable/disable configuration."""

import json
import os
import tempfile

from agent.config import Config


def test_default_config():
    """Test 1: Default config (all nodes enabled)"""
    print("Test 1: Default config (all nodes enabled)")
    config = Config()
    print(f"  Enabled nodes: {config.get_enabled_nodes()}")
    print(f"  Disabled nodes: {config.get_disabled_nodes()}")
    assert len(config.get_disabled_nodes()) == 0
    print("  ✅ PASSED\n")


def test_disable_criticism():
    """Test 2: Disable criticism via config"""
    print("Test 2: Disable criticism via config")
    config = Config(criticism_enabled=False)
    print(f"  criticism enabled? {config.is_node_enabled('criticism')}")
    print(f"  Enabled nodes: {config.get_enabled_nodes()}")
    print(f"  Disabled nodes: {config.get_disabled_nodes()}")
    assert config.is_node_enabled("criticism") is False
    assert "criticism" in config.get_disabled_nodes()
    assert "criticism" not in config.get_enabled_nodes()
    print("  ✅ PASSED\n")


def test_disable_multiple_nodes():
    """Test 3: Disable multiple nodes via config"""
    print("Test 3: Disable multiple nodes via config")
    config = Config(criticism_enabled=False, web_research_enabled=False, github_issue_enabled=False)
    print(f"  criticism enabled? {config.is_node_enabled('criticism')}")
    print(f"  web_research enabled? {config.is_node_enabled('web_research')}")
    print(f"  github_issue enabled? {config.is_node_enabled('github_issue')}")
    print(f"  plan enabled? {config.is_node_enabled('plan')}")
    print(f"  Enabled nodes: {config.get_enabled_nodes()}")
    print(f"  Disabled nodes: {config.get_disabled_nodes()}")
    assert config.is_node_enabled("criticism") is False
    assert config.is_node_enabled("web_research") is False
    assert config.is_node_enabled("github_issue") is False
    assert config.is_node_enabled("plan") is True
    assert set(config.get_disabled_nodes()) == {"criticism", "web_research", "github_issue"}
    print("  ✅ PASSED\n")


def test_load_from_json_file():
    """Test 4: Load from file (JSON)"""
    print("Test 4: Load from JSON file")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"criticism_enabled": False, "plan_enabled": False, "openai_api_key": "test-key"}, f)
        temp_file = f.name

    try:
        config = Config.from_file(temp_file)
        print(f"  criticism enabled? {config.is_node_enabled('criticism')}")
        print(f"  plan enabled? {config.is_node_enabled('plan')}")
        print(f"  Enabled nodes: {config.get_enabled_nodes()}")
        print(f"  Disabled nodes: {config.get_disabled_nodes()}")
        assert config.is_node_enabled("criticism") is False
        assert config.is_node_enabled("plan") is False
        assert set(config.get_disabled_nodes()) == {"criticism", "plan"}
        print("  ✅ PASSED\n")
    finally:
        os.unlink(temp_file)


def test_env_vars_work_by_default():
    """Test 5: Environment variables work by default"""
    print("Test 5: Environment variables work by default (pydantic BaseSettings)")

    # Set environment variables
    old_env = os.environ.copy()
    os.environ["CRITICISM_ENABLED"] = "false"
    os.environ["PLAN_ENABLED"] = "false"

    try:
        config = Config()
        print(f"  criticism enabled? {config.is_node_enabled('criticism')}")
        print(f"  plan enabled? {config.is_node_enabled('plan')}")
        print(f"  Disabled nodes: {config.get_disabled_nodes()}")

        # Environment variables should work with default Config()
        assert config.is_node_enabled("criticism") is False
        assert config.is_node_enabled("plan") is False
        assert set(config.get_disabled_nodes()) == {"plan", "criticism"}
        print("  ✅ PASSED - Environment variables work correctly\n")
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(old_env)


def test_config_file_overrides_env():
    """Test 6: Config file overrides environment variables"""
    print("Test 6: Config file takes precedence over environment")

    # Set conflicting environment variables
    old_env = os.environ.copy()
    os.environ["CRITICISM_ENABLED"] = "true"  # env says enabled
    os.environ["PLAN_ENABLED"] = "true"  # env says enabled

    try:
        # Create config file that disables them
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "criticism_enabled": False,  # file says disabled
                    "plan_enabled": False,  # file says disabled
                    "openai_api_key": "test-key",
                },
                f,
            )
            temp_file = f.name

        try:
            config = Config.from_file(temp_file)
            print(f"  criticism enabled? {config.is_node_enabled('criticism')}")
            print(f"  plan enabled? {config.is_node_enabled('plan')}")
            print(f"  Disabled nodes: {config.get_disabled_nodes()}")

            # Config file should override environment
            assert config.is_node_enabled("criticism") is False
            assert config.is_node_enabled("plan") is False
            assert set(config.get_disabled_nodes()) == {"plan", "criticism"}
            print("  ✅ PASSED - Config file correctly overrides environment\n")
        finally:
            os.unlink(temp_file)
    finally:
        # Restore environment
        os.environ.clear()
        os.environ.update(old_env)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Node Enable/Disable Configuration")
    print("=" * 60 + "\n")

    try:
        test_default_config()
        test_disable_criticism()
        test_disable_multiple_nodes()
        test_load_from_json_file()
        test_env_vars_work_by_default()
        test_config_file_overrides_env()

        print("=" * 60)
        print("All tests passed! ✅")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
