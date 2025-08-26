"""
Prior art checking node using MCP (Model Context Protocol) for GitHub integration.
"""

from typing import Any, Dict

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.prior_art")


async def prior_art_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Check for prior art using MCP GitHub integration."""
    logger.info("Starting prior art node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="prior_art")
    available_tools = mcp_client.get_available_tool_names()

    idea = state["idea"]
    logger.info("Checking prior art for idea (length: %d characters)", len(idea))

    logger.debug("Prior art node has access to tools: %s", available_tools)
    print(f"Prior art node has access to tools: {available_tools}")

    # Generate search queries for prior art using centralized prompts
    prior_art_queries = ResearchPrompts.get_prior_art_queries(idea)
    logger.info("Generated %d prior art search queries", len(prior_art_queries))

    all_github_results = []

    # Search GitHub via MCP for each query if available
    if mcp_client.has_tool("github"):
        logger.debug("GitHub tool available, starting repository search")
        for i, query in enumerate(prior_art_queries[:3], 1):  # Limit searches
            logger.info(
                "Processing GitHub query %d/%d: %s",
                i,
                min(len(prior_art_queries), 3),
                query,
            )
            try:
                logger.debug("Executing GitHub search for query: %s", query)
                results = await mcp_client.github_search(query, max_results=5)
                all_github_results.extend(results)
                logger.info("GitHub search found %d results for query: %s", len(results), query)
                print(f"GitHub search found {len(results)} results for: {query}")
            except Exception as e:
                logger.warning("GitHub search failed for query '%s': %s", query, str(e))
                print(f"MCP GitHub search failed for query '{query}': {e}")
    else:
        logger.warning("GitHub tool not available for prior art search")
        print("GitHub tool not available for prior art search")

    # Close MCP client
    logger.debug("Closing MCP client")
    await mcp_client.close()

    # Analyze results to determine novelty using prompts
    verdict, reasoning = ResearchPrompts.get_prior_art_reasoning(len(all_github_results))
    logger.info(
        "Prior art analysis complete: verdict=%s, found=%d repositories",
        verdict,
        len(all_github_results),
    )

    prior_art_results = {
        "queries": prior_art_queries,
        "github_results": all_github_results,
        "verdict": verdict,
        "reasoning": reasoning,
        "total_found": len(all_github_results),
        "search_method": "mcp_github",
        "mcp_tools_used": available_tools,
    }

    # Check if we should restart planning due to prior art
    should_restart, restart_reason = ResearchPrompts.should_restart_for_prior_art(prior_art_results)

    if should_restart:
        logger.warning("Restart triggered due to prior art: %s", restart_reason)
        return {
            "prior_art_results": prior_art_results,
            "should_restart_planning": True,
            "restart_reason": restart_reason,
            "current_step": "plan",
        }

    logger.info("Prior art check passed, proceeding to criticism")
    return {
        "prior_art_results": prior_art_results,
        "should_restart_planning": False,
        "current_step": "criticism",
    }
