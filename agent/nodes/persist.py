"""
Persistence node for saving research proposals using MCP (Model Context Protocol).
"""

import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.persist")


def _compute_new_branch_name(branch_name: str) -> str:
    """Determine the new branch name based on the base branch."""
    uid = str(uuid.uuid4())
    if branch_name == "main" or re.match(r"portfolio.*", branch_name, re.IGNORECASE):
        return f"portfolio-{uid}"
    elif re.match(r"alpha.*", branch_name, re.IGNORECASE):
        return f"alpha-{uid}"
    else:
        return f"portfolio-{uid}"


def _generate_issue_markdown(
    proposal: Dict[str, Any],
    new_branch_name: str = "",
    image_name: str = "",
) -> str:
    """Generate GitHub issue markdown from research proposal."""
    proposal_json = json.dumps(proposal, indent=2, ensure_ascii=False)

    issue_template = f"""# Meta-Information
* Please move the research-proposal into the research/r/live directory before implementing it.
* The pull-request should be raised against the BASE BRANCH: `{new_branch_name}`

# Branch Information
BASE BRANCH: {new_branch_name}
ImageName: {image_name}


# Research Proposal Details
```
{proposal_json}
```
"""
    return issue_template


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
        # Get output directory from state, default to 'proposals'
        output_dir = state.get("output_dir", "proposals")
        output_path = Path(output_dir)

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        logger.info("Using output directory: %s", output_path)

        # Create output paths
        proposal_output_path = output_path / f"{slug}.json"
        state_output_path = output_path / f"{slug}_state.json"

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

        # Generate issue.md file for GitHub issue creation
        issue_output_path = output_path / "issue.md"
        branch_name = state.get("branch_name", "")
        image_name = state.get("image_name", "")
        new_branch_name = _compute_new_branch_name(branch_name)
        issue_content = _generate_issue_markdown(final_proposal, new_branch_name, image_name)
        with open(issue_output_path, "w", encoding="utf-8") as f:
            f.write(issue_content)

        logger.info("Successfully saved proposal to: %s", proposal_output_path)
        logger.info("Successfully saved final state to: %s", state_output_path)
        logger.info("Successfully saved GitHub issue template to: %s", issue_output_path)
        logger.info("Computed new branch name: %s (from base: %s)", new_branch_name, branch_name)

        return {
            "proposal_path": str(proposal_output_path),
            "state_path": str(state_output_path),
            "issue_path": str(issue_output_path),
            "new_branch_name": new_branch_name,
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
