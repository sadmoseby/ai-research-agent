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
from .nodes.prior_art import prior_art_node
from .nodes.synthesize import synthesize_node
from .nodes.validate import validate_node
from .nodes.web_research import web_research_node
from .state import ResearchState

# Get logger for the graph
logger = get_logger("graph")


def create_logged_node_wrapper(node_func, node_name: str):
    """Create a wrapper for node functions that adds logging."""

    def wrapper(state: ResearchState, config: Config):
        logger.info("Starting execution of node: %s", node_name)
        logger.debug("Node %s received state keys: %s", node_name, list(state.keys()))

        try:
            result = node_func(state, config)
            logger.info("Successfully completed node: %s", node_name)
            result_info = list(result.keys()) if isinstance(result, dict) else "non-dict result"
            logger.debug("Node %s returned keys: %s", node_name, result_info)
            return result
        except Exception as e:
            logger.error("Error in node %s: %s", node_name, str(e), exc_info=True)
            raise

    return wrapper


def create_research_graph(config: Config) -> StateGraph:
    """Create the LangGraph workflow for research proposal generation."""
    logger.info("Creating research graph with configuration")

    # Create the graph
    workflow = StateGraph(ResearchState)

    # Add nodes with node-specific config binding and logging
    logger.debug("Adding nodes to workflow graph")
    workflow.add_node(
        "plan",
        create_logged_node_wrapper(lambda state: plan_node(state, config.for_node("plan")), "plan"),
    )
    workflow.add_node(
        "web_research",
        create_logged_node_wrapper(
            lambda state: web_research_node(state, config.for_node("web_research")),
            "web_research",
        ),
    )
    workflow.add_node(
        "prior_art",
        create_logged_node_wrapper(
            lambda state: prior_art_node(state, config.for_node("prior_art")),
            "prior_art",
        ),
    )
    workflow.add_node(
        "criticism",
        create_logged_node_wrapper(
            lambda state: criticism_node(state, config.for_node("criticism")),
            "criticism",
        ),
    )
    workflow.add_node(
        "synthesize",
        create_logged_node_wrapper(
            lambda state: synthesize_node(state, config.for_node("synthesize")),
            "synthesize",
        ),
    )
    workflow.add_node(
        "validate",
        create_logged_node_wrapper(lambda state: validate_node(state, config.for_node("validate")), "validate"),
    )
    workflow.add_node(
        "persist",
        create_logged_node_wrapper(lambda state: persist_node(state, config.for_node("persist")), "persist"),
    )

    # Define the workflow with conditional routing
    logger.debug("Setting up workflow edges")
    workflow.add_edge(START, "plan")
    workflow.add_edge("plan", "web_research")
    workflow.add_edge("web_research", "prior_art")

    # Conditional edge for prior art check
    def route_after_prior_art(state: ResearchState) -> str:
        should_restart = state.get("should_restart_planning", False)
        next_node = "plan" if should_restart else "criticism"
        logger.info(
            "Prior art routing decision: should_restart=%s -> %s",
            should_restart,
            next_node,
        )
        return next_node

    workflow.add_conditional_edges("prior_art", route_after_prior_art, {"plan": "plan", "criticism": "criticism"})

    # Conditional edge for criticism check
    def route_after_criticism(state: ResearchState) -> str:
        should_restart = state.get("should_restart_planning", False)
        next_node = "plan" if should_restart else "synthesize"
        logger.info(
            "Criticism routing decision: should_restart=%s -> %s",
            should_restart,
            next_node,
        )
        return next_node

    workflow.add_conditional_edges("criticism", route_after_criticism, {"plan": "plan", "synthesize": "synthesize"})

    workflow.add_edge("synthesize", "validate")

    # Conditional edge for validation repair
    def should_retry_validation(state: ResearchState) -> str:
        has_errors = bool(state.get("validation_errors"))
        repair_attempts = state.get("repair_attempts", 0)
        next_node = "synthesize" if has_errors and repair_attempts < 1 else "persist"
        logger.info(
            "Validation routing decision: has_errors=%s, repair_attempts=%d -> %s",
            has_errors,
            repair_attempts,
            next_node,
        )
        return next_node

    workflow.add_conditional_edges(
        "validate",
        should_retry_validation,
        {"synthesize": "synthesize", "persist": "persist"},
    )

    workflow.add_edge("persist", END)

    # Add memory checkpointing
    memory = MemorySaver()
    logger.info("Compiling research graph with memory checkpointing")

    return workflow.compile(checkpointer=memory)
