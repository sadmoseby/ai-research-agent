"""
Tests for validation MCP tool functionality.
"""

import json
from unittest.mock import AsyncMock, Mock

import pytest

from agent.config import Config
from agent.tools.validation_mcp_tool import ValidationMCPTool


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = Mock(spec=Config)

    # Mock the schema
    mock_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "alphas": {"type": "object", "properties": {"new": {"type": "array", "items": {"type": "object"}}}},
        },
        "required": ["title"],
    }
    config.get_schema.return_value = mock_schema
    return config


@pytest.fixture
def validation_tool(mock_config):
    """Create a validation MCP tool instance."""
    return ValidationMCPTool(mock_config)


def test_validate_proposal_success(validation_tool):
    """Test successful proposal validation."""
    valid_proposal = {"title": "Test Strategy", "alphas": {"new": []}}

    result = validation_tool.validate_proposal(valid_proposal)

    assert result["is_valid"] is True
    assert result["errors"] == []
    assert "success" in result["report"].lower()


def test_validate_proposal_missing_required_field(validation_tool):
    """Test validation failure with missing required field."""
    invalid_proposal = {
        "alphas": {"new": []}
        # Missing required "title" field
    }

    result = validation_tool.validate_proposal(invalid_proposal)

    assert result["is_valid"] is False
    assert len(result["errors"]) > 0
    assert any("title" in error for error in result["errors"])


def test_validate_proposal_empty(validation_tool):
    """Test validation with empty proposal."""
    result = validation_tool.validate_proposal({})

    assert result["is_valid"] is False
    assert "No proposal" in result["errors"][0]


def test_validate_proposal_none(validation_tool):
    """Test validation with None proposal."""
    result = validation_tool.validate_proposal(None)

    assert result["is_valid"] is False
    assert "No proposal" in result["errors"][0]


async def test_repair_proposal_success(validation_tool, mock_config):
    """Test successful proposal repair."""
    invalid_proposal = {"alphas": {"new": []}}  # Missing title
    validation_errors = ["'title' is a required property"]

    # Mock LLM client using AsyncMock
    mock_llm_client = AsyncMock()
    mock_llm_client.structured_completion.return_value = {"title": "Repaired Strategy", "alphas": {"new": []}}

    result = await validation_tool.repair_proposal(
        proposal=invalid_proposal,
        validation_errors=validation_errors,
        llm_client=mock_llm_client,
        idea="test strategy",
        alpha_only=False,
    )

    assert result is not None
    assert "title" in result
    assert result["title"] == "Repaired Strategy"

    # Verify LLM was called with correct parameters
    mock_llm_client.structured_completion.assert_called_once()


async def test_repair_proposal_llm_failure(validation_tool):
    """Test proposal repair when LLM fails."""
    invalid_proposal = {"alphas": {"new": []}}
    validation_errors = ["'title' is a required property"]

    # Mock LLM client that fails
    mock_llm_client = Mock()
    mock_llm_client.generate_structured_output.side_effect = Exception("LLM failed")

    result = await validation_tool.repair_proposal(
        proposal=invalid_proposal,
        validation_errors=validation_errors,
        llm_client=mock_llm_client,
        idea="test strategy",
        alpha_only=False,
    )

    assert result is None


async def test_repair_proposal_alpha_only(validation_tool):
    """Test proposal repair in alpha-only mode."""
    invalid_proposal = {"alphas": {"new": []}}
    validation_errors = ["'title' is a required property"]

    # Mock LLM client using AsyncMock
    mock_llm_client = AsyncMock()
    mock_llm_client.structured_completion.return_value = {
        "title": "Alpha Strategy",
        "alphas": {"new": []},
        "alpha-only": True,
    }

    result = await validation_tool.repair_proposal(
        proposal=invalid_proposal,
        validation_errors=validation_errors,
        llm_client=mock_llm_client,
        idea="test alpha strategy",
        alpha_only=True,
    )

    assert result is not None
    assert "title" in result

    # Check that alpha-only mode was passed in the system prompt
    call_args = mock_llm_client.structured_completion.call_args
    messages = call_args[1]["messages"]
    system_message = next(msg["content"] for msg in messages if msg["role"] == "system")

    assert "alpha-only" in system_message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
