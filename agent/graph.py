"""
LangGraph workflow for the Lean Research Agent.
"""

import logging

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from .config import Config, get_logger
from .nodes.criticism import criticism_node
from .nodes.persist import persist_node
from .nodes.plan import plan_node
from .nodes.synthesize import synthesize_node
from .nodes.web_research import web_research_node
from .state import ResearchState

# Get logger for the graph
logger = get_logger("graph")


def create_logged_node_wrapper(node_func, node_name: str):
    """Create a wrapper for node functions that adds logging."""
    import asyncio
    import inspect

    if inspect.iscoroutinefunction(node_func):
        # Async wrapper for async node functions
        async def async_wrapper(state: ResearchState):
            logger.info("Starting execution of node: %s", node_name)
            logger.debug("Node %s received state keys: %s", node_name, list(state.keys()))

            try:
                result = await node_func(state)
                logger.info("Successfully completed node: %s", node_name)
                result_info = list(result.keys()) if isinstance(result, dict) else "non-dict result"
                logger.debug("Node %s returned keys: %s", node_name, result_info)
                return result
            except Exception as e:
                logger.error("Error in node %s: %s", node_name, str(e), exc_info=True)
                raise

        return async_wrapper
    else:
        # Sync wrapper for sync node functions
        def sync_wrapper(state: ResearchState):
            logger.info("Starting execution of node: %s", node_name)
            logger.debug("Node %s received state keys: %s", node_name, list(state.keys()))

            try:
                result = node_func(state)
                logger.info("Successfully completed node: %s", node_name)
                result_info = list(result.keys()) if isinstance(result, dict) else "non-dict result"
                logger.debug("Node %s returned keys: %s", node_name, result_info)
                return result
            except Exception as e:
                logger.error("Error in node %s: %s", node_name, str(e), exc_info=True)
                raise

        return sync_wrapper


def get_next_enabled_node(config: Config, current_node: str, node_sequence: list[str]) -> str:
    """Find the next enabled node in the sequence after current_node."""
    try:
        current_index = node_sequence.index(current_node)
        for next_node in node_sequence[current_index + 1 :]:
            if config.is_node_enabled(next_node):
                return next_node
        return END
    except ValueError:
        # current_node not in sequence, return first enabled node
        for node in node_sequence:
            if config.is_node_enabled(node):
                return node
        return END


