"""
Test configuration and fixtures for the AI Research Agent.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import Mock, patch

import pytest

from agent.config import Config
from agent.state import ResearchState


@pytest.fixture(scope="session")
def test_env_vars() -> Dict[str, str]:
    """Test environment variables."""
    return {
        "OPENAI_API_KEY": "test-openai-key",
        "ANTHROPIC_API_KEY": "test-anthropic-key",
        "GOOGLE_API_KEY": "test-google-key",
        "GITHUB_TOKEN": "test-github-token",
        "TAVILY_API_KEY": "test-tavily-key",
        "DEFAULT_LLM_PROVIDER": "openai",
        "MODEL": "gpt-4o",
        "TEMPERATURE": "0.7",
        "MAX_TOKENS": "4000",
        "LOG_LEVEL": "INFO",
    }


@pytest.fixture(scope="function")
def mock_env(test_env_vars: Dict[str, str]) -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    with patch.dict(os.environ, test_env_vars, clear=False):
        yield


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def test_config(mock_env) -> Config:
    """Create test configuration."""
    return Config()


@pytest.fixture
def test_state() -> ResearchState:
    """Create test research state."""
    return ResearchState(
        idea="test momentum strategy",
        alpha_only=True,
        slug="test-momentum",
        current_step="plan",
        repair_attempts=0,
        planning_iterations=0,
    )


@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """Mock LLM response."""
    return {"choices": [{"message": {"content": "Test response from mock LLM"}}]}


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(choices=[Mock(message=Mock(content="Test response"))])
    return mock_client


@pytest.fixture
def sample_schema() -> Dict[str, Any]:
    """Sample JSON schema for testing."""
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "alphas": {
                "type": "object",
                "properties": {
                    "new": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"name": {"type": "string"}, "text": {"type": "string"}},
                            "required": ["name", "text"],
                        },
                    }
                },
            },
            "universe": {"type": "object", "properties": {"existing": {"type": "array", "items": {"type": "string"}}}},
        },
        "required": ["title", "summary", "alphas", "universe"],
    }


@pytest.fixture
def sample_proposal() -> Dict[str, Any]:
    """Sample research proposal."""
    return {
        "title": "Test Momentum Strategy",
        "summary": "A test momentum-based trading strategy",
        "alphas": {"new": [{"name": "TestMomentumAlpha", "text": "Buy stocks with positive 12-month momentum"}]},
        "universe": {"existing": ["QTradableStocksUS"]},
    }


@pytest.fixture
def mock_web_search_results() -> Dict[str, Any]:
    """Mock web search results."""
    return {
        "results": [
            {
                "title": "Momentum Trading Strategies",
                "url": "https://example.com/momentum",
                "content": "Overview of momentum trading approaches",
            },
            {
                "title": "Risk Management in Algorithmic Trading",
                "url": "https://example.com/risk",
                "content": "Best practices for managing trading risks",
            },
        ]
    }


@pytest.fixture
def mock_github_search_results() -> Dict[str, Any]:
    """Mock GitHub search results."""
    return {
        "total_count": 2,
        "items": [
            {
                "name": "momentum-strategy",
                "full_name": "user/momentum-strategy",
                "description": "A momentum-based trading strategy",
                "html_url": "https://github.com/user/momentum-strategy",
                "stargazers_count": 15,
            },
            {
                "name": "trend-following",
                "full_name": "org/trend-following",
                "description": "Trend following algorithms",
                "html_url": "https://github.com/org/trend-following",
                "stargazers_count": 42,
            },
        ],
    }


# Test markers for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.slow = pytest.mark.slow
pytest.mark.requires_api = pytest.mark.requires_api
pytest.mark.requires_mcp = pytest.mark.requires_mcp
