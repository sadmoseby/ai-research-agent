"""
Persistence node for saving research proposals using MCP (Model Context Protocol).
"""

import json
from pathlib import Path
from typing import Any, Dict

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.persist")


async def persist_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Persist the research proposal to various outputs using MCP."""
    logger.info("Starting persistence node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="persist")
    available_tools = mcp_client.get_available_tool_names()

    print(f"Persistence node has access to tools: {available_tools}")

    final_proposal = state.get("final_proposal")
    slug = state.get("slug", "research_proposal")
    validation_report = state.get("validation_report", "")

    if not final_proposal:
        error_msg = ResearchPrompts.PERSISTENCE_NO_PROPOSAL_ERROR
        return {
            "error": error_msg,
            "validation_report": validation_report,
            "mcp_tools_available": available_tools,
        }

    try:
        # Ensure proposals directory exists
        proposals_dir = Path("proposals")
        proposals_dir.mkdir(exist_ok=True)

        # Create output path
        output_path = proposals_dir / f"{slug}.json"

        # Save the proposal (could use filesystem MCP tool if available)
        if mcp_client.has_tool("filesystem"):
            # Future: Use MCP filesystem tool for saving
            # For now, fallback to direct filesystem access
            pass

        # Save the proposal
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(final_proposal, f, indent=2, ensure_ascii=False)

        return {
            "proposal_path": str(output_path),
            "validation_report": validation_report,
            "mcp_tools_available": available_tools,
            "error": None,
        }

    except (OSError, ValueError, KeyError) as e:
        error_msg = ResearchPrompts.PERSISTENCE_SAVE_ERROR_TEMPLATE.format(error=str(e))
        return {
            "error": error_msg,
            "validation_report": validation_report,
            "mcp_tools_available": available_tools,
        }
