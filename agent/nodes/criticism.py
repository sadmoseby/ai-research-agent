"""
Criticism node for evaluating research proposals using MCP (Model Context Protocol).
"""

from typing import Any, Dict

from ..config import Config, get_logger
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient, MCPToolError

# Get logger for this node
logger = get_logger("nodes.criticism")


async def _generate_criticism_analysis(
    idea: str,
    research_context: str,
    prior_art_summary: str,
    config: Config,
    available_tools: list,
) -> str:
    """Generate criticism analysis using OpenAI via the config."""
    logger.debug("Generating criticism analysis using OpenAI")
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=config.openai_api_key)

    # Format available tools for the LLM
    tools_formatted = ResearchPrompts.format_available_tools(available_tools)
    logger.debug("Formatted %d tools for LLM context", len(available_tools))

    system_prompt = ResearchPrompts.CRITICISM_SYSTEM_PROMPT.format(available_tools=tools_formatted)
    user_prompt = ResearchPrompts.CRITICISM_USER_PROMPT.format(
        idea=idea,
        research_context=research_context,
        prior_art_summary=prior_art_summary,
    )

    try:
        response = await client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1500,
        )

        return response.choices[0].message.content

    except Exception as e:
        raise MCPToolError(f"Criticism analysis failed: {str(e)}")


async def criticism_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Critically evaluate the research proposal concept using MCP."""
    logger.info("Starting criticism node execution")

    # Create node-specific MCP client
    mcp_client = MCPClient(config, node_name="criticism")
    available_tools = mcp_client.get_available_tool_names()

    logger.debug("Criticism node has access to tools: %s", available_tools)
    print(f"Criticism node has access to tools: {available_tools}")

    # Get context from previous steps
    idea = state["idea"]
    research_plan = state.get("research_plan", "")
    web_results = state.get("web_search_results", [])
    prior_art_results = state.get("prior_art_results", {})

    logger.info(
        "Analyzing research proposal: idea_length=%d, web_results=%d, prior_art_found=%d",
        len(idea),
        len(web_results),
        prior_art_results.get("total_found", 0),
    )

    # Format context for criticism using prompts
    research_context = ResearchPrompts.format_criticism_context(
        research_plan=research_plan, web_results=web_results, idea=idea
    )

    prior_art_summary = ResearchPrompts.format_prior_art_summary(prior_art_results)

    try:
        logger.debug("Generating criticism analysis")
        # Generate criticism analysis with tool awareness
        criticism_text = await _generate_criticism_analysis(
            idea=idea,
            research_context=research_context,
            prior_art_summary=prior_art_summary,
            config=config,
            available_tools=available_tools,
        )

        # If the LLM needs additional research during criticism, it can use MCP tools
        # This is where the LLM could potentially call tools if configured to do so
        # For now, we just inform it about available tools

        # Extract viability score from the criticism text
        viability_score = ResearchPrompts.extract_viability_score(criticism_text)

        # Structure the criticism results
        criticism_results = {
            "criticism_text": criticism_text,
            "idea": idea,
            "viability_score": viability_score,
            "research_quality": "analyzed",
            "risk_factors_identified": True,
            "recommendations_provided": True,
            "analysis_method": "mcp_criticism",
            "mcp_tools_available": available_tools,
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
            "research_quality": "limited",
            "risk_factors_identified": False,
            "recommendations_provided": True,
            "analysis_method": "fallback",
            "error": error_msg,
        }

        return {
            "criticism_results": criticism_results,
            "criticism_score": 50.0,
            "should_restart_planning": False,
            "current_step": "synthesize",
        }

    except Exception as e:
        error_msg = f"Criticism analysis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()

        # Minimal fallback
        criticism_results = {
            "criticism_text": f"Critical analysis unavailable for: {idea}",
            "idea": idea,
            "viability_score": 30.0,  # Low score due to inability to analyze
            "research_quality": "unavailable",
            "risk_factors_identified": False,
            "recommendations_provided": False,
            "analysis_method": "error",
            "error": error_msg,
        }

        return {
            "criticism_results": criticism_results,
            "criticism_score": 30.0,
            "should_restart_planning": False,
            "current_step": "synthesize",
        }
