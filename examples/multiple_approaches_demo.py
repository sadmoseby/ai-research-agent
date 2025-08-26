#!/usr/bin/env python3
"""
Example demonstrating the multiple research approaches functionality.

This example shows how the web research component can generate and parse
multiple approaches per component, allowing for more comprehensive research
coverage.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import Config
from agent.nodes.web_research import _parse_multiple_approaches


def demo_parsing():
    """Demonstrate the multiple approach parsing functionality."""
    print("🔍 Web Research Multiple Approaches Demo")
    print("=" * 50)
    print("This demo shows how LLM responses with multiple approaches")
    print("are parsed into structured component research results.\n")

    # Example LLM response with multiple approaches
    sample_response = """
Approach 1: Factor-Based Alpha Generation
This approach focuses on identifying and combining traditional risk factors such as value, momentum,
quality, and low volatility. The methodology involves:
- Factor exposure analysis using Barra risk models
- Multi-factor regression for alpha decomposition
- Dynamic factor timing based on market regimes

Approach 2: Machine Learning Signal Ensemble
This approach leverages ensemble machine learning techniques to generate alpha signals:
- Feature engineering from fundamental and technical data
- Random Forest and XGBoost models for prediction
- Cross-validation and walk-forward optimization

Approach 3: Alternative Data Integration
This approach incorporates alternative data sources for unique alpha generation:
- Satellite imagery for retail foot traffic analysis
- Social media sentiment analysis
- Patent filings and R&D expenditure tracking
- Supply chain disruption indicators

Approach 4: Market Microstructure Exploitation
This approach focuses on short-term price inefficiencies:
- Order flow imbalance analysis
- High-frequency momentum reversals
- Liquidity provision in stressed markets
- Cross-asset arbitrage opportunities

Approach 5: Regime-Aware Strategy Switching
This approach adapts strategy based on market conditions:
- Volatility regime detection using hidden Markov models
- Strategy allocation based on regime probabilities
- Dynamic risk budgeting across regimes
"""

    # Parse the response
    approaches = _parse_multiple_approaches(sample_response, "ALPHA", "Multi-Factor Strategy")

    print(f"Parsed {len(approaches)} distinct approaches:\n")

    for i, approach in enumerate(approaches, 1):
        print(f"Approach {i}:")
        print(f"  Title: {approach['title']}")
        print(f"  Component: {approach['component']}")
        print(f"  Approach Number: {approach['approach_number']}")
        print(f"  Content Length: {len(approach['content'])} characters")
        print(f"  Content Preview: {approach['content'][:100]}...\n")

    # Example with numbered list format
    print("=== Testing Numbered List Format ===\n")

    numbered_response = """
1. Traditional Value Strategy
Focus on P/E, P/B, and EV/EBITDA ratios with sector-neutral implementation.

2. Quality Growth Approach
Emphasize ROE, earnings growth consistency, and balance sheet strength.

3. Momentum Cross-Sectional
Rank securities based on 3-12 month price momentum with volatility adjustment.
"""

    numbered_approaches = _parse_multiple_approaches(numbered_response, "UNIVERSE", "Value Strategy")
    print(f"Parsed {len(numbered_approaches)} approaches from numbered list:\n")

    for approach in numbered_approaches:
        print(f"  - {approach['title']}")
        print(f"    Content: {approach['content'][:60]}...\n")


if __name__ == "__main__":
    demo_parsing()
