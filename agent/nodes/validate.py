"""
Validation node for checking research proposal completeness and quality.
"""

from typing import Any, Dict

import jsonschema

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.validate")


def validate_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Validate the research proposal against the schema."""
    logger.info("Starting validation node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="validate")
    available_tools = mcp_client.get_available_tool_names()

    print(f"Validation node has access to tools: {available_tools}")

    raw_proposal = state.get("raw_proposal")
    repair_attempts = state.get("repair_attempts", 0)

    if not raw_proposal:
        return {
            "validation_errors": [ResearchPrompts.VALIDATION_NO_PROPOSAL_ERROR],
            "validation_report": ResearchPrompts.VALIDATION_NO_PROPOSAL_REPORT,
            "mcp_tools_available": available_tools,
            "current_step": "persist",
        }

    try:
        # Load schema (could use filesystem tool if available)
        schema = config.get_schema()

        # Validate against schema
        jsonschema.validate(raw_proposal, schema)

        # Validation passed
        return {
            "final_proposal": raw_proposal,
            "validation_errors": None,
            "validation_report": ResearchPrompts.VALIDATION_SUCCESS_REPORT,
            "mcp_tools_available": available_tools,
            "current_step": "persist",
        }

    except jsonschema.ValidationError as e:
        # Collect validation errors using prompts
        errors = [
            ResearchPrompts.VALIDATION_ERROR_TEMPLATE.format(
                path=".".join(str(p) for p in e.absolute_path), message=e.message
            )
        ]

        # Try to collect additional errors
        try:
            validator = jsonschema.Draft202012Validator(schema)
            all_errors = list(validator.iter_errors(raw_proposal))
            errors = [
                ResearchPrompts.VALIDATION_PATH_ERROR_TEMPLATE.format(
                    path=".".join(str(p) for p in err.absolute_path),
                    message=err.message,
                )
                for err in all_errors[:5]
            ]  # Limit to 5 errors
        except (AttributeError, TypeError):
            pass  # Use the single error from above

        # Check if we should retry
        if repair_attempts < 1:
            return {
                "validation_errors": errors,
                "repair_attempts": repair_attempts + 1,
                "validation_report": ResearchPrompts.VALIDATION_FAILED_REPAIR_REPORT.format(count=len(errors)),
                "current_step": "synthesize",  # Will trigger retry
            }
        else:
            # Max retries reached, persist with errors
            return {
                "validation_errors": errors,
                "final_proposal": raw_proposal,  # Persist invalid proposal with errors noted
                "validation_report": ResearchPrompts.VALIDATION_FAILED_FINAL_REPORT.format(count=len(errors)),
                "current_step": "persist",
            }

    except (ValueError, KeyError) as e:
        error_msg = ResearchPrompts.VALIDATION_SYSTEM_ERROR_TEMPLATE.format(error=str(e))
        return {
            "validation_errors": [error_msg],
            "validation_report": f"❌ {error_msg}",
            "current_step": "persist",
        }
