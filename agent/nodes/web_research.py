"""
Web research node using MCP (Model Context Protocol) for tool integrations.
"""

import json
from typing import Any, Dict, List

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.web_research")


async def web_research_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Conduct web research using MCP tool integrations."""
    logger.info("Starting web research node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="web_research")
    available_tools = mcp_client.get_available_tool_names()

    search_queries = state.get("search_queries", [])
    logger.info("Received %d search queries to process", len(search_queries))

    # Check what tools are available and plan accordingly
    logger.debug("Web research node has access to tools: %s", available_tools)
    print(f"Web research node has access to tools: {available_tools}")

    all_results = []

    # Use available MCP tools for search
    for i, query in enumerate(search_queries[:3], 1):  # Limit to 3 queries to avoid hitting limits
        logger.info("Processing search query %d/%d: %s", i, min(len(search_queries), 3), query)
        try:
            results_found = False

            # Try web search first if available
            if mcp_client.has_tool("web_search"):
                try:
                    logger.debug("Attempting web search for query: %s", query)
                    openai_results = await mcp_client.web_search(query)
                    all_results.extend(openai_results)
                    results_found = True
                    logger.info(
                        "Web search found %d results for query: %s",
                        len(openai_results),
                        query,
                    )
                    print(f"OpenAI web search found {len(openai_results)} results for: {query}")
                except Exception as e:
                    logger.warning("Web search failed for query '%s': %s", query, str(e))
                    print(f"OpenAI web search failed for query '{query}': {e}")

            # Fallback to Tavily if available and no results yet
            if mcp_client.has_tool("tavily") and not results_found:
                try:
                    logger.debug("Attempting Tavily search for query: %s", query)
                    tavily_results = await mcp_client.tavily_search(query)
                    all_results.extend(tavily_results)
                    results_found = True
                    logger.info(
                        "Tavily search found %d results for query: %s",
                        len(tavily_results),
                        query,
                    )
                    print(f"Tavily search found {len(tavily_results)} results for: {query}")
                except Exception as e:
                    logger.warning("Tavily search failed for query '%s': %s", query, str(e))
                    print(f"Tavily search failed for query '{query}': {e}")

            # If no tools worked, add error result
            if not results_found:
                logger.warning("No search tools worked for query: %s", query)
                all_results.append(
                    {
                        "query": query,
                        "title": ResearchPrompts.WEB_SEARCH_ERROR_TITLE.format(query=query),
                        "content": ResearchPrompts.WEB_SEARCH_ERROR_CONTENT.format(query=query),
                        "url": "mcp_error",
                        "source": "error",
                    }
                )

        except Exception as e:
            logger.error("MCP web search failed for query '%s': %s", query, str(e), exc_info=True)
            print(f"MCP web search failed for query '{query}': {e}")
            # Add a placeholder result so we don't fail completely
            all_results.append(
                {
                    "query": query,
                    "title": ResearchPrompts.WEB_SEARCH_ERROR_TITLE.format(query=query),
                    "content": ResearchPrompts.WEB_SEARCH_ERROR_CONTENT.format(query=query),
                    "url": "mcp_error",
                    "source": "error",
                }
            )

    # Close MCP client
    logger.debug("Closing MCP client")
    await mcp_client.close()

    logger.info("Web research completed with %d total results", len(all_results))

    return {
        "web_search_results": all_results,
        "mcp_tools_used": available_tools,
        "current_step": "prior_art",
    }
