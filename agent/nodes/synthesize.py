"""
Synthesis node for generating research proposals using MCP (Model Context Protocol).
"""

import json
from typing import Any, Dict, List, Optional

from ..config import Config, get_logger
from ..llm_client import LLMClient
from ..prompts import ResearchPrompts
from ..state import ResearchState
from ..tools.mcp_client import MCPClient, MCPToolError

# Get logger for this node
logger = get_logger("nodes.synthesize")


async def synthesize_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Synthesize research findings into a structured proposal using MCP."""
    logger.info("Starting synthesis node execution")

    # Initialize LLM client for this node
    llm_client = LLMClient(config, node_name="synthesize")
    logger.debug("Initialized LLM client: %s", llm_client.get_provider_info())

    # Create node-specific MCP client
    mcp_client = MCPClient(config, llm_client, node_name="synthesize")
    available_tools = mcp_client.get_available_tool_names()

    print(f"Synthesis node has access to tools: {available_tools}")

    # Get the schema for structured output
    schema = config.get_schema()

    # Prepare context from research
    idea = state["idea"]
    instruments = state.get("instruments", [])
    alpha_only = state.get("alpha_only", False)
    research_plan = state.get("research_plan", "")
    web_results = state.get("web_search_results", [])
    component_search_results = state.get("component_research_results", {})
    prior_art = state.get("prior_art_results", {})
    validation_errors = state.get("validation_errors", [])

    # Prefer component-specific research over general web results
    if component_search_results:
        # Build research context using component-specific results
        research_context_data = ResearchPrompts.format_component_research_context(
            research_plan, component_search_results, web_results, idea
        )
    else:
        # Fallback to general web results
        web_results_formatted = ResearchPrompts.format_web_results(web_results, limit=5)
        research_context_data = web_results_formatted

    # Component scope note for context (optional)
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

    research_context = ResearchPrompts.RESEARCH_CONTEXT_TEMPLATE.format(
        research_plan=research_plan,
        web_results=research_context_data,
        verdict=prior_art.get("verdict", "unknown"),
        reasoning=prior_art.get("reasoning", "No analysis available"),
        total_found=prior_art.get("total_found", 0),
        search_method=prior_art.get("search_method", "unknown"),
    )

    # Format available tools for the LLM
    tools_formatted = ResearchPrompts.format_available_tools(available_tools)

    # Check if we should use component-by-component synthesis
    # When unified_synthesis is False (default), use component-by-component if we have component results
    use_component_synthesis = not config.unified_synthesis and component_search_results and not alpha_only

    if use_component_synthesis:
        print("Using component-by-component synthesis approach")
        # Generate proposal using component-by-component approach
        proposal_json = await _generate_component_by_component_proposal(
            llm_client=llm_client,
            schema=schema,
            idea=idea,
            instruments=instruments,
            research_plan=research_plan,
            component_search_results=component_search_results,
            prior_art=prior_art,
            available_tools=tools_formatted,
            validation_errors=validation_errors,
        )
    else:
        print("Using unified synthesis approach")
        # Generate initial proposal using unified function
        proposal_json = await _generate_proposal(
            llm_client=llm_client,
            schema=schema,
            idea=idea,
            instruments=instruments,
            research_context=research_context,
            alpha_only=alpha_only,
            available_tools=tools_formatted,
            component_names=", ".join(component_names) if component_names else "All components",
            validation_errors=validation_errors,
            original_proposal="",  # No original proposal for initial synthesis
        )

    if not proposal_json:
        error_msg = "Failed to generate initial proposal"
        print(error_msg)
        await mcp_client.close()
        return {"error": error_msg, "current_step": "persist"}

    # Add metadata from research (only in non-alpha-only mode)
    if not alpha_only:
        if "misc" not in proposal_json:
            proposal_json["misc"] = {}

        proposal_json["misc"]["prior_art"] = prior_art
        proposal_json["misc"]["research_sources"] = len(web_results)
        proposal_json["misc"]["generated_by"] = "lean-research-agent-mcp"
        proposal_json["misc"]["tool_protocol"] = "mcp"
        proposal_json["misc"]["mcp_tools_available"] = available_tools

    # Always add instruments field regardless of mode
    proposal_json["instruments"] = instruments

    try:
        # Unified validation and repair loop
        max_repair_attempts = 3
        current_repair_attempts = state.get("repair_attempts", 0)
        current_proposal = proposal_json

        for attempt in range(max_repair_attempts + 1):
            logger.info("Validating proposal (attempt %d/%d)", attempt + 1, max_repair_attempts + 1)
            validation_result = await mcp_client.validate_proposal(current_proposal)

            if validation_result["is_valid"]:
                logger.info("Proposal validation successful")
                await mcp_client.close()
                return {
                    "final_proposal": current_proposal,
                    "validation_errors": None,
                    "validation_report": validation_result["report"],
                    "repair_attempts": current_repair_attempts + attempt,
                    "current_step": "persist",
                }
            elif attempt < max_repair_attempts:
                # Attempt repair
                logger.info("Validation failed, attempting repair %d/%d", attempt + 1, max_repair_attempts)

                repaired_proposal = await _generate_proposal(
                    llm_client=llm_client,
                    schema=schema,
                    idea=idea,
                    instruments=instruments,
                    research_context=research_context,
                    alpha_only=alpha_only,
                    available_tools=tools_formatted,
                    component_names=", ".join(component_names) if component_names else "All components",
                    validation_errors=validation_result["errors"],
                    original_proposal=json.dumps(current_proposal, indent=2),
                )

                if repaired_proposal:
                    current_proposal = repaired_proposal
                else:
                    # Repair failed, return with errors
                    logger.info("Repair attempt failed, will retry synthesis")
                    await mcp_client.close()
                    return {
                        "validation_errors": validation_result["errors"],
                        "repair_attempts": current_repair_attempts + attempt + 1,
                        "validation_report": validation_result["report"],
                        "current_step": "synthesize",
                    }
            else:
                # Max repairs reached
                logger.info("Max repair attempts reached, persisting with errors")
                await mcp_client.close()
                return {
                    "final_proposal": current_proposal,
                    "validation_errors": validation_result["errors"],
                    "validation_report": f"❌ Max repairs reached. {validation_result['report']}",
                    "repair_attempts": current_repair_attempts + max_repair_attempts,
                    "current_step": "persist",
                }

    except MCPToolError as e:
        error_msg = f"MCP synthesis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()
        return {"error": error_msg, "current_step": "persist"}
    except (RuntimeError, ValueError, TypeError) as e:
        error_msg = f"Synthesis failed: {str(e)}"
        print(error_msg)
        await mcp_client.close()
        return {"error": error_msg, "current_step": "persist"}


async def _generate_proposal(
    llm_client: LLMClient,
    schema: Dict[str, Any],
    idea: str,
    instruments: list,
    research_context: str,
    alpha_only: bool,
    available_tools: str,
    component_names: str,
    validation_errors: List[str] = None,
    original_proposal: str = "",
) -> Optional[Dict[str, Any]]:
    """Unified function to generate or repair a proposal."""
    # Determine if this is a repair or new synthesis
    is_repair = bool(validation_errors)

    # Create contexts using helper methods
    task_context = ResearchPrompts.get_task_context(is_repair, original_proposal)
    validation_context = ResearchPrompts.get_validation_context(validation_errors or [])

    # Create prompts using unified templates
    schema_json_str = json.dumps(schema, indent=2)
    system_prompt = ResearchPrompts.SYNTHESIS_SYSTEM_PROMPT.format(
        json_schema=schema_json_str,
        instruments=", ".join(instruments),
    )

    user_prompt = ResearchPrompts.SYNTHESIS_USER_PROMPT.format(
        task_context=task_context,
        idea=idea,
        instruments=", ".join(instruments),
        research_context=research_context,
        alpha_only=alpha_only,
        available_tools=available_tools,
        component_names=component_names,
        validation_context=validation_context,
    )

    try:
        # Generate proposal using unified approach
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        # Schema is provided in system prompt, but json_completion requires minimal schema
        minimal_schema = {"type": "object", "additionalProperties": True}
        proposal_json = await llm_client.json_completion(
            messages=messages,
            json_schema=minimal_schema,
        )

        # Handle alpha-only mode restrictions
        if alpha_only:
            allowed_fields = {"alphas", "universe", "alpha-only", "instruments"}
            fields_to_remove = [field for field in proposal_json.keys() if field not in allowed_fields]
            for field in fields_to_remove:
                logger.info("Removing disallowed field '%s' from alpha-only proposal", field)
                del proposal_json[field]
            proposal_json["alpha-only"] = True

            # Ensure universe is in "existing" format for alpha-only mode
            if "universe" in proposal_json:
                universe = proposal_json["universe"]
                # If universe has "new" instead of "existing", transform it
                if "new" in universe and "existing" not in universe:
                    logger.info("Converting universe 'new' to 'existing' format for alpha-only mode")
                    new_universe = universe["new"]
                    if new_universe and len(new_universe) > 0:
                        first_universe = new_universe[0]
                        # Transform to existing format with static stock selection
                        universe["existing"] = [
                            {
                                "symbol": _extract_or_default_symbol(first_universe, instruments),
                                "name": _extract_or_default_name(first_universe, instruments),
                                "description": _extract_or_default_description(first_universe, instruments),
                                "assetClass": _extract_or_default_asset_class(instruments),
                            }
                        ]
                    del universe["new"]

        return proposal_json

    except (RuntimeError, ValueError, TypeError) as e:
        error_type = "repair" if is_repair else "synthesis"
        logger.error("Failed to %s proposal: %s", error_type, str(e), exc_info=True)
        print(f"ERROR: Failed to {error_type} proposal: {str(e)}")
        return None


async def _generate_component_by_component_proposal(
    llm_client: LLMClient,
    schema: Dict[str, Any],
    idea: str,
    instruments: list,
    research_plan: str,
    component_search_results: Dict[str, List[Dict[str, Any]]],
    prior_art: Dict[str, Any],
    available_tools: str,
    validation_errors: List[str] = None,
) -> Optional[Dict[str, Any]]:
    """Generate a proposal by creating each component separately and then combining them."""
    logger.info("Starting component-by-component proposal generation")

    # Component mapping for the schema
    component_mapping = {
        "ALPHA": "alphas",
        "UNIVERSE": "universe",
        "PORTFOLIO": "portfolio",
        "EXECUTION": "execution",
        "RISK": "risk",
    }

    final_proposal = {}

    # Process each component that has research results
    for component_name, research_results in component_search_results.items():
        if component_name in component_mapping:
            schema_key = component_mapping[component_name]
            logger.info("Generating %s component", schema_key)

            # Generate component-specific content
            component_data = await _generate_single_component(
                llm_client=llm_client,
                component_name=component_name,
                schema_key=schema_key,
                idea=idea,
                research_plan=research_plan,
                component_research=research_results,
                available_tools=available_tools,
            )

            if component_data:
                final_proposal[schema_key] = component_data
                logger.info("Successfully generated %s component", schema_key)
            else:
                logger.warning("Failed to generate %s component", schema_key)

    # Add metadata
    final_proposal["misc"] = {
        "prior_art": prior_art,
        "research_sources": sum(len(results) for results in component_search_results.values()),
        "generated_by": "lean-research-agent-mcp-component-synthesis",
        "tool_protocol": "mcp",
        "synthesis_method": "component_by_component",
    }

    logger.info("Component-by-component synthesis completed with %d components", len(final_proposal) - 1)
    return final_proposal


async def _generate_single_component(
    llm_client: LLMClient,
    component_name: str,
    schema_key: str,
    idea: str,
    research_plan: str,
    component_research: List[Dict[str, Any]],
    available_tools: str,
) -> Optional[Dict[str, Any]]:
    """Generate a single component of the research proposal."""

    # Format research context for this component
    research_context = f"Research Plan:\n{research_plan}\n\n"
    research_context += f"=== {component_name} RESEARCH FINDINGS ===\n"

    for i, result in enumerate(component_research, 1):
        title = result.get("title", "Untitled")
        content = result.get("content", "")
        approach_num = result.get("approach_number", i)

        research_context += f"Approach {approach_num}: {title}\n"
        research_context += f"Content: {content}\n\n"

    # Create component-specific system prompt
    system_prompt = f"""You are an expert quantitative finance researcher specializing in
{component_name.lower()} components for algorithmic trading strategies.

