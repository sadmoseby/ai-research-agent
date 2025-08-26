#!/usr/bin/env python3
"""
Example demonstrating the restructured prompts for component research.

This example shows how the research prompts are structured for each component
(UNIVERSE, ALPHA, PORTFOLIO, EXECUTION, RISK) with specific combination logic
and focus areas.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.config import Config
from agent.prompts import ResearchPrompts


def demo_prompt_restructure():
    """Demonstrate the updated prompt structure for component combination."""
    print("📝 Component Research Prompts Demo")
    print("=" * 50)
    print("This demo shows the structured prompts used for each research component.\n")

    components = ["UNIVERSE", "ALPHA", "PORTFOLIO", "EXECUTION", "RISK"]

    for component in components:
        print(f"=== {component} COMPONENT ===")

        # Show system prompt key points
        system_prompt = ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS[component]
        if "IMPORTANT:" in system_prompt:
            important_section = system_prompt.split("IMPORTANT:")[1].split("Focus Areas:")[0].strip()
            print(f"Key Instruction: {important_section}\n")

        # Show user prompt combination logic
        user_prompt = ResearchPrompts.COMPONENT_RESEARCH_USER_PROMPTS[component]
        if "COMBINATION LOGIC:" in user_prompt:
            combination_logic = user_prompt.split("COMBINATION LOGIC:")[1].split("Please use")[0].strip()
            print(f"Combination Logic: {combination_logic}\n")

        print("-" * 80)
        print()


def demo_combination_scenarios():
    """Demonstrate how different combinations would work in practice."""
    print("=== Practical Combination Examples ===\n")

    scenarios = {
        "UNIVERSE": {
            "approaches": ["Large Cap Growth", "High Volume Liquidity", "Sector Diversified"],
            "combination": "Asset included if it passes ANY of these criteria (OR logic)",
            "result": "Broader universe capturing opportunities across different screening methods",
        },
        "ALPHA": {
            "approaches": ["Momentum Factor", "Mean Reversion", "Earnings Quality"],
            "combination": "Ensemble approach considering insights from ALL models",
            "result": "Robust alpha signal leveraging diverse predictive sources",
        },
        "PORTFOLIO": {
            "approaches": ["Risk Parity Optimization"],
            "combination": "Single comprehensive method for all position sizing",
            "result": "Unified portfolio construction with consistent risk management",
        },
        "EXECUTION": {
            "approaches": ["TWAP with Market Impact Minimization"],
            "combination": "Single execution strategy for all trades",
            "result": "Consistent transaction cost optimization across all orders",
        },
        "RISK": {
            "approaches": ["Factor Risk Model", "VaR Estimation", "Stress Testing"],
            "combination": "Multi-layered framework using ALL risk approaches",
            "result": "Comprehensive risk protection through diverse measurement techniques",
        },
    }

    for component, info in scenarios.items():
        print(f"=== {component} EXAMPLE ===")
        print(f"Approaches: {', '.join(info['approaches'])}")
        print(f"Combination: {info['combination']}")
        print(f"Result: {info['result']}")
        print()

    print("=== Final LEAN Algorithm Structure ===")
    print(
        """
    Universe Selection: OR combination of multiple screening criteria
                       ↓
    Alpha Generation: Ensemble of multiple alpha signals
                       ↓
    Portfolio Construction: Single comprehensive optimization model
                       ↓
    Risk Management: Multi-layered framework with diverse approaches
                       ↓
    Execution: Single optimized execution strategy
    """
    )


if __name__ == "__main__":
    demo_prompt_restructure()
    demo_combination_scenarios()
