#!/usr/bin/env python3
"""
Detailed proposal inspection to verify quality of generated proposals.
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agent.config import Config
from agent.nodes.synthesize import synthesize_node


async def inspect_component_proposal():
    """Generate and inspect a component-by-component proposal in detail."""
    print("=== DETAILED COMPONENT-BY-COMPONENT PROPOSAL INSPECTION ===\n")

    # Enable component-by-component synthesis
    os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

    config = Config()

    state = {
        "idea": "Multi-factor cryptocurrency strategy combining momentum and mean reversion",
        "alpha_only": False,
        "research_plan": "Combine momentum and mean reversion factors for enhanced crypto returns",
        "component_research_results": {
            "ALPHA": [
                {
                    "title": "Momentum Factor Implementation",
                    "content": "12-1 month momentum strategy: Calculate returns over 12 months excluding the most recent month to avoid microstructure noise. Rank cryptocurrencies by momentum score and select top decile. Use exponential moving averages (12, 26, 50) for trend confirmation. Incorporate volume-weighted momentum to account for liquidity. Rebalance monthly with minimum holding period of 2 weeks to reduce turnover.",
                    "approach_number": 1,
                    "component": "ALPHA",
                },
                {
                    "title": "Mean Reversion Component",
                    "content": "Mean reversion alpha using Bollinger Bands and RSI. When price touches lower Bollinger Band (2 std dev) AND RSI < 30, generate buy signal. Sell when price reaches upper band OR RSI > 70. Use 20-day moving average as baseline. For crypto markets, use shorter windows (10-15 days) due to high volatility. Combine with volume analysis to avoid low-liquidity traps.",
                    "approach_number": 2,
                    "component": "ALPHA",
                },
            ],
            "UNIVERSE": [
                {
                    "title": "Tiered Cryptocurrency Universe",
                    "content": "Three-tier universe structure: Tier 1 (BTC, ETH) - 40% allocation, large cap stable coins. Tier 2 (Top 10 altcoins) - 45% allocation, includes BNB, XRP, ADA, SOL, DOGE. Tier 3 (Mid-cap growth) - 15% allocation, market cap $1B-10B with high growth potential. Minimum criteria: daily volume >$50M, available on 3+ major exchanges, minimum 12 months trading history. Rebalance tiers quarterly based on market cap changes.",
                    "approach_number": 1,
                    "component": "UNIVERSE",
                }
            ],
            "PORTFOLIO": [
                {
                    "title": "Risk Parity with Momentum Overlay",
                    "content": "Portfolio construction using risk parity principles with momentum overlay. Base allocation: equal risk contribution from each asset based on 30-day volatility. Momentum overlay: increase allocation to assets with positive momentum scores by up to 50%. Maximum single asset weight: 15%. Minimum weight: 2%. Use mean reversion signals for tactical tilts. Rebalance weekly with 2% threshold for weight changes to control turnover.",
                    "approach_number": 1,
                    "component": "PORTFOLIO",
                }
            ],
            "EXECUTION": [
                {
                    "title": "Smart Order Execution System",
                    "content": "TWAP (Time-Weighted Average Price) execution over 4-hour windows to minimize market impact. Split large orders into smaller chunks (max 5% of average daily volume). Use limit orders with aggressive pricing during low volatility periods, market orders during high volatility. Implement dark pool connectivity for large trades. Real-time slippage monitoring with automatic order size adjustment when slippage exceeds 0.5%.",
                    "approach_number": 1,
                    "component": "EXECUTION",
                }
            ],
            "RISK": [
                {
                    "title": "Multi-Layer Risk Management",
                    "content": "Portfolio-level VaR limit of 3% daily (95% confidence). Individual position stop-loss at 20%. Sector concentration limit: max 60% in any single crypto category. Leverage limit: 1.5x gross exposure. Dynamic position sizing based on realized volatility with lookback period of 20 days. Correlation-adjusted risk budgeting during stress periods. Real-time monitoring with automatic position reduction when limits are breached.",
                    "approach_number": 1,
                    "component": "RISK",
                }
            ],
        },
        "prior_art_results": {
            "verdict": "novel",
            "reasoning": "Unique combination of momentum and mean reversion with risk parity",
            "total_found": 0,
            "search_method": "github_search",
        },
        "current_step": "synthesize",
    }

    try:
        result = await synthesize_node(state, config)

        if "final_proposal" in result:
            proposal = result["final_proposal"]

            print("📋 GENERATED PROPOSAL STRUCTURE:")
            print("=" * 50)

            # Save to file for inspection
            with open("detailed_proposal_output.json", "w") as f:
                json.dump(proposal, f, indent=2)

            print(f"Components generated: {list(proposal.keys())}")
            print(f"Generated using: {proposal.get('misc', {}).get('generated_by', 'Unknown')}")
            print(f"Synthesis method: {proposal.get('misc', {}).get('synthesis_method', 'unified')}")

            # Inspect each component in detail
            for comp_key in ["alphas", "universe", "portfolio", "execution", "risk"]:
                if comp_key in proposal:
                    print(f"\n🔍 {comp_key.upper()} COMPONENT:")
                    print("-" * 30)

                    comp_data = proposal[comp_key]
                    items = comp_data.get("new", [])

                    for i, item in enumerate(items, 1):
                        print(f"  Item {i}:")
                        print(f"    Name: {item.get('name', 'N/A')}")
                        print(f"    Title: {item.get('title', 'N/A')}")
                        print(f"    Description: {item.get('description', 'N/A')[:100]}...")

                        # Show parameters
                        params = item.get("params", [])
                        print(f"    Parameters ({len(params)}):")
                        for param in params[:3]:  # Show first 3 params
                            name = param.get("name", "unknown")
                            ptype = param.get("type", "unknown")
                            value = param.get("value", "N/A")
                            print(f"      - {name} ({ptype}): {value}")

                        if len(params) > 3:
                            print(f"      ... and {len(params) - 3} more parameters")
                        print()

            print("\n✅ Detailed proposal saved to: detailed_proposal_output.json")
            print("\n🎯 QUALITY ASSESSMENT:")
            print("=" * 30)

            # Check for key quality indicators
            quality_checks = []

            # Check if all expected components are present
            expected_components = ["alphas", "universe", "portfolio", "execution", "risk"]
            present_components = [comp for comp in expected_components if comp in proposal]
            quality_checks.append(f"Components present: {len(present_components)}/{len(expected_components)}")

            # Check parameter quality
            total_params = 0
            for comp in expected_components:
                if comp in proposal:
                    for item in proposal[comp].get("new", []):
                        total_params += len(item.get("params", []))
            quality_checks.append(f"Total parameters defined: {total_params}")

            # Check text content
            has_meaningful_text = True
            for comp in present_components:
                for item in proposal[comp].get("new", []):
                    text = item.get("text", "")
                    if len(text) < 50:  # Too short
                        has_meaningful_text = False
                        break
            quality_checks.append(f"Meaningful text content: {'✅' if has_meaningful_text else '❌'}")

            # Check schema compliance
            validation_report = result.get("validation_report", "")
            schema_valid = "successfully validated" in validation_report.lower()
            quality_checks.append(f"Schema validation: {'✅' if schema_valid else '❌'}")

            for check in quality_checks:
                print(f"  {check}")

            return True

        else:
            print("❌ No proposal generated")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if "SYNTHESIZE_COMPONENT_BY_COMPONENT" in os.environ:
            del os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"]


if __name__ == "__main__":
    asyncio.run(inspect_component_proposal())
