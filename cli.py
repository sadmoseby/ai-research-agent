#!/usr/bin/env python3
"""
CLI entry point for the Lean Research Agent.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

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
            f"Invalid components: {invalid_components}. " f"Valid options are: {', '.join(sorted(valid_components))}"
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
        # Load config from file if provided, otherwise from .env
        if args.config:
            print(f"📄 Loading configuration from: {args.config}")
            config = Config.from_file(args.config)
            print(f"✅ Configuration loaded from file")
        else:
            print(f"📄 Loading configuration from .env file")
            config = Config.from_dotenv()
            print(f"✅ Configuration loaded from .env")

        # Validate required parameters from config
        if not config.idea:
            raise ValueError("'idea' is required in config file or .env (IDEA=...)")
        if not config.instruments:
            raise ValueError("'instruments' is required in config file or .env (INSTRUMENTS=...)")

        # Setup logging
        config.setup_logging()

        # Set synthesis mode based on config
        import os
        if config.unified_synthesis:
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "false"
        else:
            # Default to component-by-component
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

        graph = create_research_graph(config)

        slug = config.slug or create_slug(config.idea)
        instruments = parse_instruments(config.instruments)

        # Parse components if provided
        components = None
        if config.components:
            components = parse_components(config.components)

        initial_state = ResearchState(
            idea=config.idea,
            alpha_only=config.alpha_only,
            instruments=instruments,
            components=components,
            slug=slug,
            output_dir=config.output_dir,
            branch_name=config.branch_name,
            image_name=config.image_name,
            upload_to_github=config.upload_to_github,
            github_owner=config.github_owner,
            github_repository=config.github_repository,
            current_step="plan",
            should_restart_planning=False,
            planning_iteration=0,
            repair_attempts=0,
        )

        print(f"🔬 Starting research for: {config.idea}")
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
        output_path = Path(config.output_dir) / f"{slug}.json"
        print(f"📁 Will write to: {output_path}")

        # Show synthesis mode
        synthesis_mode = (
            "component-by-component"
            if os.environ.get("SYNTHESIZE_COMPONENT_BY_COMPONENT", "false").lower() == "true"
            else "unified"
        )
        print(f"⚙️  Synthesis mode: {synthesis_mode}")
        if config.alpha_only:
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
            if final_state.get("github_issue_url"):
                print(f"🐙 GitHub issue: {final_state['github_issue_url']}")
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
    propose_parser = subparsers.add_parser(
        "propose", 
        help="Generate a research proposal (all parameters from config file or .env)"
    )
    propose_parser.add_argument(
        "--config",
        help="Path to JSON or YAML config file. If not provided, loads from .env file.",
    )

    args = parser.parse_args()

    if args.command == "propose":
        asyncio.run(propose_command(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
