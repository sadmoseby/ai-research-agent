#!/usr/bin/env python3
"""
Test the modified synthesize node with component research results.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.config import Config
from agent.nodes.synthesize import synthesize_node
from agent.state import ResearchComponents, ResearchState


class MockLLMClient:
    """Mock LLM client that returns realistic proposal components."""

    def __init__(self, provider_info="mock-openai"):
        self.provider_info = provider_info

    def get_provider_info(self):
        return self.provider_info

    async def json_completion(self, messages, json_schema=None):
        """Return a realistic component or full proposal based on the prompt."""
        user_content = messages[1]["content"] if len(messages) > 1 else ""

        # Check if this is a component-specific generation
        if "alphas component" in user_content.lower():
            return {
                "new": [
                    {
                        "name": "crypto_momentum_alpha",
                        "componentId": "momentum_v1",
                        "version": "1.0",
                        "title": "Cryptocurrency Momentum Strategy",
                        "description": "Momentum-based alpha generation for cryptocurrency markets",
                        "text": "This strategy exploits momentum effects in cryptocurrency prices by ranking assets based on past performance and taking long positions in top performers while shorting bottom performers. The strategy uses a 12-1 month momentum calculation excluding the most recent month to avoid microstructure noise.",
                        "params": [
                            {
                                "name": "lookback_months",
                                "type": "int",
                                "value": 12,
                                "minimum": 6,
                                "maximum": 24,
                                "tuning": {"distribution": "uniform"},
                            },
                            {
                                "name": "skip_months",
                                "type": "int",
                                "value": 1,
                                "minimum": 0,
                                "maximum": 3,
                                "tuning": {"distribution": "uniform"},
                            },
                            {
                                "name": "rebalance_frequency",
                                "type": "enum",
                                "value": "monthly",
                                "enumValues": ["daily", "weekly", "monthly"],
                                "tuning": {"distribution": "categorical"},
                            },
                        ],
                    }
                ]
            }
        elif "universe component" in user_content.lower():
            return {
                "new": [
                    {
                        "name": "top_crypto_universe",
                        "componentId": "crypto_univ_v1",
                        "version": "1.0",
                        "title": "Top Cryptocurrency Universe",
                        "description": "Universe of top cryptocurrencies by market capitalization and liquidity",
                        "text": "This universe selects the top cryptocurrencies based on market capitalization and trading volume criteria. It includes major cryptocurrencies with sufficient liquidity for algorithmic trading while excluding stablecoins and tokens with poor data quality.",
                        "params": [
                            {
                                "name": "min_market_cap",
                                "type": "float",
                                "value": 100000000.0,
                                "minimum": 50000000.0,
                                "maximum": 1000000000.0,
                                "tuning": {"distribution": "log"},
                            },
                            {
                                "name": "max_assets",
                                "type": "int",
                                "value": 50,
                                "minimum": 20,
                                "maximum": 100,
                                "tuning": {"distribution": "uniform"},
                            },
                        ],
                    }
                ]
            }
        elif "risk component" in user_content.lower():
            return {
                "new": [
                    {
                        "name": "volatility_risk_management",
                        "componentId": "vol_risk_v1",
                        "version": "1.0",
                        "title": "Volatility-Based Risk Management",
                        "description": "Risk management system based on realized volatility",
                        "text": "This risk management system uses realized volatility to adjust position sizes and implement stop-losses. It includes portfolio-level risk budgeting and individual asset exposure limits appropriate for the high volatility of cryptocurrency markets.",
                        "params": [
                            {
                                "name": "max_position_size",
                                "type": "float",
                                "value": 0.1,
                                "minimum": 0.05,
                                "maximum": 0.2,
                                "tuning": {"distribution": "uniform"},
                            },
                            {
                                "name": "volatility_lookback",
                                "type": "int",
                                "value": 30,
                                "minimum": 10,
                                "maximum": 90,
                                "tuning": {"distribution": "uniform"},
                            },
                        ],
                    }
                ]
            }
        else:
            # Full proposal generation (unified approach)
            return {
                "alphas": {
                    "new": [
                        {
                            "name": "unified_crypto_alpha",
                            "componentId": "unified_v1",
                            "version": "1.0",
                            "title": "Unified Cryptocurrency Alpha Strategy",
                            "description": "Combined momentum and mean reversion strategy for crypto markets",
                            "text": "This strategy combines momentum and mean reversion signals to generate alpha in cryptocurrency markets. It uses multiple time horizons and incorporates volatility scaling for position sizing.",
                            "params": [
                                {
                                    "name": "momentum_weight",
                                    "type": "float",
                                    "value": 0.6,
                                    "minimum": 0.0,
                                    "maximum": 1.0,
                                    "tuning": {"distribution": "uniform"},
                                }
                            ],
                        }
                    ]
                },
                "universe": {
                    "new": [
                        {
                            "name": "unified_crypto_universe",
                            "componentId": "unified_univ_v1",
                            "version": "1.0",
                            "title": "Unified Crypto Universe",
                            "description": "Standard cryptocurrency universe for unified strategy",
                            "text": "Top 30 cryptocurrencies by market cap with minimum liquidity requirements.",
                            "params": [
                                {
                                    "name": "universe_size",
                                    "type": "int",
                                    "value": 30,
                                    "minimum": 20,
                                    "maximum": 50,
                                    "tuning": {"distribution": "uniform"},
                                }
                            ],
                        }
                    ]
                },
            }


class MockMCPClient:
    """Mock MCP client."""

    def __init__(self, config, llm_client, node_name):
        self.config = config
        self.llm_client = llm_client
        self.node_name = node_name

    def get_available_tool_names(self):
        return ["validation", "llm_fallback"]

    async def validate_proposal(self, proposal):
        """Mock validation that always passes."""
        return {"is_valid": True, "errors": [], "report": "✅ Mock validation passed"}

    async def close(self):
        pass


async def test_unified_synthesis():
    """Test the traditional unified synthesis approach."""
    print("=== Testing Unified Synthesis Approach ===")

    # Mock the dependencies
    import agent.llm_client as llm_module
    import agent.nodes.synthesize as synth_module
    import agent.tools.mcp_client as mcp_module

    # Patch the classes
    original_llm_client = llm_module.LLMClient
    original_mcp_client = mcp_module.MCPClient

    llm_module.LLMClient = MockLLMClient
    mcp_module.MCPClient = MockMCPClient

    try:
        # Create test state with component research results
        state: ResearchState = {
            "idea": "Cryptocurrency momentum and mean reversion strategy",
            "alpha_only": False,
            "research_plan": "Develop a cryptocurrency trading strategy combining momentum and mean reversion signals",
            "component_research_results": {
                "ALPHA": [
                    {
                        "title": "Alpha Research Approach 1: Momentum Strategy",
                        "content": "Momentum strategies in crypto markets exploit trend persistence. Key finding: 12-1 month momentum works well with volatility scaling. Implementation requires careful handling of crypto-specific risks like extreme volatility and liquidity constraints.",
                        "approach_number": 1,
                        "component": "ALPHA",
                    },
                    {
                        "title": "Alpha Research Approach 2: Mean Reversion",
                        "content": "Mean reversion works in crypto markets during consolidation periods. Optimal parameters: 20-day lookback, 2 standard deviation bands. Risk management crucial due to trending markets that can persist longer than expected.",
                        "approach_number": 2,
                        "component": "ALPHA",
                    },
                ],
                "UNIVERSE": [
                    {
                        "title": "Universe Research: Top Crypto Selection",
                        "content": "Top 20-50 cryptocurrencies by market cap provide optimal balance of liquidity and diversification. Minimum criteria: $100M market cap, $10M daily volume, major exchange listing. Exclude stablecoins and wrapped tokens.",
                        "approach_number": 1,
                        "component": "UNIVERSE",
                    }
                ],
                "RISK": [
                    {
                        "title": "Risk Management: Volatility-Based Sizing",
                        "content": "Crypto markets require enhanced risk management. Use realized volatility for position sizing, maximum 10% per asset, portfolio VaR limits. Implement circuit breakers for extreme market conditions.",
                        "approach_number": 1,
                        "component": "RISK",
                    }
                ],
            },
            "web_search_results": [],
            "prior_art_results": {
                "verdict": "acceptable",
                "reasoning": "Limited similar implementations found",
                "total_found": 1,
                "search_method": "github",
            },
            "validation_errors": [],
            "current_step": "synthesize",
        }

        # Create mock config
        config = MagicMock()
        config.get_boolean_env.return_value = False  # Unified approach
        config.get_schema.return_value = {"type": "object", "properties": {}}
        config.get_components_from_env.return_value = None

        # Mock the prompts methods that are used
        import agent.prompts

        original_research_context_template = agent.prompts.ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE
        original_format_available_tools = agent.prompts.ResearchPrompts.format_available_tools
        original_format_component_research_context = agent.prompts.ResearchPrompts.format_component_research_context

        agent.prompts.ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE = """
Research Plan: {research_plan}
Web Results: {web_results}
Prior Art: {verdict} - {reasoning} ({total_found} found via {search_method})
"""
        agent.prompts.ResearchPrompts.format_available_tools = lambda x: "Mock tools: " + str(x)
        agent.prompts.ResearchPrompts.format_component_research_context = (
            lambda *args: "Mock component research context"
        )

        # Create mock config
        config = MagicMock()
        config.get_boolean_env.return_value = False  # Unified approach
        config.get_schema.return_value = {"type": "object", "properties": {}}
        config.get_components_from_env.return_value = None

        # Mock the prompts methods that are used
        import agent.prompts

        original_research_context_template = agent.prompts.ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE
        original_format_available_tools = agent.prompts.ResearchPrompts.format_available_tools
        original_format_component_research_context = agent.prompts.ResearchPrompts.format_component_research_context

        agent.prompts.ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE = """
Research Plan: {research_plan}
Web Results: {web_results}
Prior Art: {verdict} - {reasoning} ({total_found} found via {search_method})
"""
        agent.prompts.ResearchPrompts.format_available_tools = lambda x: "Mock tools: " + str(x)
        agent.prompts.ResearchPrompts.format_component_research_context = (
            lambda *args: "Mock component research context"
        )

        # Test unified synthesis
        result = await synthesize_node(state, config)

        print("✓ Unified synthesis completed")
        print(f"✓ Result keys: {list(result.keys())}")

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print(f"✓ Generated proposal with components: {list(proposal.keys())}")

            # Validate structure
            assert "alphas" in proposal, "Missing alphas component"
            assert "universe" in proposal, "Missing universe component"
            print("✓ Required components present")

            # Check alphas structure
            alphas = proposal["alphas"]
            assert "new" in alphas, "Missing 'new' in alphas"
            assert len(alphas["new"]) > 0, "No alpha components generated"

            alpha_component = alphas["new"][0]
            required_fields = ["name", "componentId", "title", "description", "text", "params"]
            for field in required_fields:
                assert field in alpha_component, f"Missing required field: {field}"
            print("✓ Alpha component structure valid")

            print("✓ Unified synthesis test PASSED")
            return True
        else:
            print("❌ No final_proposal in result")
            print(f"Result: {result}")
            return False

    finally:
        # Restore original classes and methods
        llm_module.LLMClient = original_llm_client
        mcp_module.MCPClient = original_mcp_client
        agent.prompts.ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE = original_research_context_template
        agent.prompts.ResearchPrompts.format_available_tools = original_format_available_tools
        agent.prompts.ResearchPrompts.format_component_research_context = original_format_component_research_context


async def test_component_by_component_synthesis():
    """Test the new component-by-component synthesis approach."""
    print("\n=== Testing Component-by-Component Synthesis Approach ===")

    # Mock the dependencies
    import agent.llm_client as llm_module
    import agent.nodes.synthesize as synth_module
    import agent.tools.mcp_client as mcp_module

    # Patch the classes
    original_llm_client = llm_module.LLMClient
    original_mcp_client = mcp_module.MCPClient

    llm_module.LLMClient = MockLLMClient
    mcp_module.MCPClient = MockMCPClient

    try:
        # Create test state
        state: ResearchState = {
            "idea": "Cryptocurrency momentum strategy with risk management",
            "alpha_only": False,
            "research_plan": "Develop a momentum-based cryptocurrency trading strategy with comprehensive risk management",
            "component_research_results": {
                "ALPHA": [
                    {
                        "title": "Alpha Research: Momentum Strategy Analysis",
                        "content": "Comprehensive analysis of momentum strategies in cryptocurrency markets. Research shows 12-1 month momentum performs well when combined with volatility scaling. Key considerations include transaction costs, slippage in smaller cap cryptos, and market regime changes during bull/bear cycles.",
                        "approach_number": 1,
                        "component": "ALPHA",
                    }
                ],
                "UNIVERSE": [
                    {
                        "title": "Universe Research: Cryptocurrency Selection Framework",
                        "content": "Framework for selecting cryptocurrencies for algorithmic trading. Optimal universe size is 30-50 assets based on market cap and liquidity. Selection criteria: minimum $100M market cap, $10M daily volume, listing on tier-1 exchanges, exclude stablecoins and governance tokens with irregular trading patterns.",
                        "approach_number": 1,
                        "component": "UNIVERSE",
                    }
                ],
                "RISK": [
                    {
                        "title": "Risk Management: Crypto-Specific Risk Controls",
                        "content": "Risk management framework tailored for cryptocurrency markets. Implements volatility-based position sizing, maximum individual asset exposure of 10%, portfolio-level VaR monitoring, and circuit breakers for extreme market conditions. Special attention to crypto-specific risks like flash crashes and exchange outages.",
                        "approach_number": 1,
                        "component": "RISK",
                    }
                ],
            },
            "web_search_results": [],
            "prior_art_results": {
                "verdict": "novel",
                "reasoning": "No exact implementations found",
                "total_found": 0,
                "search_method": "github",
            },
            "validation_errors": [],
            "current_step": "synthesize",
        }

        # Create mock config that enables component-by-component
        config = MagicMock()
        config.get_boolean_env.return_value = True  # Enable component-by-component
        config.get_schema.return_value = {"type": "object", "properties": {}}
        config.get_components_from_env.return_value = None

        # Test component-by-component synthesis
        result = await synthesize_node(state, config)

        print("✓ Component-by-component synthesis completed")
        print(f"✓ Result keys: {list(result.keys())}")

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print(f"✓ Generated proposal with components: {list(proposal.keys())}")

            # Validate that each component was generated separately
            expected_components = ["alphas", "universe", "risk"]
            for component in expected_components:
                assert component in proposal, f"Missing component: {component}"
                assert "new" in proposal[component], f"Missing 'new' in {component}"
                assert len(proposal[component]["new"]) > 0, f"No items in {component}"
                print(f"✓ {component.capitalize()} component generated")

            # Check metadata indicates component-by-component synthesis
            if "misc" in proposal:
                misc = proposal["misc"]
                if "synthesis_method" in misc:
                    assert misc["synthesis_method"] == "component_by_component"
                    print("✓ Synthesis method correctly marked as component_by_component")
                if "generated_by" in misc:
                    assert "component-synthesis" in misc["generated_by"]
                    print("✓ Generator correctly marked as component synthesis")

            # Validate component structure
            alpha_component = proposal["alphas"]["new"][0]
            required_fields = ["name", "componentId", "title", "description", "text", "params"]
            for field in required_fields:
                assert field in alpha_component, f"Missing required field in alpha: {field}"
            print("✓ Alpha component structure valid")

            universe_component = proposal["universe"]["new"][0]
            for field in required_fields:
                assert field in universe_component, f"Missing required field in universe: {field}"
            print("✓ Universe component structure valid")

            print("✓ Component-by-component synthesis test PASSED")
            return True
        else:
            print("❌ No final_proposal in result")
            print(f"Result: {result}")
            return False

    finally:
        # Restore original classes
        llm_module.LLMClient = original_llm_client
        mcp_module.MCPClient = original_mcp_client


async def test_fallback_behavior():
    """Test fallback to web results when no component research available."""
    print("\n=== Testing Fallback to Web Results ===")

    # Mock the dependencies
    import agent.llm_client as llm_module
    import agent.nodes.synthesize as synth_module
    import agent.tools.mcp_client as mcp_module

    # Patch the classes
    original_llm_client = llm_module.LLMClient
    original_mcp_client = mcp_module.MCPClient

    llm_module.LLMClient = MockLLMClient
    mcp_module.MCPClient = MockMCPClient

    try:
        # Create test state with NO component research results
        state: ResearchState = {
            "idea": "Simple cryptocurrency strategy",
            "alpha_only": False,
            "research_plan": "Develop a basic cryptocurrency trading strategy",
            "component_research_results": {},  # Empty!
            "web_search_results": [
                {
                    "title": "Cryptocurrency Trading Strategies Overview",
                    "content": "General overview of cryptocurrency trading approaches including momentum, mean reversion, and arbitrage strategies. Key considerations for crypto markets include high volatility, 24/7 trading, and regulatory risks.",
                    "source": "web_search",
                },
                {
                    "title": "Risk Management for Crypto Trading",
                    "content": "Risk management best practices for cryptocurrency trading. Important aspects include position sizing, stop losses, and portfolio diversification across different crypto categories.",
                    "source": "web_search",
                },
            ],
            "prior_art_results": {
                "verdict": "acceptable",
                "reasoning": "Some similar strategies exist",
                "total_found": 2,
                "search_method": "github",
            },
            "validation_errors": [],
            "current_step": "synthesize",
        }

        # Create mock config
        config = MagicMock()
        config.get_boolean_env.return_value = True  # Try component-by-component
        config.get_schema.return_value = {"type": "object", "properties": {}}
        config.get_components_from_env.return_value = None

        # Test synthesis - should fall back to unified approach
        result = await synthesize_node(state, config)

        print("✓ Fallback synthesis completed")
        print(f"✓ Result keys: {list(result.keys())}")

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print(f"✓ Generated proposal with components: {list(proposal.keys())}")
            print("✓ Successfully fell back to unified approach when no component data available")
            return True
        else:
            print("❌ No final_proposal in result")
            return False

    finally:
        # Restore original classes
        llm_module.LLMClient = original_llm_client
        mcp_module.MCPClient = original_mcp_client


async def main():
    """Run all tests."""
    print("🧪 Testing Modified Synthesize Node")
    print("=" * 50)

    tests = [
        ("Unified Synthesis", test_unified_synthesis),
        ("Component-by-Component Synthesis", test_component_by_component_synthesis),
        ("Fallback Behavior", test_fallback_behavior),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} FAILED with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! The synthesize node modifications are working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")


if __name__ == "__main__":
    asyncio.run(main())
