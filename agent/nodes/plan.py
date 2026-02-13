"""
Planning node for research workflow using MCP tools.
"""

from typing import Any, Dict

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchComponents, ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.plan")


def plan_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Plan the research approach based on the idea."""
    logger.info("Starting planning node execution")

    # Initialize LLM client for this node
    llm_client = LLMClient(config, node_name="plan")
    logger.debug("Initialized LLM client: %s", llm_client.get_provider_info())

    # Create node-specific MCP client to check available tools
    mcp_client = MCPClient(config, llm_client, node_name="plan")
    available_tools = mcp_client.get_available_tool_names()

    logger.debug("Planning node has access to tools: %s", available_tools)
    print(f"Planning node has access to tools: {available_tools}")

    idea = state["idea"]
    alpha_only = state.get("alpha_only", False)
    planning_iteration = state.get("planning_iteration", 0)
    restart_reason = state.get("restart_reason", "")

    logger.info(
        "Planning parameters: idea_length=%d, alpha_only=%s, iteration=%d",
        len(idea),
        alpha_only,
        planning_iteration,
    )

    # Increment planning iteration
    new_iteration = planning_iteration + 1

    # Modify the idea/approach if this is a restart
    modified_idea = idea
    iteration_note = ""

    if restart_reason:
        logger.info("Planning restart triggered: %s", restart_reason)
        iteration_note = f"\n\nITERATION {new_iteration} - ADDRESSING: {restart_reason}"

        # Add guidance based on restart reason
        if "prior art" in restart_reason.lower() or "similar implementations" in restart_reason.lower():
            iteration_note += "\nFocus on: Novel approaches, unique data sources, differentiation strategies"
            logger.debug("Added prior art focus guidance")
        elif "viability score" in restart_reason.lower():
            iteration_note += "\nFocus on: Risk mitigation, implementation feasibility, alternative approaches"
            logger.debug("Added viability focus guidance")

    # Add tool-aware planning note
    tools_note = (
        f"\n\nAVAILABLE RESEARCH TOOLS: {', '.join(available_tools) if available_tools else 'Basic tools only'}"
    )

    # Generate research plan using centralized prompts
    if alpha_only:
        logger.debug("Generating alpha-only research plan")
        plan = ResearchPrompts.ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE.format(idea=modified_idea).strip()
    else:
        # If specific components are provided in state, scope the plan accordingly
        components_flag = state.get("components") or config.get_components_from_config()
        if components_flag:
            # Map IntFlag/int bitmask to list of component names safely
            selected_components: list[str] = []
            if isinstance(components_flag, (int, ResearchComponents)):
                if components_flag & ResearchComponents.UNIVERSE:
                    selected_components.append("UNIVERSE")
                if components_flag & ResearchComponents.ALPHA:
                    selected_components.append("ALPHA")
                if components_flag & ResearchComponents.PORTFOLIO:
                    selected_components.append("PORTFOLIO")
                if components_flag & ResearchComponents.EXECUTION:
                    selected_components.append("EXECUTION")
                if components_flag & ResearchComponents.RISK:
                    selected_components.append("RISK")

            logger.debug("Generating component-scoped research plan for: %s", selected_components)
            plan = ResearchPrompts.format_full_plan_for_components(idea=modified_idea, components=selected_components)
        else:
            logger.debug("Generating full research plan")
            plan = ResearchPrompts.FULL_RESEARCH_PLAN_TEMPLATE.format(idea=modified_idea).strip()

    # Add iteration guidance and tool information to plan
    plan += iteration_note + tools_note

    # Get search queries from prompts (component-aware if available)
    if "components_flag" in locals() and components_flag:
        selected_components = []
        if isinstance(components_flag, (int, ResearchComponents)):
            if components_flag & ResearchComponents.UNIVERSE:
                selected_components.append("UNIVERSE")
            if components_flag & ResearchComponents.ALPHA:
                selected_components.append("ALPHA")
            if components_flag & ResearchComponents.PORTFOLIO:
                selected_components.append("PORTFOLIO")
            if components_flag & ResearchComponents.EXECUTION:
                selected_components.append("EXECUTION")
            if components_flag & ResearchComponents.RISK:
                selected_components.append("RISK")
        search_queries = ResearchPrompts.get_component_scoped_queries(modified_idea, selected_components, alpha_only)
    else:
        search_queries = ResearchPrompts.get_search_queries(modified_idea, alpha_only)
    logger.debug("Generated %d base search queries", len(search_queries))

    # Add variation to search queries for iterations
    if new_iteration > 1:
        additional_queries = [
            f"{modified_idea} novel approach alternative",
            f"{modified_idea} differentiation strategy unique",
            f"alternative {modified_idea} methodology",
        ]
        search_queries.extend(additional_queries)
        logger.debug("Added %d iteration-specific search queries", len(additional_queries))

    logger.info("Planning completed successfully with %d search queries", len(search_queries))

    return {
        "research_plan": plan,
        "search_queries": search_queries,
        "planning_iteration": new_iteration,
        "should_restart_planning": False,  # Reset restart flag
        "restart_reason": None,  # Clear restart reason
        "mcp_tools_available": available_tools,
        # Persist component selection for downstream nodes
        "components": components_flag if "components_flag" in locals() else state.get("components"),
        "current_step": "web_research",
    }
