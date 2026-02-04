"""
Web research node using LLM with web search tool calling for comprehensive research.
"""

from typing import Any, Dict, List

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient

# Get logger for this node
logger = get_logger("nodes.web_research")


async def web_research_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Conduct comprehensive web research using LLM with web search tool calling ability."""
    logger.info("Starting web research node execution")

    # Initialize LLM client for this node
    llm_client = LLMClient(config, node_name="web_research")
    logger.debug("Initialized LLM client: %s", llm_client.get_provider_info())

    # Create node-specific MCP client with LLM client
    mcp_client = MCPClient(config, llm_client, node_name="web_research")
    available_tools = mcp_client.get_available_tool_names()

    # Get context from state
    idea = state.get("idea", "")
    research_plan = state.get("research_plan", "")
    alpha_only = state.get("alpha_only", False)
    instruments = state.get("instruments", [])
    components_flag = state.get("components") or config.get_components_from_env()

    logger.info("Conducting component-specific research for idea: %s", idea)
    logger.debug("Web research node has access to tools: %s", available_tools)
    print(f"Web research node has access to tools: {available_tools}")

    # Determine which components to research
    from ..state import ResearchComponents

    # Component name mapping
    component_names = {
        ResearchComponents.UNIVERSE: "UNIVERSE",
        ResearchComponents.ALPHA: "ALPHA",
        ResearchComponents.PORTFOLIO: "PORTFOLIO",
        ResearchComponents.EXECUTION: "EXECUTION",
        ResearchComponents.RISK: "RISK",
    }

    # Determine active components
    active_components = []
    if alpha_only:
        # In alpha-only mode, focus on ALPHA and UNIVERSE
        active_components = ["ALPHA", "UNIVERSE"]
    elif components_flag:
        # Use specified components
        for component_flag, component_name in component_names.items():
            if components_flag & component_flag:
                active_components.append(component_name)
    else:
        # Default to all components
        active_components = list(component_names.values())

    logger.info("Researching components: %s", active_components)
    print(f"Researching components: {active_components}")

    # Conduct research for each component
    component_research_results = {}
    all_results = []  # Backward compatibility

    try:
        for component in active_components:
            logger.info("Starting research for component: %s", component)
            print(f"Starting research for component: {component}")

            # Get component-specific research (now returns a list of approaches)
            component_approaches = await _conduct_component_research(
                mcp_client, component, idea, research_plan, alpha_only, available_tools, instruments
            )

            if component_approaches:
                # Store component-specific results (list of approaches)
                component_research_results[component] = component_approaches

                # Also add to general results for backward compatibility
                all_results.extend(component_approaches)

                logger.info(
                    "Completed research for component %s with %d approaches", component, len(component_approaches)
                )
                print(f"Completed research for component {component} with {len(component_approaches)} approaches")
            else:
                logger.warning("Research for component %s returned empty results", component)
                # Add placeholder result
                error_result = {
                    "title": f"{component} Research Error: {idea}",
                    "content": ResearchPrompts.WEB_SEARCH_ERROR_CONTENT.format(query=f"{component} for {idea}"),
                    "url": "component_research_error",
                    "source": "error",
                    "research_type": "component_error",
                    "component": component,
                    "approach_number": 1,
                }
                component_research_results[component] = [error_result]
                all_results.append(error_result)

        if not all_results:
            logger.warning("All component research returned empty results")
            # Add a placeholder result so we don't fail completely
            all_results = [
                {
                    "title": f"Research Error: {idea}",
                    "content": ResearchPrompts.WEB_SEARCH_ERROR_CONTENT.format(query=idea),
                    "url": "research_error",
                    "source": "error",
                    "research_type": "error",
                    "approach_number": 1,
                }
            ]

    except (RuntimeError, ValueError, ConnectionError) as e:
        logger.error("Component-based web research failed: %s", str(e), exc_info=True)
        print(f"Component-based web research failed: {e}")
        # Add a placeholder result so we don't fail completely
        all_results = [
            {
                "title": f"Research Error: {idea}",
                "content": ResearchPrompts.WEB_SEARCH_ERROR_CONTENT.format(query=idea),
                "url": "research_error",
                "source": "error",
                "research_type": "error",
                "approach_number": 1,
            }
        ]

    # Close MCP client
    logger.debug("Closing MCP client")
    await mcp_client.close()

    logger.info("Web research completed with component-specific analysis")

    return {
        "web_search_results": all_results,  # Backward compatibility
        "component_research_results": component_research_results,  # New component-specific results
        "mcp_tools_used": available_tools,
        "current_step": "criticism",
    }


async def _conduct_component_research(
    mcp_client: MCPClient,
    component: str,
    idea: str,
    research_plan: str,
    alpha_only: bool,
    available_tools: list,
    instruments: list,
) -> List[Dict[str, Any]]:
    """Conduct component-specific research using LLM with web search tool calling via MCP client.

    Returns a list of research results, one for each approach found in the LLM response.
    Note: PORTFOLIO and EXECUTION components should return exactly one approach,
    while UNIVERSE, ALPHA, and RISK can return multiple approaches.
    """
    try:
        # Get component-specific prompts
        system_prompt = ResearchPrompts.COMPONENT_RESEARCH_SYSTEM_PROMPTS[component].format(
            available_tools=available_tools, 
            instruments=", ".join(instruments),
            alpha_only="Yes" if alpha_only else "No"
        )

        user_prompt = ResearchPrompts.COMPONENT_RESEARCH_USER_PROMPTS[component].format(
            idea=idea,
            research_plan=research_plan,
            alpha_only="Yes" if alpha_only else "No",
            instruments=", ".join(instruments),
        )

        # Create a comprehensive research query based on the prompts
        research_query = f"{system_prompt}\n\n{user_prompt}"

        logger.debug("Conducting component-specific research for %s using MCP web search", component)

        # Use MCP client's web_search with Tavily disabled to get LLM-based search
        search_results = await mcp_client.web_search(research_query, use_tavily=False)

        if search_results:
            # Extract the content from the first result (should be comprehensive)
            content = search_results[0].get("content", "")
            logger.info("MCP web search returned component-specific research content for %s", component)

            # Parse the content to extract approaches
            approaches = _parse_multiple_approaches(content, component, idea)

            # For PORTFOLIO and EXECUTION, ensure we only return one approach
            if component in ["PORTFOLIO", "EXECUTION"] and len(approaches) > 1:
                logger.info("Component %s returned %d approaches, using only the first one", component, len(approaches))
                approaches = [approaches[0]]  # Keep only the first approach
                # Update the approach to indicate it's the single comprehensive approach
                approaches[0]["title"] = f"{component} Research: {idea}"
                approaches[0]["approach_number"] = 1

            if approaches:
                return approaches
            else:
                # Fallback to single approach if parsing fails
                return [
                    {
                        "title": f"{component} Research: {idea}",
                        "content": content,
                        "url": "llm_component_research",
                        "source": "llm_with_web_tools",
                        "research_type": "component_specific",
                        "component": component,
                        "approach_number": 1,
                    }
                ]
        else:
            logger.warning("MCP web search returned no results for component %s", component)
            return []

    except (RuntimeError, ValueError, ConnectionError) as e:
        logger.error("Component research failed for %s: %s", component, str(e))
        raise


def _parse_multiple_approaches(content: str, component: str, idea: str) -> List[Dict[str, Any]]:
    """Parse LLM response content to extract multiple approaches.

    Looks for patterns like 'Approach 1:', 'Approach 2:', etc. and creates separate result objects.
    """
    import re

    approaches = []

    # Split content by approach markers
    approach_pattern = r"(?i)approach\s+(\d+):\s*"
    sections = re.split(approach_pattern, content)

    if len(sections) > 1:
        # First section might be introduction/overview
        overview = sections[0].strip()

        # Process approach sections (they come in pairs: number, content)
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                approach_num = sections[i]
                approach_content = sections[i + 1].strip()

                # Include overview in first approach if it exists and is substantial
                if int(approach_num) == 1 and overview and len(overview) > 100:
                    approach_content = f"{overview}\n\nApproach {approach_num}:\n{approach_content}"

                approaches.append(
                    {
                        "title": f"{component} Research Approach {approach_num}: {idea}",
                        "content": approach_content,
                        "url": "llm_component_research",
                        "source": "llm_with_web_tools",
                        "research_type": "component_specific",
                        "component": component,
                        "approach_number": int(approach_num),
                    }
                )
    else:
        # Try alternative parsing patterns
        # Look for numbered sections, bullet points, or other structure
        alt_patterns = [
            (r"(\d+)\.\s*([^\n]+)\n([^0-9]+?)(?=\d+\.|$)", "numbered_with_title"),  # 1. Title\nContent pattern
            (r"(?i)(\d+)\.\s*(.+?)(?=\n\d+\.|$)", "numbered_simple"),  # 1. Content pattern
            (r"(?i)###\s*([^#\n]+)\n([^#]+?)(?=###|$)", "markdown_header"),  # ### Header pattern
            (r"(?i)\*\*([^*]+)\*\*\s*\n([^*]+?)(?=\*\*|$)", "bold_header"),  # **Bold** pattern
        ]

        for pattern, pattern_type in alt_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            if len(matches) >= 2:  # Found multiple structured sections
                for i, match_groups in enumerate(matches, 1):
                    if pattern_type == "numbered_with_title":
                        # Three groups: number, title, content
                        number, title, content_part = match_groups
                        title_text = title.strip()
                        content_text = content_part.strip()
                    elif pattern_type in ["numbered_simple", "markdown_header", "bold_header"]:
                        # Two groups: title, content
                        title_part, content_part = match_groups
                        title_text = title_part.strip()
                        content_text = content_part.strip()

                    approaches.append(
                        {
                            "title": f"{component} Research Approach {i}: {title_text}",
                            "content": content_text,
                            "url": "llm_component_research",
                            "source": "llm_with_web_tools",
                            "research_type": "component_specific",
                            "component": component,
                            "approach_number": i,
                        }
                    )
                break

    # If no clear structure found, try to split by paragraphs and group
    if not approaches and len(content) > 500:  # Lower threshold
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

        # Group paragraphs into approaches (roughly equal chunks)
        if len(paragraphs) >= 3:  # Lower minimum for more flexible parsing
            chunk_size = max(1, len(paragraphs) // 3)  # Aim for 3-5 approaches

            for i in range(0, len(paragraphs), chunk_size):
                chunk = paragraphs[i : i + chunk_size]
                if chunk:
                    approach_num = (i // chunk_size) + 1
                    approaches.append(
                        {
                            "title": f"{component} Research Approach {approach_num}: {idea}",
                            "content": "\n\n".join(chunk),
                            "url": "llm_component_research",
                            "source": "llm_with_web_tools",
                            "research_type": "component_specific",
                            "component": component,
                            "approach_number": approach_num,
                        }
                    )

    return approaches


async def _conduct_comprehensive_research(mcp_client: MCPClient, system_prompt: str, user_prompt: str) -> str:
    """Conduct comprehensive research using LLM with web search tool calling via MCP client."""
    try:
        # Create a comprehensive research query based on the prompts
        research_query = f"{system_prompt}\n\n{user_prompt}"

        logger.debug("Conducting comprehensive research using MCP web search (no Tavily)")

        # Use MCP client's web_search with Tavily disabled to get LLM-based search
        search_results = await mcp_client.web_search(research_query, use_tavily=False)

        if search_results:
            # Extract the content from the first result (should be comprehensive)
            content = search_results[0].get("content", "")
            logger.info("MCP web search returned comprehensive research content")
            return content
        else:
            logger.warning("MCP web search returned no results")
            return ""

    except (RuntimeError, ValueError, ConnectionError) as e:
        logger.error("Comprehensive research failed: %s", str(e))
        raise
