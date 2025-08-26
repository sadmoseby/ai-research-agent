"""
Persistence node for saving research proposals using MCP (Model Context Protocol).
"""

import json
from pathlib import Path
from typing import Any, Dict

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.persist")


async def persist_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Persist the research proposal to various outputs using MCP."""
    logger.info("Starting persistence node execution")

    # Initialize LLM client for this node
    llm_client = LLMClient(config, node_name="persist")
    logger.debug("Initialized LLM client: %s", llm_client.get_provider_info())

    # Create node-specific MCP client
    mcp_client = MCPClient(config, llm_client, node_name="persist")
    available_tools = mcp_client.get_available_tool_names()

    print(f"Persistence node has access to tools: {available_tools}")

    final_proposal = state.get("final_proposal")
    slug = state.get("slug", "research_proposal")
    validation_report = state.get("validation_report", "")

    logger.info("Persist node state keys: %s", list(state.keys()))
    logger.info("final_proposal present: %s", final_proposal is not None)
    logger.info("raw_proposal present: %s", state.get("raw_proposal") is not None)

    if not final_proposal:
        # Check if we have raw_proposal as fallback
        raw_proposal = state.get("raw_proposal")
        if raw_proposal:
            logger.info("Using raw_proposal as fallback for final_proposal")
            final_proposal = raw_proposal
        else:
            error_msg = ResearchPrompts.PERSISTENCE_NO_PROPOSAL_ERROR
            logger.error("No proposal to persist - neither final_proposal nor raw_proposal found")
            return {
                "error": error_msg,
                "validation_report": validation_report,
                "mcp_tools_available": available_tools,
                "proposal_path": None,
                "state_path": None,
            }

    try:
        # Ensure proposals directory exists
        proposals_dir = Path("proposals")
        proposals_dir.mkdir(exist_ok=True)

        # Create output paths
        proposal_output_path = proposals_dir / f"{slug}.json"
        state_output_path = proposals_dir / f"{slug}_state.json"

        # Save the proposal (could use filesystem MCP tool if available)
        if mcp_client.has_tool("filesystem"):
            # Future: Use MCP filesystem tool for saving
            # For now, fallback to direct filesystem access
            pass

        # Save the research proposal
        with open(proposal_output_path, "w", encoding="utf-8") as f:
            json.dump(final_proposal, f, indent=2, ensure_ascii=False)

        # Save the final state (excluding potentially large or redundant fields)
        state_to_save = dict(state)
        # Remove fields that might be very large or redundant
        fields_to_exclude = ["final_proposal"]  # Already saved separately
        filtered_state = {k: v for k, v in state_to_save.items() if k not in fields_to_exclude}

        with open(state_output_path, "w", encoding="utf-8") as f:
            json.dump(filtered_state, f, indent=2, ensure_ascii=False, default=str)

        logger.info("Successfully saved proposal to: %s", proposal_output_path)
        logger.info("Successfully saved final state to: %s", state_output_path)

        return {
            "proposal_path": str(proposal_output_path),
            "state_path": str(state_output_path),
            "validation_report": validation_report,
            "mcp_tools_available": available_tools,
            "error": None,
        }

    except (OSError, ValueError, KeyError) as e:
        error_msg = ResearchPrompts.PERSISTENCE_SAVE_ERROR_TEMPLATE.format(error=str(e))
        logger.error("Failed to persist proposal and state: %s", str(e))
        return {
            "error": error_msg,
            "validation_report": validation_report,
            "mcp_tools_available": available_tools,
            "proposal_path": None,
            "state_path": None,
        }
