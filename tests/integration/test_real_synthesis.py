#!/usr/bin/env python3
"""
Real synthesis test using actual OpenAI API calls to validate our component-based changes.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.config import Config
from agent.nodes.synthesize import synthesize_node
from agent.state import ResearchState


async def test_traditional_synthesis():
    """Test traditional synthesis approach with component research results."""
    print("=== TESTING TRADITIONAL SYNTHESIS WITH COMPONENT RESEARCH ===\n")

    # Create config with real OpenAI settings
    config = Config()

    # Create state with component research results (simulating web_research node output)
    state: ResearchState = {
        "idea": "Cryptocurrency momentum trading strategy using technical indicators",
        "alpha_only": False,
        "research_plan": "Develop a momentum-based trading strategy for cryptocurrencies using RSI and moving averages",
        "component_research_results": {
            "ALPHA": [
                {
                    "title": "Alpha Research Approach 1: RSI Momentum Strategy",
                    "content": "RSI (Relative Strength Index) momentum strategies work by identifying overbought and oversold conditions in cryptocurrency markets. When RSI drops below 30, it indicates oversold conditions and potential buying opportunities. When RSI rises above 70, it indicates overbought conditions and potential selling opportunities. For crypto markets, shorter RSI periods (6-14 days) work better due to high volatility. Combine with 20-day and 50-day moving averages for trend confirmation. Entry signals occur when RSI crosses threshold AND price is above/below moving average. Risk management through position sizing based on volatility is crucial.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "ALPHA",
                    "approach_number": 1,
                },
                {
                    "title": "Alpha Research Approach 2: Moving Average Crossover",
                    "content": "Moving average crossover strategies generate signals when shorter-term MA crosses above or below longer-term MA. For cryptocurrencies, exponential moving averages (EMA) are preferred over simple moving averages due to higher responsiveness to recent price changes. Common combinations include 12/26 EMA, 20/50 EMA, or 8/21 EMA for faster signals. Golden cross (short MA above long MA) indicates bullish momentum, while death cross indicates bearish momentum. Add volume confirmation and momentum filters to reduce false signals in sideways markets.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "ALPHA",
                    "approach_number": 2,
                },
            ],
            "UNIVERSE": [
                {
                    "title": "Universe Research: Top Cryptocurrency Selection",
                    "content": "For momentum trading, focus on top 20-30 cryptocurrencies by market capitalization to ensure adequate liquidity and reduced slippage. Include Bitcoin (BTC), Ethereum (ETH), and major altcoins like BNB, XRP, ADA, SOL, DOGE. Minimum criteria: market cap > $1B, daily volume > $100M, available on major exchanges (Binance, Coinbase, Kraken). Exclude stablecoins (USDT, USDC, BUSD) as they don't exhibit momentum patterns. Rebalance universe quarterly to account for new listings and delistings. Consider correlation analysis to avoid over-concentration in similar assets.",
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
                    "content": "Cryptocurrency markets require sophisticated risk management due to extreme volatility. Implement position sizing based on realized volatility using 20-day rolling standard deviation. Maximum position size should be inversely proportional to volatility: Position_Size = Target_Risk / (Volatility * Price). Set maximum individual position at 10% of portfolio and maximum sector exposure at 40%. Use stop-losses at 15-20% for individual positions. Implement portfolio-level daily VaR limits and rebalance when exposure exceeds thresholds. Consider correlation-adjusted risk to account for crypto market's high correlation during stress periods.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "RISK",
                    "approach_number": 1,
                }
            ],
        },
        "web_search_results": [
            {
                "title": "Fallback: General Crypto Trading Info",
                "content": "General information about cryptocurrency trading...",
                "url": "web_search",
                "source": "web",
            }
        ],
        "prior_art_results": {
            "verdict": "novel",
            "reasoning": "No similar RSI momentum strategies found in prior art search",
            "total_found": 1,
            "search_method": "github_search",
        },
        "current_step": "synthesize",
    }

    print("Input state:")
    print(f"  Idea: {state['idea']}")
    print(f"  Component research results: {list(state['component_research_results'].keys())}")
    print(f"  Alpha approaches: {len(state['component_research_results']['ALPHA'])}")
    print(f"  Universe approaches: {len(state['component_research_results']['UNIVERSE'])}")
    print(f"  Risk approaches: {len(state['component_research_results']['RISK'])}")

    try:
        result = await synthesize_node(state, config)

        print("\n" + "=" * 60)
        print("SYNTHESIS RESULT:")
        print("=" * 60)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print("✅ Proposal generated successfully!")
            print(f"📊 Components in proposal: {list(proposal.keys())}")

            # Check specific components
            if "alphas" in proposal:
                alphas = proposal["alphas"]
                print(f"🎯 Alpha components: {len(alphas.get('new', []))} items")
                if alphas.get("new"):
                    alpha_item = alphas["new"][0]
                    print(f"   - Name: {alpha_item.get('name', 'N/A')}")
                    print(f"   - Title: {alpha_item.get('title', 'N/A')}")
                    print(f"   - Params: {len(alpha_item.get('params', []))} parameters")

            if "universe" in proposal:
                universe = proposal["universe"]
                print(f"🌍 Universe components: {len(universe.get('new', []))} items")
                if universe.get("new"):
                    universe_item = universe["new"][0]
                    print(f"   - Name: {universe_item.get('name', 'N/A')}")
                    print(f"   - Title: {universe_item.get('title', 'N/A')}")

            if "risk" in proposal:
                risk = proposal["risk"]
                print(f"⚠️  Risk components: {len(risk.get('new', []))} items")
                if risk.get("new"):
                    risk_item = risk["new"][0]
                    print(f"   - Name: {risk_item.get('name', 'N/A')}")
                    print(f"   - Title: {risk_item.get('title', 'N/A')}")

            # Check metadata
            if "misc" in proposal:
                misc = proposal["misc"]
                print("📋 Metadata:")
                print(f"   - Generated by: {misc.get('generated_by', 'N/A')}")
                print(f"   - Research sources: {misc.get('research_sources', 'N/A')}")
                print(f"   - Tool protocol: {misc.get('tool_protocol', 'N/A')}")

            # Validation info
            if "validation_report" in result:
                print(f"✅ Validation: {result['validation_report'][:100]}...")

            return True

        else:
            print("❌ No final proposal generated")
            print(f"Result keys: {list(result.keys())}")
            return False

    except Exception as e:
        print(f"❌ Exception during synthesis: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_component_by_component_synthesis():
    """Test component-by-component synthesis approach."""
    print("\n\n=== TESTING COMPONENT-BY-COMPONENT SYNTHESIS ===\n")

    # Set environment variable for component-by-component synthesis
    os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

    # Create config
    config = Config()

    # Same state as before but ensure it's not alpha_only
    state: ResearchState = {
        "idea": "Cryptocurrency arbitrage strategy across exchanges",
        "alpha_only": False,
        "research_plan": "Develop arbitrage opportunities detection and execution system for crypto exchanges",
        "component_research_results": {
            "ALPHA": [
                {
                    "title": "Alpha Research: Exchange Price Differences",
                    "content": "Cryptocurrency arbitrage exploits price differences across exchanges. Price discrepancies of 0.5-3% are common between major exchanges like Binance, Coinbase, and Kraken. Factors causing differences include: trading volume variations, regional demand, withdrawal/deposit fees, and settlement times. Automated detection systems should monitor price feeds from multiple exchanges in real-time. Consider transaction costs, slippage, and execution delays when calculating profitability thresholds.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "ALPHA",
                    "approach_number": 1,
                }
            ],
            "UNIVERSE": [
                {
                    "title": "Universe Research: High-Volume Crypto Pairs",
                    "content": "Focus on major cryptocurrency pairs with high liquidity: BTC/USD, ETH/USD, BNB/USD, ADA/USD. These pairs have sufficient volume for arbitrage without significant market impact. Minimum daily volume threshold of $500M per pair across all exchanges. Monitor at least 5-8 major exchanges for each pair to identify opportunities. Include stablecoin pairs (BTC/USDT, ETH/USDC) for faster settlement and reduced currency risk.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "UNIVERSE",
                    "approach_number": 1,
                }
            ],
            "EXECUTION": [
                {
                    "title": "Execution Research: High-Frequency Trading Infrastructure",
                    "content": "Arbitrage requires ultra-low latency execution infrastructure. Co-locate servers near exchange data centers to minimize network delays. Use WebSocket connections for real-time price feeds and order placement. Implement smart order routing to automatically execute trades when profit thresholds are met. Pre-position capital on multiple exchanges to eliminate transfer delays. Use API rate limiting strategies and failover mechanisms for reliability.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "EXECUTION",
                    "approach_number": 1,
                }
            ],
        },
        "prior_art_results": {
            "verdict": "novel",
            "reasoning": "Unique approach to multi-exchange arbitrage",
            "total_found": 0,
            "search_method": "github_search",
        },
        "current_step": "synthesize",
    }

    print("Input state for component-by-component synthesis:")
    print(f"  Idea: {state['idea']}")
    print(f"  Alpha only: {state['alpha_only']}")
    print(f"  Components: {list(state['component_research_results'].keys())}")
    print(f"  Environment: SYNTHESIZE_COMPONENT_BY_COMPONENT={os.environ.get('SYNTHESIZE_COMPONENT_BY_COMPONENT')}")

    try:
        result = await synthesize_node(state, config)

        print("\n" + "=" * 60)
        print("COMPONENT-BY-COMPONENT RESULT:")
        print("=" * 60)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print("✅ Component-by-component proposal generated!")

            # Check if it was actually generated component-by-component
            if "misc" in proposal and proposal["misc"].get("synthesis_method") == "component_by_component":
                print("🎯 Confirmed: Used component-by-component synthesis!")
                print(f"   Generated by: {proposal['misc'].get('generated_by')}")
            else:
                print("⚠️  Note: Used unified synthesis (fallback)")

            print(f"📊 Components generated: {list(proposal.keys())}")

            # Show details of each component
            for comp_key in ["alphas", "universe", "execution", "portfolio", "risk"]:
                if comp_key in proposal:
                    comp_data = proposal[comp_key]
                    items = comp_data.get("new", [])
                    print(f"   {comp_key}: {len(items)} items")
                    if items:
                        item = items[0]
                        print(f"     - {item.get('name', 'N/A')}: {item.get('title', 'N/A')}")

            return True
        else:
            print("❌ No final proposal in result")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up environment
        if "SYNTHESIZE_COMPONENT_BY_COMPONENT" in os.environ:
            del os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"]


async def test_alpha_only_mode():
    """Test alpha-only mode to ensure it still works with our changes."""
    print("\n\n=== TESTING ALPHA-ONLY MODE ===\n")

    config = Config()

    state: ResearchState = {
        "idea": "Simple momentum alpha for crypto",
        "alpha_only": True,
        "research_plan": "Create a simple momentum-based alpha factor",
        "component_research_results": {
            "ALPHA": [
                {
                    "title": "Simple Momentum Alpha",
                    "content": "12-1 month momentum factor for cryptocurrencies. Calculate 12-month return excluding last month to avoid short-term reversal effects. Rank cryptocurrencies by momentum score and select top quintile. Rebalance monthly.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "ALPHA",
                    "approach_number": 1,
                }
            ],
            "UNIVERSE": [
                {
                    "title": "Crypto Universe for Alpha",
                    "content": "Top 50 cryptocurrencies by market cap for momentum alpha testing.",
                    "url": "llm_component_research",
                    "source": "llm_with_web_tools",
                    "research_type": "component_specific",
                    "component": "UNIVERSE",
                    "approach_number": 1,
                }
            ],
        },
        "prior_art_results": {
            "verdict": "novel",
            "reasoning": "Simple momentum approach",
            "total_found": 0,
            "search_method": "github_search",
        },
        "current_step": "synthesize",
    }

    print("Input state for alpha-only mode:")
    print(f"  Idea: {state['idea']}")
    print(f"  Alpha only: {state['alpha_only']}")
    print(f"  Has component research: {bool(state['component_research_results'])}")

    try:
        result = await synthesize_node(state, config)

        print("\n" + "=" * 50)
        print("ALPHA-ONLY RESULT:")
        print("=" * 50)

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print("✅ Alpha-only proposal generated!")

            # Check alpha-only constraints
            if proposal.get("alpha-only"):
                print("🎯 Confirmed: alpha-only flag set")

            # Should only have alphas, universe, and alpha-only fields
            expected_fields = {"alphas", "universe", "alpha-only"}
            actual_fields = set(proposal.keys())

            if actual_fields.issubset(expected_fields | {"misc"}):  # Allow misc field
                print("✅ Field constraints satisfied")
                print(f"   Fields present: {list(actual_fields)}")
            else:
                print(f"⚠️  Unexpected fields: {actual_fields - expected_fields}")

            # Check content
            if "alphas" in proposal:
                alphas = proposal["alphas"].get("new", [])
                print(f"🎯 Alpha items: {len(alphas)}")
                if alphas:
                    print(f"   - {alphas[0].get('name', 'N/A')}")

            if "universe" in proposal:
                universe = proposal["universe"].get("new", [])
                print(f"🌍 Universe items: {len(universe)}")
                if universe:
                    print(f"   - {universe[0].get('name', 'N/A')}")

            return True
        else:
            print("❌ No final proposal generated")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all synthesis tests."""
    print("🚀 TESTING SYNTHESIZE NODE WITH REAL LLM CALLS")
    print("=" * 70)

    # Check API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        return

    api_key = os.environ["OPENAI_API_KEY"]
    print(f"✅ Using OpenAI API key: {api_key[:8]}...{api_key[-4:]}")
    print()

    results = []

    # Test 1: Traditional synthesis with component research
    results.append(await test_traditional_synthesis())

    # Test 2: Component-by-component synthesis
    results.append(await test_component_by_component_synthesis())

    # Test 3: Alpha-only mode
    results.append(await test_alpha_only_mode())

    # Summary
    print("\n\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    test_names = [
        "Traditional synthesis with component research",
        "Component-by-component synthesis",
        "Alpha-only mode compatibility",
    ]

    for i, (test_name, success) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{i+1}. {test_name}: {status}")

    total_passed = sum(results)
    print(f"\nOverall: {total_passed}/{len(results)} tests passed")

    if total_passed == len(results):
        print("\n🎉 All tests passed! The synthesize node changes are working correctly.")
    else:
        print(f"\n⚠️  {len(results) - total_passed} test(s) failed. Please review the output above.")


if __name__ == "__main__":
    asyncio.run(main())
