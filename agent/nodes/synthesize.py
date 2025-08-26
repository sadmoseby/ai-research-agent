"""
Synthesis node for generating research proposals using MCP (Model Context Protocol).
"""

import json
from typing import Any, Dict

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient, MCPToolError

# Get logger for this node
logger = get_logger("nodes.synthesize")


async def synthesize_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Synthesize research findings into a structured proposal using MCP."""
    logger.info("Starting synthesis node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="synthesize")
    available_tools = mcp_client.get_available_tool_names()

    print(f"Synthesis node has access to tools: {available_tools}")

    # Get the schema for structured output
    schema = config.get_schema()

    # Prepare context from research
    idea = state["idea"]
    alpha_only = state.get("alpha_only", False)
    research_plan = state.get("research_plan", "")
    web_results = state.get("web_search_results", [])
    prior_art = state.get("prior_art_results", {})
    criticism_results = state.get("criticism_results", {})
    validation_errors = state.get("validation_errors", [])

    # Build research context using prompts
    web_results_formatted = ResearchPrompts.format_web_results(web_results, limit=5)
    criticism_summary = ResearchPrompts.format_criticism_summary(criticism_results)

    research_context = ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE.format(
        research_plan=research_plan,
        web_results=web_results_formatted,
        verdict=prior_art.get("verdict", "unknown"),
        reasoning=prior_art.get("reasoning", "No analysis available"),
        total_found=prior_art.get("total_found", 0),
        search_method=prior_art.get("search_method", "unknown"),
        criticism_summary=criticism_summary,
    )

    # Add validation errors if this is a repair attempt
    repair_context = ResearchPrompts.format_validation_errors(validation_errors)

    # Format available tools for the LLM
    tools_formatted = ResearchPrompts.format_available_tools(available_tools)

    # Create system prompt using centralized prompts
    alpha_mode_note = ResearchPrompts.get_alpha_mode_note(alpha_only)
    system_prompt = ResearchPrompts.SYNTHESIS_SYSTEM_PROMPT.format(
        alpha_mode_note=alpha_mode_note,
        repair_context=repair_context,
        available_tools=tools_formatted,
    )

    # Create user prompt using centralized prompts
    user_prompt = ResearchPrompts.SYNTHESIS_USER_PROMPT.format(
        idea=idea, research_context=research_context, alpha_only=alpha_only
    )

    try:
        # Use MCP for structured proposal generation
        proposal_json = await mcp_client.generate_proposal(
            system_prompt=system_prompt, user_prompt=user_prompt, schema=schema
        )

        # Add metadata from research
        if "misc" not in proposal_json:
            proposal_json["misc"] = {}

        proposal_json["misc"]["prior_art"] = prior_art
        proposal_json["misc"]["research_sources"] = len(web_results)
        proposal_json["misc"]["generated_by"] = "lean-research-agent-mcp"
        proposal_json["misc"]["tool_protocol"] = "mcp"
        proposal_json["misc"]["mcp_tools_available"] = available_tools

        # Close MCP client
        await mcp_client.close()

        return {"raw_proposal": proposal_json, "current_step": "validate"}

    except MCPToolError as e:
        error_msg = f"MCP synthesis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()
        return {"error": error_msg, "current_step": "validate"}
    except Exception as e:
        error_msg = f"Synthesis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()
        return {"error": error_msg, "current_step": "validate"}
