import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.graph import create_research_graph
from agent.state import ResearchComponents
from agent.config import Config


def parse_components(components_str: str) -> int:
    """Parse a comma-separated string of components into a ResearchComponents bitmask."""
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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("propose", nargs="?")
    p.add_argument("--idea", required=True)
    p.add_argument("--alpha-only", action="store_true")
    p.add_argument("--slug", default=None)
    p.add_argument(
        "--components",
        help="Research components to focus on (comma-separated): universe, alpha, portfolio, execution, risk"
    )
    p.add_argument(
        "--unified-synthesis",
        action="store_true",
        help="Use unified synthesis instead of component-by-component synthesis (CLI defaults to component-by-component)"
    )
    args = p.parse_args()

    # Default to component-by-component synthesis for CLI usage
    import os
    if args.unified_synthesis:
        os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "false"
    else:
        os.environ["SYNTHESIZE_COMPONENT_BY_COMPONENT"] = "true"

    # Parse components if provided
    components = None
    if args.components:
        components = parse_components(args.components)

    state_dict = {
        "idea": args.idea,
        "alpha_only": bool(args.alpha_only),
        "slug": args.slug or args.idea.lower().replace(" ", "_")[:64],
    }
    
    if components is not None:
        state_dict["components"] = components

    config = Config.from_env()
    app = create_research_graph(config)
    app.invoke(
        state_dict,
        config={"configurable": {"thread_id": args.slug or "default"}},
    )

    print("Done. See proposals/ for output.")


if __name__ == "__main__":
    main()
