#!/usr/bin/env python3
"""
Test the new component research context formatting.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.prompts import ResearchPrompts


def test_format_component_research_context():
    """Test the new format_component_research_context method."""

    research_plan = "Study cryptocurrency trading strategies focusing on mean reversion and momentum"

    component_research_results = {
        "ALPHA": [
            {
                "title": "Alpha Research Approach 1: Mean Reversion",
                "content": "Mean reversion strategies work well in crypto markets due to high volatility...",
                "approach_number": 1,
            },
            {
                "title": "Alpha Research Approach 2: Momentum",
                "content": "Momentum strategies capitalize on trend persistence...",
                "approach_number": 2,
            },
        ],
        "UNIVERSE": [
            {
                "title": "Universe Research: Crypto Selection",
                "content": "Top 20-50 cryptocurrencies by market cap provide good liquidity...",
                "approach_number": 1,
            }
        ],
    }

    web_results = [
        {"title": "Fallback Web Result", "content": "This would be used if no component results available..."}
    ]

    idea = "Cryptocurrency momentum and mean reversion strategy"

    # Test the formatting
    formatted_context = ResearchPrompts.format_component_research_context(
        research_plan, component_research_results, web_results, idea
    )

    print("=== FORMATTED COMPONENT RESEARCH CONTEXT ===")
    print(formatted_context)
    print("\n=== VALIDATION ===")

    # Check that it includes all expected elements
    assert "Research Idea: " + idea in formatted_context
    assert "Research Plan:" in formatted_context
    assert research_plan in formatted_context
    assert "COMPONENT-SPECIFIC RESEARCH FINDINGS:" in formatted_context
    assert "=== ALPHA RESEARCH ===" in formatted_context
    assert "=== UNIVERSE RESEARCH ===" in formatted_context
    assert "Approach 1: Alpha Research Approach 1: Mean Reversion" in formatted_context
    assert "Approach 2: Alpha Research Approach 2: Momentum" in formatted_context
    assert "Mean reversion strategies work well" in formatted_context

    print("✓ All validation checks passed!")
    print("✓ Component research context formatting works correctly")


def test_fallback_to_web_results():
    """Test fallback to web results when no component results."""

    research_plan = "Study trading strategies"
    component_research_results = {}  # Empty
    web_results = [
        {"title": "Web Search Result 1", "content": "Some general trading strategy information from web search..."},
        {"title": "Web Search Result 2", "content": "More trading information from another source..."},
    ]
    idea = "Test trading strategy"

    formatted_context = ResearchPrompts.format_component_research_context(
        research_plan, component_research_results, web_results, idea
    )

    print("\n=== FALLBACK TO WEB RESULTS TEST ===")
    print(formatted_context)

    # Should contain web results instead of component results
    assert "GENERAL RESEARCH FINDINGS:" in formatted_context
    assert "Web Search Result 1" in formatted_context
    assert "Web Search Result 2" in formatted_context
    assert "COMPONENT-SPECIFIC RESEARCH FINDINGS:" not in formatted_context

    print("✓ Fallback to web results works correctly!")


if __name__ == "__main__":
    test_format_component_research_context()
    test_fallback_to_web_results()
    print("\n🎉 All tests passed! The component research context formatting is working correctly.")
