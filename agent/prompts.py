"""
Centralized prompts for the research agent nodes.
All prompts are organized here for easy modification and maintenance.
"""


class ResearchPrompts:
    """Container for all research agent prompts."""

    # Configuration constants
    MIN_VIABILITY_SCORE = 51  # Minimum score to proceed to synthesis
    MAX_PLANNING_ITERATIONS = 3  # Maximum times to restart planning
    PRIOR_ART_THRESHOLD = 3  # Number of prior art results that trigger restart

    # Planning node prompts
    PLANNING_SYSTEM_PROMPT = """
You are a quantitative research strategist responsible for creating comprehensive research plans.

Available MCP Tools: {available_tools}

Your task is to develop a structured research plan that leverages the available tools effectively.
"""

    WEB_RESEARCH_SYSTEM_PROMPT = """
You are a quantitative finance researcher conducting web-based research using MCP tools.

Available MCP Tools: {available_tools}

Use the available tools to gather comprehensive research on the given topic.
Prioritize academic sources, industry reports, and technical documentation.
"""

    PRIOR_ART_SYSTEM_PROMPT = """
You are a prior art researcher specializing in quantitative finance implementations.

Available MCP Tools: {available_tools}

Use the available tools to search for existing implementations and similar approaches.
Focus on GitHub repositories, academic code, and open-source trading frameworks.
"""

    # Planning node prompts
    ALPHA_ONLY_RESEARCH_PLAN_TEMPLATE = """
Research Plan for Alpha-Only Proposal: {idea}

Focus Areas:
1. Market analysis and data sources needed
2. Alpha generation strategy and methodology
3. Risk considerations and limitations
4. Universe definition and asset selection criteria

Search Strategy:
- Academic papers on similar trading strategies
- Industry reports on relevant market segments
- Technical analysis methodologies
- Risk management frameworks
"""

    FULL_RESEARCH_PLAN_TEMPLATE = """
Research Plan for Full Proposal: {idea}

Focus Areas:
1. Alpha generation strategies
2. Risk management approaches
3. Portfolio construction methods
4. Execution frameworks
5. Universe definition

Search Strategy:
- Comprehensive literature review
- Industry best practices
- Technical implementations
- Academic research
"""

    # Search query templates
    ALPHA_ONLY_SEARCH_QUERIES = [
        "{idea} trading strategy research",
        "{idea} alpha generation finance",
        "{idea} market analysis methodology",
        "quantitative trading risk management",
        "portfolio alpha generation techniques",
    ]

    FULL_SEARCH_QUERIES = [
        "{idea} quantitative finance research",
        "{idea} portfolio management",
        "{idea} trading strategy",
        "risk management quantitative finance",
        "portfolio optimization techniques",
        "execution algorithms trading",
    ]

    # Prior art search queries
    PRIOR_ART_QUERIES = [
        "{idea} algorithm trading",
        "{idea} quantitative finance",
        "{idea} python trading strategy",
        "lean algorithm framework",
        "{idea} alpha research",
    ]

    # Criticism prompts
    CRITICISM_SYSTEM_PROMPT = """
You are a senior quantitative finance researcher and risk management expert tasked with critically evaluating
research proposals.

Your role is to identify potential flaws, risks, limitations, and areas for improvement in quantitative trading
strategies BEFORE they are fully developed.

Available MCP Tools: {available_tools}

Focus on:
1. Market regime dependencies and robustness
2. Data quality and availability concerns
3. Implementation challenges and transaction costs
4. Risk management gaps
5. Overfitting and survivorship bias risks
6. Regulatory and compliance considerations
7. Scalability and capacity constraints
8. Alternative explanations for observed patterns

Be constructive but thorough in identifying potential issues.
Use the available MCP tools to gather additional context or verify claims if needed.
"""

    CRITICISM_USER_PROMPT = """
Please critically evaluate this research proposal idea: {idea}

Research Context:
{research_context}

Prior Art Analysis:
{prior_art_summary}

Focus Areas for Criticism:
1. **Market Structure Risks**: How might changing market conditions affect this strategy?
2. **Data Dependencies**: What data quality or availability issues could arise?
3. **Implementation Challenges**: What practical difficulties might emerge in live trading?
4. **Risk Factors**: What risks might not be immediately obvious?
5. **Alternative Explanations**: Could observed patterns be explained by other factors?
6. **Scalability Concerns**: How might the strategy perform at different asset levels?
7. **Regulatory Considerations**: Are there compliance or regulatory risks?

Provide a balanced assessment that identifies both strengths and potential weaknesses.
Include specific recommendations for addressing identified concerns.

IMPORTANT: Also provide a VIABILITY SCORE from 0-100 where:
- 0-30: Major fundamental flaws, high risk of failure
- 31-50: Significant concerns but potentially salvageable with major modifications
- 51-70: Moderate concerns, needs refinement but viable
- 71-85: Good concept with minor issues to address
- 86-100: Excellent concept with minimal concerns

Format your response with the score clearly stated as "VIABILITY SCORE: XX" at the end.
"""

    CRITICISM_CONTEXT_TEMPLATE = """
Research Plan:
{research_plan}

Key Research Findings:
{research_summary}

Market Context:
- Strategy Type: {strategy_type}
- Target Markets: {target_markets}
- Time Horizon: {time_horizon}
"""

    # Synthesis prompts
    SYNTHESIS_SYSTEM_PROMPT = """
You are a quantitative finance research expert generating a Lean algorithm research proposal.

{alpha_mode_note}Generate a research proposal that strictly follows the provided JSON schema.

Available MCP Tools: {available_tools}

Key Requirements:
- Never include actual trading code - only plain-language descriptions in 'text' fields
- For alpha-only proposals: include exactly one alpha (new or amend) and one existing universe
- All components must have clear text descriptions of their logic and methodology
- Include proper parameter definitions with tuning distributions where applicable
- Ensure all required fields are present and properly typed
- This proposal is generated using MCP (Model Context Protocol) for tool integrations
- Use the available MCP tools for any additional research or validation needs during synthesis

{repair_context}
"""

    SYNTHESIS_USER_PROMPT = """
Generate a comprehensive research proposal for: {idea}

Research Context:
{research_context}

Requirements:
- Alpha-only mode: {alpha_only}
- Must conform to the provided JSON schema
- Include detailed text descriptions (no code)
- Specify relevant parameters with tuning configurations
- Reference the research findings in component descriptions
- Acknowledge that research was conducted using MCP tool integrations

If you need additional information during synthesis, use the available MCP tools to:
- Verify technical details via web search
- Check for additional prior art via GitHub search
- Access academic sources via Tavily
- Read or write temporary files via filesystem operations
"""

    RESEARCH_CONTEXT_TEMPLATE = """
Research Plan:
{research_plan}

Web Search Results:
{web_results}

Prior Art Analysis (via MCP):
- Verdict: {verdict}
- Reasoning: {reasoning}
- Found {total_found} related implementations
- Search Method: {search_method}

Critical Analysis:
{criticism_summary}
"""

    WEB_RESULT_TEMPLATE = """
- {title} ({source})
  {content}...
"""

    VALIDATION_ERRORS_CONTEXT = """

VALIDATION ERRORS TO FIX:
{errors}

Please fix these validation errors in the output.
"""

    # Error messages
    WEB_SEARCH_ERROR_TITLE = "Search failed for: {query}"
    WEB_SEARCH_ERROR_CONTENT = "Web search temporarily unavailable for query: {query}"

    PRIOR_ART_NOVEL_REASONING = "No similar implementations found in public repositories via MCP search."
    PRIOR_ART_SIMILAR_REASONING_FEW = (
        "Found {count} potentially related implementations via MCP, but appears to have novel aspects."
    )
    PRIOR_ART_SIMILAR_REASONING_MANY = (
        "Found {count} related implementations via MCP. Consider differentiating factors."
    )

    # Validation messages
    VALIDATION_NO_PROPOSAL_ERROR = "No proposal found to validate"
    VALIDATION_NO_PROPOSAL_REPORT = "Failed - no proposal generated"
    VALIDATION_SUCCESS_REPORT = "✅ Proposal successfully validated against schema"
    VALIDATION_FAILED_REPAIR_REPORT = "❌ Validation failed, attempting repair. Errors: {count}"
    VALIDATION_FAILED_FINAL_REPORT = "❌ Validation failed after repair attempt. Errors: {count}"
    VALIDATION_SYSTEM_ERROR_TEMPLATE = "Validation system error: {error}"
    VALIDATION_ERROR_TEMPLATE = "Validation error at {path}: {message}"
    VALIDATION_PATH_ERROR_TEMPLATE = "At {path}: {message}"

    # Persistence messages
    PERSISTENCE_NO_PROPOSAL_ERROR = "No final proposal to persist"
    PERSISTENCE_SAVE_ERROR_TEMPLATE = "Failed to save proposal: {error}"

    @classmethod
    def get_alpha_mode_note(cls, alpha_only: bool) -> str:
        """Get the alpha mode note for system prompt."""
        return "ALPHA-ONLY MODE: " if alpha_only else ""

    @classmethod
    def format_available_tools(cls, mcp_tools: list) -> str:
        """Format available MCP tools for system prompts."""
        if not mcp_tools:
            return "None (operating without MCP tools)"

        tool_descriptions = {
            "web_search": "Web search for research and market data",
            "github": "GitHub code search for prior art analysis",
            "tavily": "Academic research search via Tavily",
            "filesystem": "File system operations for data access",
        }

        formatted_tools = []
        for tool in mcp_tools:
            description = tool_descriptions.get(tool, f"{tool} tool")
            formatted_tools.append(f"- {tool}: {description}")

        return "\n".join(formatted_tools)

    @classmethod
    def format_web_results(cls, web_results: list, limit: int = 5) -> str:
        """Format web search results for context."""
        formatted_results = ""
        for result in web_results[:limit]:
            title = result.get("title", "Untitled")
            source = result.get("source", "unknown")
            content = result.get("content", "")[:500]
            formatted_results += cls.WEB_RESULT_TEMPLATE.format(title=title, source=source, content=content)
        return formatted_results

    @classmethod
    def format_validation_errors(cls, errors: list) -> str:
        """Format validation errors for repair context."""
        if not errors:
            return ""
        return cls.VALIDATION_ERRORS_CONTEXT.format(errors="\n".join(errors))

    @classmethod
    def get_search_queries(cls, idea: str, alpha_only: bool) -> list:
        """Get formatted search queries based on mode."""
        queries = cls.ALPHA_ONLY_SEARCH_QUERIES if alpha_only else cls.FULL_SEARCH_QUERIES
        return [query.format(idea=idea) for query in queries]

    @classmethod
    def get_prior_art_queries(cls, idea: str) -> list:
        """Get formatted prior art search queries."""
        return [query.format(idea=idea) for query in cls.PRIOR_ART_QUERIES]

    @classmethod
    def get_prior_art_reasoning(cls, results_count: int) -> tuple[str, str]:
        """Get prior art verdict and reasoning based on results count."""
        if results_count == 0:
            return "novel", cls.PRIOR_ART_NOVEL_REASONING
        elif results_count < 3:
            return "similar", cls.PRIOR_ART_SIMILAR_REASONING_FEW.format(count=results_count)
        else:
            return "similar", cls.PRIOR_ART_SIMILAR_REASONING_MANY.format(count=results_count)

    @classmethod
    def format_criticism_context(cls, research_plan: str, web_results: list, idea: str) -> str:
        """Format context for criticism analysis."""
        # Extract key information from research and idea
        strategy_type = "quantitative trading strategy"
        target_markets = "financial markets"
        time_horizon = "medium-term"

        # Summarize research findings
        research_summary = ""
        if web_results:
            research_summary = "Key findings from web research:\n"
            for i, result in enumerate(web_results[:3], 1):
                title = result.get("title", "Untitled")
                content = result.get("content", "")[:200]
                research_summary += f"{i}. {title}: {content}...\n"

        return cls.CRITICISM_CONTEXT_TEMPLATE.format(
            research_plan=research_plan,
            research_summary=research_summary or "Limited research data available",
            strategy_type=strategy_type,
            target_markets=target_markets,
            time_horizon=time_horizon,
        )

    @classmethod
    def format_prior_art_summary(cls, prior_art_results: dict) -> str:
        """Format prior art results for criticism context."""
        verdict = prior_art_results.get("verdict", "unknown")
        reasoning = prior_art_results.get("reasoning", "No analysis available")
        total_found = prior_art_results.get("total_found", 0)

        return f"""
Prior Art Verdict: {verdict}
Reasoning: {reasoning}
Related Implementations Found: {total_found}
"""

    @classmethod
    def format_criticism_summary(cls, criticism_results: dict) -> str:
        """Format criticism results for synthesis context."""
        if not criticism_results:
            return "No critical analysis performed."

        criticism_text = criticism_results.get("criticism_text", "No criticism available")
        research_quality = criticism_results.get("research_quality", "unknown")
        score = criticism_results.get("viability_score", "N/A")

        # Truncate criticism text for context if it's too long
        if len(criticism_text) > 800:
            criticism_text = criticism_text[:800] + "... [truncated]"

        return f"""
Research Quality Assessment: {research_quality}
Viability Score: {score}/100
Critical Analysis: {criticism_text}
"""

    @classmethod
    def extract_viability_score(cls, criticism_text: str) -> float:
        """Extract viability score from criticism text."""
        import re

        # Look for "VIABILITY SCORE: XX" pattern
        pattern = r"VIABILITY SCORE:\s*(\d+)"
        match = re.search(pattern, criticism_text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

        # Fallback: look for other score patterns
        patterns = [
            r"viability.*?(\d+)(?:/100|\s*out of 100)",
            r"score.*?(\d+)(?:/100|\s*out of 100)",
            r"rating.*?(\d+)(?:/100|\s*out of 100)",
        ]

        for pattern in patterns:
            match = re.search(pattern, criticism_text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        # Default score if none found
        return 50.0

    @classmethod
    def should_restart_for_prior_art(cls, prior_art_results: dict) -> tuple[bool, str]:
        """Determine if planning should restart based on prior art."""
        total_found = prior_art_results.get("total_found", 0)
        verdict = prior_art_results.get("verdict", "unknown")

        if verdict == "novel":
            return False, ""

        if total_found >= cls.PRIOR_ART_THRESHOLD:
            reason = f"Found {total_found} similar implementations - need to differentiate approach"
            return True, reason

        return False, ""

    @classmethod
    def should_restart_for_criticism(cls, criticism_score: float, iteration: int) -> tuple[bool, str]:
        """Determine if planning should restart based on criticism score."""
        if iteration >= cls.MAX_PLANNING_ITERATIONS:
            return (
                False,
                f"Maximum planning iterations ({cls.MAX_PLANNING_ITERATIONS}) reached",
            )

        if criticism_score < cls.MIN_VIABILITY_SCORE:
            reason = f"Low viability score ({criticism_score}/100) - need to revise approach"
            return True, reason

        return False, ""
