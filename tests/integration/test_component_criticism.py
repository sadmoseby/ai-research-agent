#!/usr/bin/env python3
"""
Test script to verify component-specific criticism functionality
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from agent.config import Config
from agent.nodes.criticism import _generate_criticism_analysis, criticism_node
from agent.prompts import ResearchPrompts
from agent.state import ResearchComponents, ResearchState


async def test_component_criticism():
    """Test the component-specific criticism functionality"""

    # Mock state with component research results
    state = ResearchState()
    state["idea"] = "momentum strategy based on earnings surprises"
    state["research_plan"] = "Research earnings momentum strategies"
    state["alpha_only"] = False
    state["components"] = ResearchComponents.ALPHA | ResearchComponents.UNIVERSE
    state["component_research_results"] = {
        "ALPHA": [
            {
                "title": "Alpha Research: Earnings Momentum",
                "content": (
                    "Research on earnings momentum alpha signals including surprise factors, "
                    "analyst revisions, and post-earnings drift patterns..."
                ),
                "component": "ALPHA",
                "research_type": "component_specific",
            }
        ],
        "UNIVERSE": [
            {
                "title": "Universe Research: Large Cap Equities",
                "content": (
                    "Analysis of large cap equity universe selection criteria including "
                    "liquidity filters, market cap thresholds..."
                ),
                "component": "UNIVERSE",
                "research_type": "component_specific",
            }
        ],
    }
    state["web_search_results"] = []
    state["prior_art_results"] = {"verdict": "novel", "total_found": 0}

    # Mock config
    config = MagicMock()
    config.get_components_from_env.return_value = None

    # Test formatting of component criticism context
    print("✓ Testing component criticism context formatting...")
    context = ResearchPrompts.format_component_criticism_context(
        research_plan="Test research plan",
        component_research_results=state["component_research_results"],
        web_results=[],
        idea="test idea",
    )

    assert "=== ALPHA RESEARCH ===" in context
    assert "=== UNIVERSE RESEARCH ===" in context
    assert "Earnings Momentum" in context
    assert "Large Cap Equities" in context
    print("✓ Component criticism context formatting works correctly")

    # Test component score extraction
    print("✓ Testing component score extraction...")
    mock_criticism = """
    This is a detailed analysis.

    COMPONENT_SCORE_ALPHA: 75
    COMPONENT_SCORE_UNIVERSE: 82
    COMPONENT_SCORE_RISK: 60

    Overall assessment shows promise.

    VIABILITY SCORE: 78
    """

    component_scores = ResearchPrompts.extract_component_scores(mock_criticism)
    viability_score = ResearchPrompts.extract_viability_score(mock_criticism)

    assert component_scores["ALPHA"] == 75.0
    assert component_scores["UNIVERSE"] == 82.0
    assert component_scores["RISK"] == 60.0
    assert viability_score == 78.0
    print("✓ Component score extraction works correctly")

    # Test prompt accessibility
    print("✓ Testing component criticism prompts...")
    assert hasattr(ResearchPrompts, "COMPONENT_CRITICISM_SYSTEM_PROMPT")
    assert hasattr(ResearchPrompts, "COMPONENT_CRITICISM_USER_PROMPT")
    assert "UNIVERSE Component:" in ResearchPrompts.COMPONENT_CRITICISM_SYSTEM_PROMPT
    assert "ALPHA Component:" in ResearchPrompts.COMPONENT_CRITICISM_SYSTEM_PROMPT
    print("✓ Component criticism prompts are accessible")

    print("✓ All component criticism tests passed!")


def test_backward_compatibility():
    """Test that non-component research still works"""
    print("✓ Testing backward compatibility...")

    # Test with traditional web results
    context = ResearchPrompts.format_component_criticism_context(
        research_plan="Test plan",
        component_research_results={},  # No component results
        web_results=[{"title": "General Research", "content": "General trading strategy research..."}],
        idea="test strategy",
    )

    assert "GENERAL RESEARCH FINDINGS:" in context
    assert "General Research" in context
    print("✓ Backward compatibility works correctly")


if __name__ == "__main__":
    test_backward_compatibility()
    asyncio.run(test_component_criticism())
    print("🎉 All component criticism tests completed successfully!")
