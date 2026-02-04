#!/usr/bin/env python3
"""
CLI entry point for the Lean Research Agent.
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config
from agent.graph import create_research_graph
from agent.state import ResearchState


def parse_instruments(instruments_str: str) -> list[str]:
    """Parse a comma-separated string of instruments into a list."""
    valid_instruments = {"stocks", "options", "futures", "forex", "crypto"}

    if not instruments_str:
        raise ValueError("Instruments cannot be empty")

    instruments = [inst.strip().lower() for inst in instruments_str.split(",")]

    # Validate each instrument
    invalid_instruments = [inst for inst in instruments if inst not in valid_instruments]
    if invalid_instruments:
        raise ValueError(
            f"Invalid instruments: {invalid_instruments}. " f"Valid options are: {', '.join(sorted(valid_instruments))}"
        )

    # Remove duplicates while preserving order
    return list(dict.fromkeys(instruments))


def parse_components(components_str: str) -> int:
    """Parse a comma-separated string of components into a ResearchComponents bitmask."""
    from agent.state import ResearchComponents
    
    valid_components = {"universe", "alpha", "portfolio", "execution", "risk"}
    
    if not components_str:
        raise ValueError("Components cannot be empty")
    
    components = [comp.strip().lower() for comp in components_str.split(",")]
    
    # Validate each component
    invalid_components = [comp for comp in components if comp not in valid_components]
    if invalid_components:
        raise ValueError(
            f"Invalid components: {invalid_components}. "
            f"Valid options are: {', '.join(sorted(valid_components))}"
        )
    
    # Map to bitmask
    mapping = {
        "universe": ResearchComponents.UNIVERSE,
        "alpha": ResearchComponents.ALPHA,
        "portfolio": ResearchComponents.PORTFOLIO,
        "execution": ResearchComponents.EXECUTION,
        "risk": ResearchComponents.RISK,
    }
    
    bitmask = 0
    for comp in components:
        bitmask |= int(mapping[comp])
    
    return bitmask


def create_slug(idea_text: str) -> str:
    """Create a filesystem-safe slug from idea text."""
    import re

    # Take first 50 chars, lowercase, replace non-alphanumeric with underscores
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", idea_text.lower()[:50])
    slug = slug.strip("_")
    return slug or "research_proposal"


async def propose_command(args):
    """Execute the propose command."""
    try:
        # Default to component-by-component synthesis for CLI usage
        # This can be overridden with --unified-synthesis flag
        import os

        if args.unified_synthesis:
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "false"
        else:
            # Always default to component-by-component when using CLI
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

        config = Config.from_env()

        # Setup logging
        config.setup_logging()

        graph = create_research_graph(config)

        slug = args.slug or create_slug(args.idea)
        instruments = parse_instruments(args.instruments)
        
        # Parse components if provided
        components = None
        if args.components:
            components = parse_components(args.components)

        initial_state = ResearchState(
            idea=args.idea,
            alpha_only=args.alpha_only,
            instruments=instruments,
            components=components,
            slug=slug,
            current_step="plan",
            should_restart_planning=False,
            planning_iteration=0,
            repair_attempts=0,
        )

        print(f"🔬 Starting research for: {args.idea}")
        print(f"🎯 Trading instruments: {', '.join(instruments)}")
        if components:
            from agent.state import ResearchComponents
            component_names = []
            if components & ResearchComponents.UNIVERSE:
                component_names.append("UNIVERSE")
            if components & ResearchComponents.ALPHA:
                component_names.append("ALPHA")
            if components & ResearchComponents.PORTFOLIO:
                component_names.append("PORTFOLIO")
            if components & ResearchComponents.EXECUTION:
                component_names.append("EXECUTION")
            if components & ResearchComponents.RISK:
                component_names.append("RISK")
            print(f"🧩 Research components: {', '.join(component_names)}")
        print(f"📁 Will write to: proposals/{slug}.json")

        # Show synthesis mode
        synthesis_mode = (
            "component-by-component"
            if os.environ.get("SYNTHESIZE_COMPONENT_BY_COMPONENT", "false").lower() == "true"
            else "unified"
        )
        print(f"⚙️  Synthesis mode: {synthesis_mode} (CLI default)")
        if args.alpha_only:
            print("🎯 Alpha-only mode: will use unified synthesis regardless of setting")

        # Run the graph
        final_state = await graph.ainvoke(initial_state, config={"configurable": {"thread_id": slug}})

        # Show restart information if applicable
        planning_iteration = final_state.get("planning_iteration", 0)
        if planning_iteration > 1:
            print(f"🔄 Planning restarted {planning_iteration - 1} time(s) for quality improvement")

        if final_state.get("error"):
            print(f"❌ Error: {final_state['error']}")
            sys.exit(1)
        elif final_state.get("proposal_path"):
            print(f"✅ Proposal written to: {final_state['proposal_path']}")
            if final_state.get("state_path"):
                print(f"📊 Final state written to: {final_state['state_path']}")
            if final_state.get("validation_report"):
                print(f"📋 Validation: {final_state['validation_report']}")
        else:
            print("❌ Unknown error occurred")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Lean Research Agent")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Propose command
    propose_parser = subparsers.add_parser("propose", help="Generate a research proposal")
    propose_parser.add_argument("--idea", required=True, help="Research idea (free text)")
    propose_parser.add_argument(
        "--instruments",
        required=True,
        help="Financial instruments to trade (comma-separated): stocks, options, futures, forex, crypto",
    )
    propose_parser.add_argument("--alpha-only", action="store_true", help="Generate alpha-only proposal")
    propose_parser.add_argument("--slug", help="Custom slug for output filename")
    propose_parser.add_argument(
        "--components",
        help="Research components to focus on (comma-separated): universe, alpha, portfolio, execution, risk"
    )
    propose_parser.add_argument(
        "--unified-synthesis",
        action="store_true",
        help="Use unified synthesis instead of component-by-component synthesis (CLI defaults to component-by-component)",
    )

    args = parser.parse_args()

    if args.command == "propose":
        asyncio.run(propose_command(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
