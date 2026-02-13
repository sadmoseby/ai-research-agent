#!/usr/bin/env python3
"""
Example demonstrating how to use the --components CLI argument to focus
research on specific components of a trading strategy.

This example shows how to:
1. Use specific components via CLI
2. Compare different component combinations
3. Understand the ResearchComponents flags
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agent.state import ResearchComponents


def demonstrate_component_flags():
    """Show how ResearchComponents flags work."""
    print("=== ResearchComponents Flag System ===\n")

    components = [
        ("UNIVERSE", ResearchComponents.UNIVERSE),
        ("ALPHA", ResearchComponents.ALPHA),
        ("PORTFOLIO", ResearchComponents.PORTFOLIO),
        ("EXECUTION", ResearchComponents.EXECUTION),
        ("RISK", ResearchComponents.RISK),
    ]

    print("Individual component values:")
    for name, flag in components:
        print(f"  {name:<10} = {flag:<2} (binary: {bin(flag)})")

    print("\nCombination examples:")
    # Alpha + Universe
    combo1 = ResearchComponents.ALPHA | ResearchComponents.UNIVERSE
    print(f"  ALPHA + UNIVERSE      = {combo1} (binary: {bin(combo1)})")

    # Full strategy
    combo2 = (
        ResearchComponents.UNIVERSE
        | ResearchComponents.ALPHA
        | ResearchComponents.PORTFOLIO
        | ResearchComponents.EXECUTION
        | ResearchComponents.RISK
    )
    print(f"  All components        = {combo2} (binary: {bin(combo2)})")

    print("\n")


def run_cli_example(components_str: str, description: str):
    """Run a CLI example with specific components."""
    print(f"=== {description} ===")
    print(
        f"Command: python3 main.py propose --idea 'momentum strategy' --instruments 'stocks' --components '{components_str}'"
    )
    print()

    # Note: In a real scenario, you would run:
    # subprocess.run([
    #     "python3", "main.py", "propose",
    #     "--idea", "momentum strategy",
    #     "--instruments", "stocks",
    #     "--components", components_str
    # ], cwd=project_root)

    print("This would focus research only on the specified components.\n")


def main():
    """Demonstrate the components CLI feature."""
    print("Components CLI Demo")
    print("=" * 50)
    print()

    # Show how the flag system works
    demonstrate_component_flags()

    print("=== CLI Usage Examples ===\n")

    print("The CLI defaults to component-by-component synthesis, which generates")
    print("each component separately for better quality and modularity.\n")

    # Show various CLI usage patterns
    examples = [
        ("alpha", "Alpha-focused research (signal generation only)"),
        ("universe,alpha", "Universe selection + Alpha generation"),
        ("portfolio,execution", "Portfolio construction + Execution strategy"),
        ("universe,alpha,risk", "Core strategy with risk management"),
        ("universe,alpha,portfolio,execution,risk", "Complete strategy research"),
    ]

    for components_str, description in examples:
        run_cli_example(components_str, description)

    print("=== Advanced Usage ===\n")

    print("1. Synthesis modes:")
    print("   Default (component-by-component): python3 main.py propose --idea 'momentum' --instruments 'stocks'")
    print("   Unified synthesis: python3 main.py propose --idea 'momentum' --instruments 'stocks' --unified-synthesis")
    print()

    print("2. Environment variable alternative for components:")
    print("   export COMPONENTS='universe,alpha'")
    print("   python3 main.py propose --idea 'momentum strategy' --instruments 'stocks'")
    print()

    print("3. Combined with alpha-only mode:")
    print("   python3 main.py propose --idea 'momentum strategy' --instruments 'stocks' --alpha-only")
    print("   (Note: alpha-only mode overrides --components and uses unified synthesis)")
    print()

    print("3. Component validation:")
    print("   Invalid components will show an error:")
    print("   python3 main.py propose --idea 'test' --instruments 'stocks' --components 'invalid,alpha'")
    print("   Error: Invalid components: ['invalid']. Valid options are: alpha, execution, portfolio, risk, universe")
    print()

    print("=== Use Cases ===\n")

    use_cases = [
        ("Research Phase", "universe,alpha", "Focus on idea validation and signal generation"),
        ("Implementation Phase", "portfolio,execution", "Focus on practical implementation details"),
        ("Risk Assessment", "risk", "Focus specifically on risk management aspects"),
        ("Quick Prototype", "alpha", "Generate just the core trading signal"),
        ("Production Ready", "universe,alpha,portfolio,execution,risk", "Complete end-to-end strategy"),
    ]

    for phase, components, description in use_cases:
        print(f"{phase:<20} --components '{components}'")
        print(f"                     {description}")
        print()


if __name__ == "__main__":
    main()
