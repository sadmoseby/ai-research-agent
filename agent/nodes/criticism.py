"""
Criticism node for evaluating research proposals using MCP (Model Context Protocol).
"""

from typing import Any, Dict

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient, MCPToolError

# Get logger for this node
logger = get_logger("nodes.criticism")


async def _generate_criticism_analysis(
    idea: str,
    instruments: list,
    research_context: str,
    llm_client: LLMClient,
    available_tools: list,
    use_component_specific: bool = False,
) -> str:
    """Generate criticism analysis using the LLM client."""
    logger.debug("Generating criticism analysis using LLM client (component-specific: %s)", use_component_specific)

    # Format available tools for the LLM
    tools_formatted = ResearchPrompts.format_available_tools(available_tools)
    logger.debug("Formatted %d tools for LLM context", len(available_tools))

    # Choose appropriate prompts based on whether we have component-specific research
    if use_component_specific:
        system_prompt = ResearchPrompts.COMPONENT_CRITICISM_SYSTEM_PROMPT.format(
            available_tools=tools_formatted, instruments=", ".join(instruments)
        )
        user_prompt = ResearchPrompts.COMPONENT_CRITICISM_USER_PROMPT.format(
            idea=idea,
            instruments=", ".join(instruments),
            component_research_context=research_context,
        )
    else:
        system_prompt = ResearchPrompts.CRITICISM_SYSTEM_PROMPT.format(
            available_tools=tools_formatted, instruments=", ".join(instruments)
        )
        user_prompt = ResearchPrompts.CRITICISM_USER_PROMPT.format(
            idea=idea,
            instruments=", ".join(instruments),
            research_context=research_context,
        )

    try:
        response = await llm_client.chat_completion(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2500,  # Increased for component-specific analysis
        )

        return response

    except Exception as e:
        raise MCPToolError(f"Criticism analysis failed: {str(e)}") from e


