"""
Example usage of the Lean Research Agent.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config
from agent.graph import create_research_graph
from agent.state import ResearchState


async def example_research():
    """Example research workflow."""

    # This would normally come from environment variables
    # For demo purposes, we'll show the structure
    print("🔬 Lean Research Agent Example")
    print("=" * 50)

    # Note: In real usage, load from environment
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nPlease set up your .env file with required API keys.")
        print("See .env.template for the required format.")
        return

    # Create the research graph
    graph = create_research_graph(config)

    # Example research ideas
    examples = [
        {
            "idea": "momentum-based sector rotation using ETF data",
            "alpha_only": False,
            "slug": "momentum_sector_rotation",
        },
        {
            "idea": "mean reversion trading on individual stocks",
            "alpha_only": True,
            "slug": "mean_reversion_alpha",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n📋 Example {i}: {example['idea']}")
        print(f"   Alpha-only: {example['alpha_only']}")
        print(f"   Output: proposals/{example['slug']}.json")

        # Create initial state
        initial_state = ResearchState(
            idea=example["idea"],
            alpha_only=example["alpha_only"],
            slug=example["slug"],
            current_step="plan",
            repair_attempts=0,
        )

        print("   Status: Would execute research workflow...")
        # In real usage: result = await graph.ainvoke(initial_state)

    print("\n✨ To run these examples:")
    print("python main.py propose --idea 'momentum-based sector rotation using ETF data'")
    print("python main.py propose --idea 'mean reversion trading' --alpha-only")


if __name__ == "__main__":
    asyncio.run(example_research())
