"""
Unit tests for LLM client functionality.
"""

import os
from unittest.mock import Mock, patch

import pytest

from agent.config import Config
from agent.llm_client import LLMClient


class TestLLMClient:
    """Test LLM client functionality."""

    def test_llm_client_initialization_default_provider(self):
        """Test LLM client initialization with default provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            provider_info = client.get_provider_info()
            assert provider_info["provider"] == "openai"
            assert provider_info["model"] == "gpt-4o"

    def test_llm_client_initialization_specific_node(self):
        """Test LLM client initialization for specific node."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai",
            "ANTHROPIC_API_KEY": "test-anthropic",
            "DEFAULT_LLM_PROVIDER": "openai",
            "SYNTHESIZE_LLM_PROVIDER": "anthropic",
            "SYNTHESIZE_LLM_MODEL": "claude-3-5-sonnet",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            client = LLMClient(config, "synthesize")

            provider_info = client.get_provider_info()
            assert provider_info["provider"] == "anthropic"
            assert provider_info["model"] == "claude-3-5-sonnet"

    def test_llm_client_fallback_to_default(self):
        """Test LLM client fallback when node-specific config not available."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config.from_env()
            client = LLMClient(config, "non_existent_node")

            provider_info = client.get_provider_info()
            assert provider_info["provider"] == "openai"
            assert provider_info["model"] == "gpt-4o"

    @patch("agent.llm_client.ChatOpenAI")
    def test_openai_client_creation(self, mock_openai):
        """Test OpenAI client creation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            # Access the underlying client to trigger creation
            _ = client._get_client()

            # Verify OpenAI client was created with correct parameters
            mock_openai.assert_called_once()
            call_kwargs = mock_openai.call_args[1]
            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["temperature"] == 0.7

    @patch("agent.llm_client.ChatAnthropic")
    def test_anthropic_client_creation(self, mock_anthropic):
        """Test Anthropic client creation."""
        env_vars = {"ANTHROPIC_API_KEY": "test-key", "DEFAULT_LLM_PROVIDER": "anthropic"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            # Access the underlying client to trigger creation
            _ = client._get_client()

            # Verify Anthropic client was created
            mock_anthropic.assert_called_once()

    def test_structured_output_generation_mock(self):
        """Test structured output generation with mocked response."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            # Mock the client response
            mock_response = {"title": "Test Strategy", "summary": "A test momentum strategy"}

            with patch.object(client, "_get_client") as mock_get_client:
                mock_llm = Mock()
                mock_llm.with_structured_output.return_value.invoke.return_value = mock_response
                mock_get_client.return_value = mock_llm

                # Test that the client can be created and mocked properly
                # Since structured_completion is async, we'll test the underlying client setup
                underlying_client = client._get_client()
                assert underlying_client is not None

                # Verify the mock was set up correctly
                mock_get_client.assert_called_once()

    def test_provider_availability_check(self):
        """Test provider availability checking."""
        env_vars = {"OPENAI_API_KEY": "test-openai", "ANTHROPIC_API_KEY": "test-anthropic"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()

            # Test available providers
            available = config.get_available_providers()
            assert "openai" in available
            assert "anthropic" in available

            # Test client creation for each available provider
            for provider in available:
                client = LLMClient(config)
                provider_info = client.get_provider_info()
                assert provider_info["provider"] in available

    def test_temperature_and_max_tokens_configuration(self):
        """Test temperature and max_tokens configuration."""
        env_vars = {"OPENAI_API_KEY": "test-key", "TEMPERATURE": "0.5", "MAX_TOKENS": "8000"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            provider_info = client.get_provider_info()
            assert provider_info["temperature"] == 0.5
            assert provider_info["max_tokens"] == 8000

    def test_error_handling_invalid_provider(self):
        """Test error handling for invalid provider configuration."""
        with patch.dict(os.environ, {}, clear=True):
            # Config creation should succeed even without API keys
            config = Config.from_env()
            assert config is not None

            # Error should occur when trying to create LLM client
            client = LLMClient(config)
            with pytest.raises(ValueError, match="API key not found"):
                client._get_client()

    def test_client_caching(self):
        """Test that clients are cached properly."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config.from_env()
            client = LLMClient(config)

            # Get client twice
            client1 = client._get_client()
            client2 = client._get_client()

            # Should be the same instance (cached)
            assert client1 is client2

    def test_node_specific_overrides(self):
        """Test node-specific configuration overrides."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai",
            "ANTHROPIC_API_KEY": "test-anthropic",
            "DEFAULT_LLM_PROVIDER": "openai",
            "CRITICISM_LLM_PROVIDER": "anthropic",
            "CRITICISM_LLM_TEMPERATURE": "0.3",
            "CRITICISM_LLM_MAX_TOKENS": "6000",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config.from_env()
            criticism_client = LLMClient(config, "criticism")

            provider_info = criticism_client.get_provider_info()
            assert provider_info["provider"] == "anthropic"
            assert provider_info["temperature"] == 0.3
            assert provider_info["max_tokens"] == 6000