async def criticism_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Critically evaluate the research proposal concept using MCP."""
    logger.info("Starting criticism node execution")

    # Initialize LLM client for this node
    llm_client = LLMClient(config, node_name="criticism")
    logger.debug("Initialized LLM client: %s", llm_client.get_provider_info())

    # Create node-specific MCP client
    mcp_client = MCPClient(config, llm_client, node_name="criticism")
    available_tools = mcp_client.get_available_tool_names()

    logger.debug("Criticism node has access to tools: %s", available_tools)
    print(f"Criticism node has access to tools: {available_tools}")

    # Get context from previous steps
    idea = state["idea"]
    instruments = state.get("instruments", [])
    research_plan = state.get("research_plan", "")
    # Include component scope note if available
    components_flag = state.get("components") or config.get_components_from_config()
    component_names = []
    try:
        from ..state import ResearchComponents as _RC

        if components_flag and isinstance(components_flag, (int, _RC)):
            if components_flag & _RC.UNIVERSE:
                component_names.append("UNIVERSE")
            if components_flag & _RC.ALPHA:
                component_names.append("ALPHA")
            if components_flag & _RC.PORTFOLIO:
                component_names.append("PORTFOLIO")
            if components_flag & _RC.EXECUTION:
                component_names.append("EXECUTION")
            if components_flag & _RC.RISK:
                component_names.append("RISK")
    except (AttributeError, TypeError, ImportError):
        pass
    if component_names:
        research_plan = research_plan + f"\n\nComponent Scope: {', '.join(component_names)}\n"

    web_results = state.get("web_search_results", [])
    component_research_results = state.get("component_research_results", {})

    logger.info(
        "Analyzing research proposal: idea_length=%d, web_results=%d, component_results=%d",
        len(idea),
        len(web_results),
        len(component_research_results),
    )

    # Determine if we should use component-specific criticism
    use_component_specific = bool(component_research_results)

    # Format context for criticism using prompts
    if use_component_specific:
        logger.info("Using component-specific criticism analysis")
        research_context = ResearchPrompts.format_component_criticism_context(
            research_plan=research_plan,
            component_research_results=component_research_results,
            web_results=web_results,
            idea=idea,
        )
    else:
        logger.info("Using general criticism analysis")
        research_context = ResearchPrompts.format_criticism_context(
            research_plan=research_plan, web_results=web_results, idea=idea
        )

    try:
        logger.debug("Generating criticism analysis")
        # Generate criticism analysis with tool awareness and component-specific handling
        criticism_text = await _generate_criticism_analysis(
            idea=idea,
            instruments=instruments,
            research_context=research_context,
            llm_client=llm_client,
            available_tools=available_tools,
            use_component_specific=use_component_specific,
        )

        # If the LLM needs additional research during criticism, it can use MCP tools
        # This is where the LLM could potentially call tools if configured to do so
        # For now, we just inform it about available tools

        # Extract viability score from the criticism text
        viability_score = ResearchPrompts.extract_viability_score(criticism_text)

        # Extract component scores if using component-specific analysis
        component_scores = {}
        if use_component_specific:
            component_scores = ResearchPrompts.extract_component_scores(criticism_text)
            logger.info("Extracted component scores: %s", component_scores)

        # Structure the criticism results
        criticism_results = {
            "criticism_text": criticism_text,
            "idea": idea,
            "viability_score": viability_score,
            "component_scores": component_scores,  # New field for component-specific scores
            "research_quality": "analyzed",
            "risk_factors_identified": True,
            "recommendations_provided": True,
            "analysis_method": "mcp_component_criticism" if use_component_specific else "mcp_criticism",
            "mcp_tools_available": available_tools,
            "components_analyzed": list(component_research_results.keys()) if use_component_specific else [],
        }

        # Check if we should restart planning due to low score
        planning_iteration = state.get("planning_iteration", 0)
        should_restart, restart_reason = ResearchPrompts.should_restart_for_criticism(
            viability_score, planning_iteration
        )

        # Close MCP client
        await mcp_client.close()

        if should_restart:
            return {
                "criticism_results": criticism_results,
                "criticism_score": viability_score,
                "should_restart_planning": True,
                "restart_reason": restart_reason,
                "current_step": "plan",
            }

        return {
            "criticism_results": criticism_results,
            "criticism_score": viability_score,
            "should_restart_planning": False,
            "current_step": "synthesize",
        }

    except MCPToolError as e:
        error_msg = f"MCP criticism analysis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()

        # Provide fallback criticism
        fallback_criticism = f"""
Fallback Critical Analysis for: {idea}

Due to system limitations, a comprehensive criticism analysis could not be performed.

General Considerations:
- Ensure robust backtesting across multiple market regimes
- Consider transaction costs and market impact
- Validate data quality and availability
- Plan for risk management and position sizing
- Address potential overfitting concerns
- Consider regulatory and compliance requirements

Recommendation: Proceed with caution and conduct thorough testing.
"""

        criticism_results = {
            "criticism_text": fallback_criticism,
            "idea": idea,
            "viability_score": 50.0,  # Neutral score for fallback
            "component_scores": {},  # Empty for fallback
            "research_quality": "limited",
            "risk_factors_identified": False,
            "recommendations_provided": True,
            "analysis_method": "fallback",
            "error": error_msg,
            "components_analyzed": [],
        }

        return {
            "criticism_results": criticism_results,
            "criticism_score": 50.0,
            "should_restart_planning": False,
            "current_step": "synthesize",
        }

    except (RuntimeError, ValueError, TypeError) as e:
        error_msg = f"Criticism analysis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()

        # Minimal fallback
        criticism_results = {
            "criticism_text": f"Critical analysis unavailable for: {idea}",
            "idea": idea,
            "viability_score": 30.0,  # Low score due to inability to analyze
            "component_scores": {},  # Empty for error case
            "research_quality": "unavailable",
            "risk_factors_identified": False,
            "recommendations_provided": False,
            "analysis_method": "error",
            "error": error_msg,
            "components_analyzed": [],
        }

        return {
            "criticism_results": criticism_results,
            "criticism_score": 30.0,
            "should_restart_planning": False,
            "current_step": "synthesize",
        }
