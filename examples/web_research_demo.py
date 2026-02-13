#!/usr/bin/env python3
"""
Demo script showcasing the new comprehensive web research node functionality.
"""

import asyncio

from agent.config import Config
from agent.nodes.web_research import web_research_node
from agent.prompts import ResearchPrompts
from agent.state import ResearchState


async def demo_comprehensive_web_research():
    """Demonstrate the new comprehensive web research approach."""

    print("=== Comprehensive Web Research Node Demo ===\n")

    # Example research state
    state = ResearchState(
        {
            "idea": "Momentum-based factor investing using machine learning for portfolio optimization",
            "research_plan": "Investigate ML-enhanced momentum strategies for factor-based portfolio construction",
            "alpha_only": True,
            "current_step": "web_research",
        }
    )

    # Load configuration (this would normally be from config files)
    try:
        config = Config()
        print("Configuration loaded successfully")
    except Exception as e:
        print(f"Could not load full config: {e}")
        print("This demo shows the structure - actual execution requires proper MCP setup")
        return

    print(f"\nResearch Idea: {state['idea']}")
    print(f"Alpha-only mode: {state['alpha_only']}")
    print("Research Plan: {}".format(state["research_plan"]))

    print("\n=== New Comprehensive Research Approach ===")
    print("✓ Single comprehensive LLM-based research session")
    print("✓ Uses OpenAI Responses API with native web search tool")
    print("✓ Expands original idea into verbose detailed proposal")
    print("✓ Suitable for later JSON schema conversion")

    print("\n=== Available Prompts ===")
    print(
        "✓ WEB_RESEARCH_COMPREHENSIVE_SYSTEM_PROMPT: {}".format(
            hasattr(ResearchPrompts, "WEB_RESEARCH_COMPREHENSIVE_SYSTEM_PROMPT")
        )
    )
    print(
        "✓ WEB_RESEARCH_COMPREHENSIVE_USER_PROMPT: {}".format(
            hasattr(ResearchPrompts, "WEB_RESEARCH_COMPREHENSIVE_USER_PROMPT")
        )
    )

    # Show the structure of what would happen
    print("\n=== Research Flow ===")
    print("1. Initialize LLM client with OpenAI Responses API")
    print("2. Create comprehensive system prompt")
    print("3. Generate detailed user prompt with idea + context")
    print("4. Use OpenAI's native web search tool for research")
    print("5. Return single comprehensive research document")

    print("\n=== Expected Output Structure ===")
    print("Single comprehensive result containing:")
    print("- Strategy overview & market context")
    print("- Methodology & implementation approach")
    print("- Academic & industry research")
    print("- Risk analysis & considerations")
    print("- Parameter optimization details")
    print("- Universe definition (for alpha-only mode)")

    try:
        # This would actually run the comprehensive research
        # result = await web_research_node(state, config)
        # print(f"\n=== Actual Results ===")
        # print(f"Results: {len(result['web_search_results'])} comprehensive research documents")
        # print(f"Tools used: {result['mcp_tools_used']}")
        pass
    except Exception as e:
        print(f"\nNote: Full execution requires proper LLM and MCP setup: {e}")

    print("\n=== Summary ===")
    print("✓ Modified web_research_node for comprehensive research")
    print("✓ Added comprehensive research prompts")
    print("✓ Uses OpenAI Responses API with native web search")
    print("✓ Generates detailed proposals suitable for JSON conversion")


if __name__ == "__main__":
    asyncio.run(demo_comprehensive_web_research())
