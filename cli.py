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
        # Enable component-by-component synthesis by default, unless unified is requested
        import os

        if args.unified_synthesis:
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "false"
        elif "SYNTHESIZE_COMPONENT_BY_COMPONENT" not in os.environ:
            os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

        config = Config.from_env()

        # Setup logging
        config.setup_logging()

        graph = create_research_graph(config)

        slug = args.slug or create_slug(args.idea)

        initial_state = ResearchState(
            idea=args.idea,
            alpha_only=args.alpha_only,
            slug=slug,
            current_step="plan",
            should_restart_planning=False,
            planning_iteration=0,
            repair_attempts=0,
        )

        print(f"🔬 Starting research for: {args.idea}")
        print(f"📁 Will write to: proposals/{slug}.json")

        # Show synthesis mode
        synthesis_mode = (
            "component-by-component"
            if os.environ.get("SYNTHESIZE_COMPONENT_BY_COMPONENT", "false").lower() == "true"
            else "unified"
        )
        print(f"⚙️  Synthesis mode: {synthesis_mode}")
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
    propose_parser.add_argument("--alpha-only", action="store_true", help="Generate alpha-only proposal")
    propose_parser.add_argument("--slug", help="Custom slug for output filename")
    propose_parser.add_argument(
        "--unified-synthesis",
        action="store_true",
        help="Use unified synthesis instead of component-by-component (default: component-by-component)",
    )

    args = parser.parse_args()

    if args.command == "propose":
        asyncio.run(propose_command(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
