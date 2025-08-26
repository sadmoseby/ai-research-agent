#!/usr/bin/env python3
"""
Example demonstrating the component-by-component synthesis approach.

This example shows how to use the component-based synthesis mode, where
research results are organized by component (ALPHA, UNIVERSE, PORTFOLIO, etc.)
and synthesis occurs component by component rather than all at once.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import Config
from agent.nodes.synthesize import synthesize_node
from agent.state import ResearchState

# Set up environment for component synthesis
os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"


async def demo_component_synthesis():
    """Demonstrate the component-by-component synthesis approach."""

    print("🔬 Component-by-Component Synthesis Demo")
    print("=" * 50)

    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please set up your .env file with required API keys.")
        return

    # Mock component research results structure for demonstration
    component_search_results = {
        "ALPHA": [
            {
                "title": "Alpha Research Approach 1: Mean Reversion Strategy",
                "content": "Mean reversion strategies exploit the tendency of asset prices to return to their average value over time. In the cryptocurrency market, this approach can be particularly effective due to high volatility. Key parameters include lookback period (10-50 days), threshold multipliers (1.5-3.0 standard deviations), and position sizing based on deviation magnitude.",
                "url": "llm_component_research",
                "source": "llm_with_web_tools",
                "research_type": "component_specific",
                "component": "ALPHA",
                "approach_number": 1,
            },
            {
                "title": "Alpha Research Approach 2: Momentum Factor",
                "content": "Momentum strategies capitalize on the persistence of price trends. For crypto markets, 12-1 month momentum (excluding last month) has shown effectiveness. Implementation involves ranking assets by past returns and going long top performers while shorting bottom performers. Risk management through volatility scaling is crucial.",
                "url": "llm_component_research",
                "source": "llm_with_web_tools",
                "research_type": "component_specific",
                "component": "ALPHA",
                "approach_number": 2,
            },
        ],
        "UNIVERSE": [
            {
                "title": "Universe Research: Cryptocurrency Selection Criteria",
                "content": "For cryptocurrency universe construction, key criteria include: minimum market capitalization ($100M+), minimum daily trading volume ($10M+), availability on major exchanges, and data quality requirements. Top 20-50 cryptocurrencies by market cap provide good balance of liquidity and diversification while avoiding micro-cap volatility.",
                "url": "llm_component_research",
                "source": "llm_with_web_tools",
                "research_type": "component_specific",
                "component": "UNIVERSE",
                "approach_number": 1,
            }
        ],
        "RISK": [
            {
                "title": "Risk Management: Volatility-Based Position Sizing",
                "content": "Crypto markets require robust risk management due to extreme volatility. Implement position sizing based on realized volatility with maximum position limits (5-10% per asset), stop-losses, and portfolio-level risk budgeting. Use VaR calculations with shorter time horizons (1-day) given crypto's rapid price movements.",
                "url": "llm_component_research",
                "source": "llm_with_web_tools",
                "research_type": "component_specific",
                "component": "RISK",
                "approach_number": 1,
            }
        ],
    }

    print("=== DEMO: Component-by-Component Synthesis ===\n")

    print("1. COMPONENT RESEARCH RESULTS STRUCTURE:")
    print("   Components with research data:", list(component_search_results.keys()))

    for component, results in component_search_results.items():
        print(f"   {component}: {len(results)} approaches")
        for i, result in enumerate(results, 1):
            print(f"     - Approach {i}: {result['title'][:50]}...")

    print("\n2. SYNTHESIS APPROACH COMPARISON:")
    print("   Traditional: Single LLM call with all research data combined")
    print("   Component-by-component: Separate LLM calls per component + combination")

    print("\n3. BENEFITS OF COMPONENT-BY-COMPONENT APPROACH:")
    print("   ✓ More focused generation per component")
    print("   ✓ Better handling of component-specific research")
    print("   ✓ Easier to debug individual component issues")
    print("   ✓ Parallel generation possible for performance")
    print("   ✓ Component-specific prompts and validation")

    print("\n4. EXPECTED OUTPUT STRUCTURE:")
    expected_structure = {
        "alphas": {
            "new": [
                {
                    "name": "crypto_mean_reversion_alpha",
                    "componentId": "mean_reversion_v1",
                    "title": "Cryptocurrency Mean Reversion Strategy",
                    "description": "Mean reversion strategy for crypto markets",
                    "text": "Strategy exploiting mean reversion in crypto prices...",
                    "params": [
                        {
                            "name": "lookback_period",
                            "type": "int",
                            "value": 20,
                            "minimum": 10,
                            "maximum": 50,
                            "tuning": {"distribution": "uniform"},
                        }
                    ],
                }
            ]
        },
        "universe": {"new": [{"name": "crypto_universe", "...": "..."}]},
        "risk": {"new": [{"name": "volatility_risk_mgmt", "...": "..."}]},
        "misc": {
            "synthesis_method": "component_by_component",
            "generated_by": "lean-research-agent-mcp-component-synthesis",
        },
    }

    print(json.dumps(expected_structure, indent=2))

    print("\n5. CONFIGURATION:")
    print("   Set SYNTHESIZE_COMPONENT_BY_COMPONENT=true to enable")
    print("   Only used when component_research_results is available")
    print("   Falls back to unified approach if alpha_only=true")

    print("\n6. IMPLEMENTATION DETAILS:")
    print("   - Each component gets its own optimized prompt")
    print("   - Component-specific schema validation")
    print("   - Research content is fully included (not truncated)")
    print("   - Final combination preserves all component details")


if __name__ == "__main__":
    asyncio.run(demo_component_synthesis())
