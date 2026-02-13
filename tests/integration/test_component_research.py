#!/usr/bin/env python3
"""
Test script to verify component-specific research functionality
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from agent.config import Config
from agent.nodes.web_research import _conduct_component_research, web_research_node
from agent.prompts import ResearchPrompts
from agent.state import ResearchComponents, ResearchState


async def test_component_research():
    """Test the component-specific research functionality"""

    # Mock state
    state = ResearchState()
    state["idea"] = "momentum strategy based on earnings surprises"
    state["research_plan"] = "Research earnings momentum strategies"
    state["alpha_only"] = False
    state["components"] = ResearchComponents.ALPHA | ResearchComponents.UNIVERSE | ResearchComponents.RISK

    # Mock config
    config = MagicMock()
    config.get_components_from_env.return_value = None

    # Mock MCP client
    mock_mcp_client = AsyncMock()
    mock_mcp_client.get_available_tool_names.return_value = ["web_search", "tavily_search"]
    mock_mcp_client.web_search.return_value = [
        {
            "content": """
Approach 1: Fundamental Analysis-Based Momentum
This approach uses earnings surprise data and fundamental metrics to generate alpha signals.

Approach 2: Technical Momentum Indicators
This approach combines multiple technical indicators with earnings timing.

Approach 3: Machine Learning Ensemble
This approach uses ML models to predict post-earnings momentum patterns.
            """.strip(),
            "title": "Mock Research Result",
            "url": "https://mock.example.com",
        }
    ]
    mock_mcp_client.close = AsyncMock()

    # Test that the prompts are accessible
    print("✓ Testing prompt accessibility...")
    assert "ALPHA" in ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS
    assert "UNIVERSE" in ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS
    assert "RISK" in ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS
    assert "PORTFOLIO" in ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS
    assert "EXECUTION" in ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS
    print("✓ All component prompts are accessible")

    # Test component research function
    print("✓ Testing component research function...")
    results = await _conduct_component_research(
        mock_mcp_client, "ALPHA", "momentum strategy", "research plan", False, ["web_search"], []
    )

    assert results is not None
    assert isinstance(results, list)
    assert len(results) >= 1  # Should parse multiple approaches

    # Check first result
    first_result = results[0]
    assert first_result["component"] == "ALPHA"
    assert first_result["research_type"] == "component_specific"
    assert "approach_number" in first_result

    # If multiple approaches were parsed, check that they have different approach numbers
    if len(results) > 1:
        approach_numbers = [r["approach_number"] for r in results]
        assert len(set(approach_numbers)) == len(approach_numbers), "Approach numbers should be unique"

    print(f"✓ Component research function returned {len(results)} approaches")
    print("✓ Component research function works correctly")

    print("✓ All tests passed!")


def test_component_flags():
    """Test component flag handling"""
    print("✓ Testing component flags...")

    # Test individual components
    assert ResearchComponents.ALPHA == 1 << 1
    assert ResearchComponents.UNIVERSE == 1 << 0
    assert ResearchComponents.RISK == 1 << 4
    assert ResearchComponents.PORTFOLIO == 1 << 2
    assert ResearchComponents.EXECUTION == 1 << 3

    # Test combined components
    combined = ResearchComponents.ALPHA | ResearchComponents.UNIVERSE
    assert combined & ResearchComponents.ALPHA
    assert combined & ResearchComponents.UNIVERSE
    assert not (combined & ResearchComponents.RISK)

    print("✓ Component flags work correctly")


if __name__ == "__main__":
    test_component_flags()
    asyncio.run(test_component_research())
    print("🎉 All tests completed successfully!")