Your task is to generate a structured {schema_key} component based on the provided research
findings.

The output must be a JSON object that follows this structure for the {schema_key} component:
{{
  "new": [
    {{
      "name": "string",
      "componentId": "string",
      "version": "string",
      "title": "string",
      "description": "string",
      "text": "string",
      "params": [
        {{
          "name": "string",
          "type": "string|int|float|bool|enum|datetime|symbol",
          "value": "appropriate_default_value",
          "minimum": "number_for_tuning",
          "maximum": "number_for_tuning",
          "tuning": {{"distribution": "uniform|step|categorical|log"}}
        }}
      ]
    }}
  ]
}}

Important guidelines:
- The "text" field should contain plain-language descriptions only (no code)
- Create realistic parameter definitions for tuning/optimization
- Base all content on the research findings provided
- Ensure the component aligns with the overall trading strategy idea"""

    user_prompt = f"""Generate a {schema_key} component for this trading strategy idea: {idea}

{research_context}

Available tools: {available_tools}

Create a comprehensive {component_name.lower()} component that:
1. Incorporates insights from the research findings
2. Defines appropriate parameters for optimization
3. Provides clear descriptions in the text field
4. Follows the JSON schema requirements

Respond with valid JSON only."""

    try:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        # Use minimal schema for JSON completion
        minimal_schema = {"type": "object", "additionalProperties": True}
        component_result = await llm_client.json_completion(
            messages=messages,
            json_schema=minimal_schema,
        )

        logger.debug("Generated %s component: %s", schema_key, str(component_result)[:200])
        return component_result

    except (RuntimeError, ValueError, TypeError) as e:
        logger.error("Failed to generate %s component: %s", schema_key, str(e))
        return None


def _extract_or_default_symbol(universe_component: Dict[str, Any], instruments: List[str]) -> str:
    """Extract symbol from universe component or provide default based on instruments."""
    # Check if the component has a symbol or ticker mentioned
    text_content = str(universe_component.get("text", "")) + str(universe_component.get("description", ""))

    # Common ETF patterns
    etf_patterns = ["SPY", "QQQ", "VTI", "IWM", "EFA", "EEM", "TLT", "GLD", "BTC-USD", "ETH-USD"]
    for pattern in etf_patterns:
        if pattern in text_content.upper():
            return pattern

    # Default based on instruments
    if "stocks" in instruments:
        return "SPY"  # S&P 500 ETF
    elif "crypto" in instruments:
        return "BTC-USD"  # Bitcoin
    elif "futures" in instruments:
        return "ES"  # E-mini S&P 500 futures
    elif "forex" in instruments:
        return "EUR/USD"  # Euro/Dollar
    elif "options" in instruments:
        return "SPY"  # SPY options
    else:
        return "SPY"  # Default fallback


def _extract_or_default_name(universe_component: Dict[str, Any], instruments: List[str]) -> str:
    """Extract name from universe component or provide default."""
    symbol = _extract_or_default_symbol(universe_component, instruments)

    name_mapping = {
        "SPY": "SPDR S&P 500 ETF Trust",
        "QQQ": "Invesco QQQ Trust ETF",
        "VTI": "Vanguard Total Stock Market ETF",
        "IWM": "iShares Russell 2000 ETF",
        "EFA": "iShares MSCI EAFE ETF",
        "EEM": "iShares MSCI Emerging Markets ETF",
        "TLT": "iShares 20+ Year Treasury Bond ETF",
        "GLD": "SPDR Gold Shares",
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "ES": "E-mini S&P 500 Futures",
        "EUR/USD": "Euro/US Dollar Currency Pair",
    }

    return name_mapping.get(symbol, f"{symbol} Security")


def _extract_or_default_description(universe_component: Dict[str, Any], instruments: List[str]) -> str:
    """Extract description from universe component or provide default."""
    symbol = _extract_or_default_symbol(universe_component, instruments)
    existing_desc = universe_component.get("description", "")

    if existing_desc and len(existing_desc) > 20:
        return f"Representative {symbol} security chosen for alpha testing: {existing_desc}"

    desc_mapping = {
        "SPY": "Highly liquid S&P 500 ETF representing large-cap US equity market, "
        "ideal for testing equity momentum and factor strategies",
        "QQQ": "Technology-focused Nasdaq 100 ETF, excellent for growth and tech momentum strategies",
        "VTI": "Broad US total stock market ETF, perfect for testing market-wide alpha strategies",
        "IWM": "Small-cap Russell 2000 ETF, ideal for small-cap momentum and value strategies",
        "EFA": "International developed markets ETF, suitable for global equity strategies",
        "EEM": "Emerging markets ETF, perfect for testing strategies in developing economies",
        "TLT": "Long-term Treasury ETF, ideal for bond momentum and yield curve strategies",
        "GLD": "Gold ETF providing exposure to precious metals for commodity strategies",
        "BTC-USD": "Bitcoin cryptocurrency, perfect for testing crypto momentum and volatility strategies",
        "ETH-USD": "Ethereum cryptocurrency, ideal for DeFi and smart contract based strategies",
        "ES": "E-mini S&P 500 futures, excellent for leveraged equity strategies",
        "EUR/USD": "Major currency pair, perfect for forex carry trade and momentum strategies",
    }

    return desc_mapping.get(symbol, f"{symbol} chosen as representative security for alpha strategy testing")


def _extract_or_default_asset_class(instruments: List[str]) -> str:
    """Determine asset class based on instruments."""
    if "stocks" in instruments:
        return "equity"
    elif "crypto" in instruments:
        return "crypto"
    elif "futures" in instruments:
        return "futures"
    elif "forex" in instruments:
        return "currency"
    elif "options" in instruments:
        return "equity"  # Options are typically on equity
    else:
        return "equity"  # Default fallback