def create_research_graph(config: Config) -> StateGraph:
    """Create the LangGraph workflow for research proposal generation."""
    logger.info("Creating research graph with configuration")

    # Create the graph
    workflow = StateGraph(ResearchState)

    # Get enabled nodes
    enabled_nodes = config.get_enabled_nodes()
    disabled_nodes = config.get_disabled_nodes()

    if disabled_nodes:
        logger.info("Disabled nodes: %s", disabled_nodes)
    logger.info("Enabled nodes: %s", enabled_nodes)

    # Validate essential nodes
    if not enabled_nodes:
        raise ValueError("No nodes are enabled! At least one node must be enabled.")

    # Check for critical nodes - at minimum we need synthesis and persistence
    critical_nodes = ["synthesize", "persist"]
    missing_critical = [node for node in critical_nodes if node not in enabled_nodes]
    if missing_critical:
        logger.warning("Critical nodes are disabled: %s. This may cause issues.", missing_critical)

    # Add nodes with node-specific config binding and logging (only if enabled)
    logger.debug("Adding enabled nodes to workflow graph")

    if "plan" in enabled_nodes:
        workflow.add_node(
            "plan",
            create_logged_node_wrapper(lambda state: plan_node(state, config.for_node("plan")), "plan"),
        )

    if "web_research" in enabled_nodes:

        async def web_research_wrapper(state):
            return await web_research_node(state, config.for_node("web_research"))

        workflow.add_node(
            "web_research",
            create_logged_node_wrapper(web_research_wrapper, "web_research"),
        )

    if "criticism" in enabled_nodes:

        async def criticism_wrapper(state):
            return await criticism_node(state, config.for_node("criticism"))

        workflow.add_node(
            "criticism",
            create_logged_node_wrapper(criticism_wrapper, "criticism"),
        )

    if "synthesize" in enabled_nodes:

        async def synthesize_wrapper(state):
            return await synthesize_node(state, config.for_node("synthesize"))

        workflow.add_node(
            "synthesize",
            create_logged_node_wrapper(synthesize_wrapper, "synthesize"),
        )

    if "persist" in enabled_nodes:

        async def persist_wrapper(state):
            return await persist_node(state, config.for_node("persist"))

        workflow.add_node(
            "persist",
            create_logged_node_wrapper(persist_wrapper, "persist"),
        )

    # Define the workflow with conditional routing
    logger.debug("Setting up workflow edges")

    # Define the standard node sequence
    node_sequence = ["plan", "web_research", "criticism", "synthesize", "persist"]

    # Start with the first enabled node
    first_enabled_node = get_next_enabled_node(config, "", node_sequence)
    if first_enabled_node != END:
        workflow.add_edge(START, first_enabled_node)
    else:
        raise ValueError("No nodes are enabled! At least one node must be enabled.")

    # Add edges between consecutive enabled nodes
    if "plan" in enabled_nodes:
        next_after_plan = get_next_enabled_node(config, "plan", node_sequence)
        if next_after_plan != END:
            workflow.add_edge("plan", next_after_plan)

    if "web_research" in enabled_nodes:
        next_after_web_research = get_next_enabled_node(config, "web_research", node_sequence)
        if next_after_web_research != END:
            workflow.add_edge("web_research", next_after_web_research)

    # Special routing for criticism with restart logic
    if "criticism" in enabled_nodes:

        def route_after_criticism(state: ResearchState) -> str:
            should_restart = state.get("should_restart_planning", False)
            if should_restart and config.is_node_enabled("plan"):
                logger.info("Criticism routing decision: should_restart=True -> plan")
                return "plan"

            # Find next enabled node after criticism
            next_candidates = ["synthesize", "persist"]
            for candidate in next_candidates:
                if config.is_node_enabled(candidate):
                    logger.info("Criticism routing decision: should_restart=%s -> %s", should_restart, candidate)
                    return candidate

            logger.info("Criticism routing decision: no enabled nodes found -> END")
            return END

        routing_options = {}
        if config.is_node_enabled("plan"):
            routing_options["plan"] = "plan"
        for candidate in ["synthesize", "persist"]:
            if config.is_node_enabled(candidate):
                routing_options[candidate] = candidate
        routing_options[END] = END

        workflow.add_conditional_edges("criticism", route_after_criticism, routing_options)

    # Special routing for synthesize with validation and repair logic
    if "synthesize" in enabled_nodes:

        def route_after_synthesize(state: ResearchState) -> str:
            current_step = state.get("current_step", "")

            if current_step == "synthesize":
                # Retry synthesis (validation repair failed)
                logger.info("Synthesize routing decision: retry synthesis")
                return "synthesize"
            else:
                # Normal flow to next node
                next_node = get_next_enabled_node(config, "synthesize", node_sequence)
                logger.info("Synthesize routing decision: continue to %s", next_node)
                return next_node

        routing_options = {"synthesize": "synthesize"}
        for candidate in ["persist"]:
            if config.is_node_enabled(candidate):
                routing_options[candidate] = candidate
        routing_options[END] = END

        workflow.add_conditional_edges("synthesize", route_after_synthesize, routing_options)

    # Final edge to END
    if "persist" in enabled_nodes:
        workflow.add_edge("persist", END)

    # Add memory checkpointing
    memory = MemorySaver()
    logger.info("Compiling research graph with memory checkpointing")

    return workflow.compile(checkpointer=memory)
