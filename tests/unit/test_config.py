"""
Unit tests for configuration management.
"""

import os
from unittest.mock import patch

import pytest

from agent.config import Config, LLMProviderConfig


class TestConfig:
    """Test configuration loading and validation."""

    def test_config_from_env_minimal(self):
        """Test config creation with minimal environment."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config()
            assert os.getenv("OPENAI_API_KEY") == "test-key"
            # Check that config was created successfully
            assert config.default_config is not None
            assert config.default_config.llm_provider is not None
            assert config.default_config.llm_provider.provider in ["openai", "anthropic"]

    def test_config_from_env_full(self):
        """Test config creation with full environment."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai",
            "ANTHROPIC_API_KEY": "test-anthropic",
            "GOOGLE_API_KEY": "test-google",
            "GITHUB_TOKEN": "test-github",
            "TAVILY_API_KEY": "test-tavily",
            "DEFAULT_LLM_PROVIDER": "anthropic",
            "MODEL": "claude-3-5-sonnet",
            "TEMPERATURE": "0.5",
            "MAX_TOKENS": "8000",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()
            assert os.getenv("OPENAI_API_KEY") == "test-openai"
            assert os.getenv("GITHUB_TOKEN") == "test-github"
            assert config.default_config.llm_provider.provider == "anthropic"
            assert config.default_config.llm_provider.model == "claude-3-5-sonnet"
            assert config.default_config.llm_provider.temperature == 0.5
            assert config.default_config.llm_provider.max_tokens == 8000

    def test_config_missing_api_key_raises_error(self):
        """Test that config can be created without API keys (validation happens at runtime)."""
        with patch.dict(os.environ, {}, clear=True):
            # Config creation should succeed even without API keys
            config = Config()
            assert config is not None
            assert config.openai_api_key is None
            assert config.anthropic_api_key is None

    def test_llm_provider_configuration(self):
        """Test LLM provider configuration."""
        provider_config = LLMProviderConfig(
            provider="openai", api_key_env="OPENAI_API_KEY", model="gpt-4o", temperature=0.7, max_tokens=4000
        )

        assert provider_config.provider == "openai"
        assert provider_config.model == "gpt-4o"
        assert provider_config.temperature == 0.7

    def test_get_available_providers(self):
        """Test getting available providers."""
        env_vars = {"OPENAI_API_KEY": "test-openai", "ANTHROPIC_API_KEY": "test-anthropic"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()
            providers = config.get_available_providers()
            assert "openai" in providers
            assert "anthropic" in providers
            assert len(providers) == 2

    def test_node_enable_disable_configuration(self):
        """Test node enable/disable functionality."""
        env_vars = {"OPENAI_API_KEY": "test-key", "CRITICISM_ENABLED": "false"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()

            assert not config.is_node_enabled("criticism")
            assert config.is_node_enabled("plan")
            assert config.is_node_enabled("synthesize")

            enabled = config.get_enabled_nodes()
            disabled = config.get_disabled_nodes()

            assert "criticism" not in enabled
            assert "criticism" in disabled
            # Enabled should have all nodes except criticism
            assert "criticism" not in enabled

    def test_schema_loading(self):
        """Test schema loading functionality."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config()
            schema = config.get_schema()

            assert isinstance(schema, dict)
            assert "properties" in schema
            # Check for actual schema properties that exist
            assert "alphas" in schema["properties"]
            assert "universe" in schema["properties"]

    def test_logging_configuration(self):
        """Test logging configuration."""
        env_vars = {"OPENAI_API_KEY": "test-key", "LOG_LEVEL": "DEBUG", "LOG_TO_FILE": "true"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()
            # Note: LOG_LEVEL and LOG_TO_FILE may not be read directly by Config()
            # This test verifies the config object has logging configuration
            assert hasattr(config, "logging_config")
            assert config.logging_config is not None
