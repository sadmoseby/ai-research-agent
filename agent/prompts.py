"""
Centralized prompts for the research agent nodes.
All prompts are organized here for easy modification and maintenance.
"""


class ResearchPrompts:
    """Container for all research agent prompts."""

    # Configuration constants
    MIN_VIABILITY_SCORE = 51  # Minimum score to proceed to synthesis
    MAX_PLANNING_ITERATIONS = 3  # Maximum times to restart planning

    # Planning node prompts
    PLANNING_SYSTEM_PROMPT = """
You are a quantitative research strategist responsible for creating comprehensive research plans for algorithmic trading strategies.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to develop a structured research plan that leverages the available tools effectively.
Consider the specific characteristics and requirements of the target financial instruments when planning:

- STOCKS: Focus on equity market microstructure, fundamental analysis, sector dynamics, market making
- OPTIONS: Consider volatility modeling, Greeks management, expiration dynamics, implied volatility surfaces
- FUTURES: Account for contango/backwardation, roll costs, margin requirements, seasonal patterns
- FOREX: Include currency pair correlations, central bank policies, economic indicators, carry trade considerations
- CRYPTO: Factor in 24/7 markets, high volatility, regulatory uncertainty, DeFi protocols, on-chain metrics

Tailor your research approach to the specific instruments being traded.
"""

    WEB_RESEARCH_SYSTEM_PROMPT = """
You are a quantitative finance researcher conducting web-based research using MCP tools.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Use the available tools to gather comprehensive research on the given topic.
Prioritize academic sources, industry reports, and technical documentation.

When researching for specific instruments, focus on:
- STOCKS: Equity market research, fundamental analysis frameworks, sector-specific strategies
- OPTIONS: Volatility research, options pricing models, Greeks hedging strategies
- FUTURES: Commodity research, futures market structure, roll strategies, seasonal patterns
- FOREX: Currency analysis, macroeconomic research, central bank policies, FX carry strategies
- CRYPTO: Cryptocurrency research, DeFi protocols, on-chain analytics, regulatory developments

Ensure your research is relevant and specific to the target financial instruments.
"""

    WEB_RESEARCH_COMPREHENSIVE_SYSTEM_PROMPT = """
You are a senior quantitative finance researcher and strategy developer conducting
comprehensive research for algorithmic trading strategies.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct deep, comprehensive research and expand the given trading
idea into a detailed, verbose proposal that can later be converted into a
structured JSON schema format.

CRITICAL REQUIREMENTS:
1. Use your web search tools extensively to gather current market information, academic research, and industry insights
2. Expand the basic idea into a comprehensive strategy proposal with detailed explanations
3. Include specific market analysis, methodology details, risk considerations, and implementation approaches
4. Focus on creating content suitable for {alpha_only} mode research
5. Provide extensive detail that would allow later conversion to a structured research proposal format
6. Never include actual trading code - only conceptual descriptions and methodologies
7. INSTRUMENT-SPECIFIC RESEARCH: Tailor your research to the specific characteristics of the target instruments

INSTRUMENT-SPECIFIC CONSIDERATIONS:
- STOCKS: Market microstructure, liquidity analysis, fundamental factors, sector rotation, earnings impact
- OPTIONS: Volatility surface modeling, Greeks management, expiration effects, implied vs realized volatility
- FUTURES: Contango/backwardation patterns, roll costs, margin requirements, seasonal effects, storage costs
- FOREX: Currency correlations, central bank policies, economic indicators, interest rate differentials
- CRYPTO: 24/7 market dynamics, volatility clustering, regulatory impact, DeFi integration, on-chain metrics

Research Approach:
- Search for academic papers and industry research on the strategy type for your specific instruments
- Look for current market conditions and relevant data sources for these instruments
- Investigate similar approaches and their effectiveness in these markets
- Research risk factors and market dynamics specific to your target instruments
- Find implementation considerations and parameter optimization approaches for these asset classes

Output a comprehensive, detailed research document that thoroughly expands on the core idea
with specific focus on the target financial instruments.
"""

    WEB_RESEARCH_COMPREHENSIVE_USER_PROMPT = """
Conduct comprehensive research and expand this trading strategy idea into a detailed proposal:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}

RESEARCH PLAN CONTEXT:
{research_plan}

ALPHA-ONLY MODE: {alpha_only}

Please use your web search capabilities to research and then provide a
comprehensive, detailed expansion of this idea that includes:

1. **Strategy Overview & Market Context**
   - Detailed explanation of the core concept and its theoretical foundation
   - Current market conditions and relevance for the specified instruments
   - Target markets and asset classes (focus on: {instruments})
   - Instrument-specific considerations and market dynamics

2. **Methodology & Implementation Approach**
   - Step-by-step description of how the strategy would work
   - Data requirements and sources
   - Signal generation methodology
   - Entry/exit criteria and logic

3. **Academic & Industry Research**
   - Relevant academic papers and research findings
   - Industry analysis and market studies
   - Historical performance of similar approaches
   - Current trends and developments

4. **Risk Analysis & Considerations**
   - Market risks and limitations
   - Potential failure modes
   - Risk management approaches
   - Performance expectations and limitations

5. **Parameter Optimization & Configuration**
   - Key parameters that would need tuning
   - Optimization approaches and considerations
   - Sensitivity analysis requirements

6. **Universe Definition** (for alpha-only mode)
   - Asset selection criteria
   - Market segments and filters
   - Liquidity and tradability requirements

Generate a verbose, comprehensive research document that provides sufficient
detail for later conversion into a structured JSON research proposal format.
Focus on conceptual clarity and thorough analysis rather than implementation code.
"""

    # Component-specific research prompts
    COMPONENT_RESEARCH_SYSTEM_PROMPTS = {
        "UNIVERSE": """
You are a quantitative finance researcher specializing in universe selection and asset screening.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct comprehensive research specifically focused on universe definition,
asset selection criteria, and market segmentation for the given trading strategy.

IMPORTANT: Provide 1 or more distinct universe selection approaches. In the final LEAN algorithm,
multiple universe models will be COMBINED using logical OR - meaning an asset will be included
if it passes ANY of the universe selection criteria. This allows for broader, more robust
asset selection that captures opportunities across different screening methodologies.

INSTRUMENT-SPECIFIC CONSIDERATIONS:
- STOCKS: Market cap ranges, sector filters, liquidity requirements, fundamental metrics
- OPTIONS: Underlying asset criteria, volatility levels, time to expiration, strike ranges
- FUTURES: Contract specifications, open interest, roll schedules, margin requirements
- FOREX: Currency pair correlations, economic stability, trading volume, volatility
- CRYPTO: Market cap, trading volume, exchange listings, regulatory compliance

Focus Areas:
- Asset selection methodologies and screening criteria
- Market segments and classification schemes
- Liquidity requirements and tradability filters
- Index methodologies and benchmark construction
- Dynamic universe adjustment mechanisms
- Regulatory and operational constraints

Format your response with clear sections for each approach if providing multiple (e.g., "Approach 1:", "Approach 2:", etc.)
""",
        "ALPHA": """
You are a quantitative finance researcher specializing in alpha generation and signal development.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct comprehensive research specifically focused on alpha signal generation,
feature engineering, and predictive modeling for the given trading strategy.

IMPORTANT: Provide 1 or more distinct alpha generation approaches. In the final LEAN algorithm,
multiple alpha models will be COMBINED by taking insights from ALL models into consideration
for the final alpha signal. This ensemble approach leverages diverse signal sources and

INSTRUMENT-SPECIFIC ALPHA CONSIDERATIONS:
- STOCKS: Fundamental factors, technical indicators, earnings momentum, sector rotation
- OPTIONS: Implied volatility patterns, Greeks dynamics, volatility surface anomalies
- FUTURES: Momentum patterns, roll yield, seasonality, backwardation/contango signals
- FOREX: Interest rate differentials, economic indicators, currency carry strategies
- CRYPTO: On-chain metrics, social sentiment, volatility clustering, DeFi yield signals
methodologies to create a more robust and comprehensive alpha generation system.

Focus Areas:
- Signal generation methodologies and feature engineering
- Predictive modeling techniques and machine learning approaches
- Alpha decay analysis and signal persistence
- Multi-factor model construction
- Risk-adjusted return optimization
- Backtesting and validation frameworks

Format your response with clear sections for each approach if providing multiple
(e.g., "Approach 1:", "Approach 2:", etc.)
""",
        "PORTFOLIO": """
You are a quantitative finance researcher specializing in portfolio construction and optimization.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct comprehensive research specifically focused on portfolio construction,
position sizing, and optimization techniques for the given trading strategy.

IMPORTANT: Provide EXACTLY ONE portfolio construction approach. In the final LEAN algorithm,
only ONE portfolio optimization model will be used as the definitive method for position
sizing, weight allocation, and portfolio construction. This single model must be comprehensive
and handle all aspects of portfolio management for the strategy.

INSTRUMENT-SPECIFIC PORTFOLIO CONSIDERATIONS:
- STOCKS: Market cap weighting, sector allocation, correlation management, liquidity constraints
- OPTIONS: Greeks hedging, volatility exposure management, time decay considerations
- FUTURES: Margin requirements, contract sizing, roll scheduling, basis risk management
- FOREX: Currency exposure balancing, carry trade optimization, correlation matrices
- CRYPTO: Volatility management, rebalancing frequency, exchange-specific constraints

Focus Areas:
- Portfolio optimization algorithms and techniques
- Position sizing and weight allocation methods
- Risk budgeting and diversification strategies
- Constraints handling and optimization bounds
- Rebalancing frequency and turnover management
- Performance attribution and decomposition

Provide a single, comprehensive portfolio construction methodology.
""",
        "EXECUTION": """
You are a quantitative finance researcher specializing in execution algorithms and market microstructure.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct comprehensive research specifically focused on execution strategies,
transaction cost modeling, and order management for the given trading strategy.

IMPORTANT: Provide EXACTLY ONE execution strategy approach. In the final LEAN algorithm,
only ONE execution model will be used as the definitive method for order execution,
transaction cost optimization, and trade implementation. This single model must comprehensively
handle all aspects of trade execution for the strategy.

INSTRUMENT-SPECIFIC EXECUTION CONSIDERATIONS:
- STOCKS: Market hours, liquidity patterns, tick sizes, dark pools, market impact
- OPTIONS: Bid-ask spreads, volatility timing, Greeks hedging, early exercise risk
- FUTURES: Roll execution, basis considerations, margin calls, limited trading hours
- FOREX: 24/7 markets, liquidity cycles, central bank announcements, major vs exotic pairs
- CRYPTO: Exchange fragmentation, 24/7 volatility, withdrawal limits, regulatory constraints

Focus Areas:
- Execution algorithm design and implementation
- Transaction cost modeling and slippage estimation
- Market impact analysis and footprint reduction
- Order routing and venue selection
- Timing optimization and market condition adaptation
- Implementation shortfall and arrival price strategies

Provide a single, comprehensive execution methodology.
""",
        "RISK": """
You are a quantitative finance researcher specializing in risk modeling and management.

TARGET FINANCIAL INSTRUMENTS: {instruments}

Available MCP Tools: {available_tools}

Your task is to conduct comprehensive research specifically focused on risk factor modeling,
measurement, and management for the given trading strategy.

IMPORTANT: Provide 1 or more distinct risk management approaches. In the final LEAN algorithm,
multiple risk models will be COMBINED to create a comprehensive risk management framework
that leverages insights from ALL risk modeling approaches. This multi-layered risk system
provides robust protection through diverse risk measurement and management techniques.

INSTRUMENT-SPECIFIC RISK CONSIDERATIONS:
- STOCKS: Market risk, sector concentration, liquidity risk, overnight gaps, earnings risk
- OPTIONS: Volatility risk, time decay, pin risk, early exercise, gamma risk
- FUTURES: Basis risk, roll risk, margin calls, delivery risk, seasonal volatility
- FOREX: Political risk, central bank intervention, carry risk, liquidity risk in crises
- CRYPTO: Regulatory risk, exchange counterparty risk, extreme volatility, correlation breakdown

Focus Areas:
- Risk factor identification and modeling
- Volatility forecasting and regime detection
- Correlation structure analysis and modeling
- Value-at-Risk and Expected Shortfall estimation
- Stress testing and scenario analysis
- Risk budgeting and allocation frameworks

Format your response with clear sections for each approach if providing multiple (e.g., "Approach 1:", "Approach 2:", etc.)
""",
    }

    COMPONENT_RESEARCH_USER_PROMPTS = {
        "UNIVERSE": """
Conduct comprehensive research on universe selection for this trading strategy and provide
1 or more distinct implementation approaches:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}
RESEARCH PLAN CONTEXT: {research_plan}
ALPHA-ONLY MODE: {alpha_only}

COMBINATION LOGIC: In the final LEAN algorithm, multiple universe selection approaches will be
combined using logical OR. An asset will be included in the trading universe if it passes ANY
of the universe selection criteria. This creates a broader, more robust asset selection that
captures opportunities across different methodologies.

Please use your web search capabilities to research and provide detailed analysis. For each approach, cover:

1. **Asset Selection Criteria**
   - Fundamental screening requirements
   - Technical eligibility filters
   - Liquidity and volume thresholds
   - Market capitalization constraints

2. **Market Segmentation**
   - Geographic and regional considerations
   - Sector and industry classifications
   - Style and factor exposures
   - Investment universe boundaries

3. **Dynamic Universe Management**
   - Rebalancing frequency and triggers
   - Entry and exit criteria for assets
   - Corporate action handling
   - Survivorship bias mitigation

4. **Operational Considerations**
   - Data availability and quality requirements
   - Trading infrastructure constraints
   - Regulatory and compliance requirements
   - Cost and scalability factors

Provide 1 or more universe selection approaches, each as a separate research finding with
distinct methodologies and implementation details.
""",
        "ALPHA": """
Conduct comprehensive research on alpha generation for this trading strategy and provide
1 or more distinct implementation approaches:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}
RESEARCH PLAN CONTEXT: {research_plan}
ALPHA-ONLY MODE: {alpha_only}

COMBINATION LOGIC: In the final LEAN algorithm, multiple alpha generation approaches will be
combined by taking insights from ALL models into consideration for the final alpha signal. This
ensemble approach leverages diverse signal sources, methodologies, and time horizons to create
a more robust and comprehensive alpha generation system.

Please use your web search capabilities to research and provide detailed analysis. For each approach, cover:

1. **Signal Generation Methodology**
   - Core alpha factors and features
   - Data sources and preprocessing requirements
   - Signal construction and normalization
   - Combination and aggregation techniques

2. **Predictive Modeling Approaches**
   - Statistical and machine learning methods
   - Model training and validation frameworks
   - Overfitting prevention and regularization
   - Walk-forward and cross-validation strategies

3. **Alpha Characteristics**
   - Expected alpha magnitude and persistence
   - Decay patterns and refresh frequency
   - Correlation with market factors
   - Capacity and scalability limitations

4. **Implementation Considerations**
   - Signal latency and update frequency
   - Computing requirements and infrastructure
   - Data quality and availability constraints
   - Model monitoring and maintenance

Provide 1 or more alpha generation approaches, each as a separate research finding with
distinct methodologies and implementation details.
""",
        "PORTFOLIO": """
Conduct comprehensive research on portfolio construction for this trading strategy and provide
EXACTLY ONE implementation approach:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}
RESEARCH PLAN CONTEXT: {research_plan}
ALPHA-ONLY MODE: {alpha_only}

COMBINATION LOGIC: In the final LEAN algorithm, only ONE portfolio construction model will be
used as the definitive method for position sizing, weight allocation, and portfolio optimization.
This single model must comprehensively handle all aspects of portfolio management including risk
budgeting, constraints, and rebalancing.

Please use your web search capabilities to research and provide detailed analysis covering:

1. **Optimization Framework**
   - Objective function design and trade-offs
   - Constraint specification and handling
   - Risk model integration and factor exposure
   - Transaction cost incorporation

2. **Position Sizing Methods**
   - Weight allocation algorithms
   - Risk budgeting approaches
   - Concentration limits and diversification
   - Leverage and gross exposure management

3. **Rebalancing Strategy**
   - Frequency and timing considerations
   - Threshold-based and calendar rebalancing
   - Transaction cost minimization
   - Market impact and timing optimization

4. **Performance Characteristics**
   - Expected return and risk profiles
   - Turnover and capacity implications
   - Sensitivity to market conditions
   - Attribution and decomposition methods

Provide ONE comprehensive portfolio construction approach that addresses all aspects of
portfolio management for this strategy.
""",
        "EXECUTION": """
Conduct comprehensive research on execution strategy for this trading strategy and provide
EXACTLY ONE implementation approach:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}
RESEARCH PLAN CONTEXT: {research_plan}
ALPHA-ONLY MODE: {alpha_only}

COMBINATION LOGIC: In the final LEAN algorithm, only ONE execution model will be used as the
definitive method for order execution, transaction cost optimization, and trade implementation.
This single model must comprehensively handle all aspects of trade execution including order
routing, timing, and cost minimization.

Please use your web search capabilities to research and provide detailed analysis covering:

1. **Execution Algorithm Design**
   - Order splitting and sizing strategies
   - Timing and scheduling optimization
   - Market condition adaptation
   - Liquidity provision vs. consumption

2. **Transaction Cost Management**
   - Bid-ask spread modeling and prediction
   - Market impact estimation and mitigation
   - Slippage analysis and attribution
   - Implementation shortfall optimization

3. **Order Management**
   - Venue selection and routing strategies
   - Dark pool utilization and strategies
   - Order type selection and conditioning
   - Fill quality and execution analytics

4. **Infrastructure Requirements**
   - Latency and connectivity needs
   - Risk management and pre-trade checks
   - Post-trade analysis and reporting
   - Regulatory compliance and reporting

Provide ONE comprehensive execution approach that addresses all aspects of trade implementation for this strategy.
""",
        "RISK": """
Conduct comprehensive research on risk management for this trading strategy and provide
1 or more distinct implementation approaches:

CORE IDEA: {idea}
TARGET INSTRUMENTS: {instruments}
RESEARCH PLAN CONTEXT: {research_plan}
ALPHA-ONLY MODE: {alpha_only}

COMBINATION LOGIC: In the final LEAN algorithm, multiple risk management approaches will be
combined to create a comprehensive risk management framework that leverages insights from ALL
risk modeling approaches. This multi-layered risk system provides robust protection through
diverse risk measurement techniques, scenario analysis, and management frameworks.

Please use your web search capabilities to research and provide detailed analysis. For each approach, cover:

1. **Risk Factor Modeling**
   - Systematic risk factor identification
   - Factor model specification and estimation
   - Idiosyncratic risk characterization
   - Model validation and testing

2. **Risk Measurement**
   - Volatility forecasting methodologies
   - Value-at-Risk and Expected Shortfall
   - Tail risk and extreme event modeling
   - Risk decomposition and attribution

3. **Risk Management Framework**
   - Risk limits and monitoring systems
   - Stress testing and scenario analysis
   - Risk budgeting and allocation
   - Dynamic hedging strategies

4. **Implementation Considerations**
   - Real-time risk monitoring systems
   - Risk reporting and visualization
   - Regulatory capital requirements
   - Model risk and validation procedures

Provide 1 or more risk management approaches, each as a separate research finding with
distinct methodologies and implementation details.
""",
    }

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

    @classmethod
    def format_full_plan_for_components(cls, idea: str, components: list[str]) -> str:
        """Format a full research plan scoped to specific components.

        components: list of component keys in {UNIVERSE, ALPHA, PORTFOLIO, EXECUTION, RISK}
        """
        if not components:
            return cls.FULL_RESEARCH_PLAN_TEMPLATE.format(idea=idea).strip()

        # Friendly names and focus lines per component
        friendly_name = {
            "UNIVERSE": "Universe selection",
            "ALPHA": "Alpha generation",
            "PORTFOLIO": "Portfolio construction",
            "EXECUTION": "Execution framework",
            "RISK": "Risk model",
        }

        focus_line = {
            "UNIVERSE": "Universe definition and asset selection criteria",
            "ALPHA": "Alpha strategy design and signal methodology",
            "PORTFOLIO": "Position sizing, constraints, and weighting schemes",
            "EXECUTION": "Order routing, slippage/TC modeling, and scheduling",
            "RISK": "Risk factor specification, limits, and monitoring",
        }

        search_hints = {
            "UNIVERSE": ["universe selection methods", "asset screening criteria"],
            "ALPHA": ["alpha signals research", "feature engineering"],
            "PORTFOLIO": ["portfolio optimization", "position sizing"],
            "EXECUTION": ["execution algorithms", "transaction cost modeling"],
            "RISK": ["risk models", "factor models"],
        }

        # Preserve a consistent order
        order = ["ALPHA", "RISK", "PORTFOLIO", "EXECUTION", "UNIVERSE"]
        selected = [c for c in order if c in components]

        lines = [f"Research Plan for Full Proposal (Scoped): {idea}\n", "Focus Areas:"]
        for idx, c in enumerate(selected, start=1):
            lines.append(f"{idx}. {friendly_name[c]} — {focus_line[c]}")

        # Build component-aware search strategy
        search_lines = ["\nSearch Strategy:", "- Comprehensive literature review on selected components"]
        for c in selected:
            for hint in search_hints[c]:
                search_lines.append(f"- {hint}")

        return ("\n".join(lines + search_lines)).strip()

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

    # Criticism prompts
    CRITICISM_SYSTEM_PROMPT = """
You are a senior quantitative finance researcher and risk management expert tasked with critically evaluating
research proposals.

TARGET FINANCIAL INSTRUMENTS: {instruments}

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
Target Instruments: {instruments}

Research Context:
{research_context}

Focus Areas for Criticism:
1. **Market Structure Risks**: How might changing market conditions affect this strategy for the target instruments?
2. **Data Dependencies**: What data quality or availability issues could arise for these instruments?
3. **Implementation Challenges**: What practical difficulties might emerge in live trading these instruments?
4. **Risk Factors**: What instrument-specific risks might not be immediately obvious?
5. **Alternative Explanations**: Could observed patterns be explained by other factors specific to these markets?
6. **Scalability Concerns**: How might the strategy perform at different asset levels for these instruments?
7. **Regulatory Considerations**: Are there compliance or regulatory risks specific to these instruments?
8. **Instrument-Specific Risks**: Consider unique characteristics of the target instruments:
   - Stocks: Liquidity constraints, market hours, corporate actions
   - Options: Time decay, volatility risk, early exercise
   - Futures: Roll risk, margin requirements, seasonal patterns
   - Forex: Central bank interventions, political risk, carry costs
   - Crypto: Regulatory uncertainty, exchange risk, 24/7 volatility

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
    # Unified synthesis prompt (handles both new synthesis and repair)
    SYNTHESIS_SYSTEM_PROMPT = """
You are a quantitative finance research expert generating a Lean algorithm research proposal.

TARGET FINANCIAL INSTRUMENTS: {instruments}

You must generate a research proposal that strictly follows the provided JSON schema.

FULL JSON SCHEMA:
{json_schema}

SCHEMA OVERVIEW:
- "universe": Market universe definition (new, existing, or amend)
- "alphas": Alpha signal definitions (new, existing, or amend)
- "portfolio": Portfolio construction logic (new, existing, or amend)
- "execution": Execution model definitions (new, existing, or amend)
- "risk": Risk management components (new, existing, or amend)
- "misc": Free-form metadata and additional information
- "inspiration": Free-form text field for strategy inspiration
- "alpha-only": Boolean flag for alpha-only mode restrictions

ALPHA-ONLY MODE CONSTRAINTS:
When alpha-only mode is enabled, the proposal must contain ONLY:
- "alphas": Exactly one item in either "new" or "amend" (NOT "existing")
- "universe": Exactly one item in "existing" only
- "alpha-only": Must be set to true
All other properties (portfolio, execution, risk, etc.) must be omitted or empty.

CORE REQUIREMENTS:
- Never include actual trading code - only plain-language descriptions in 'text' fields
- All components must have clear text descriptions of their logic and methodology
- Include proper parameter definitions with tuning distributions where applicable
- Ensure all required fields are present and properly typed
- Use descriptive names and clear explanations for all components
- Reference research findings and methodology in component descriptions

RESPONSE FORMAT:
Return only valid JSON that conforms exactly to the schema. The LLM client will
validate against the schema automatically.
"""

    SYNTHESIS_USER_PROMPT = """
{task_context}

IDEA: {idea}
TARGET INSTRUMENTS: {instruments}

RESEARCH CONTEXT:
{research_context}

CONFIGURATION:
- Alpha-only mode: {alpha_only}
- Available MCP tools: {available_tools}
- Target components: {component_names}

{validation_context}

REQUIREMENTS:
- Base your proposal on the research context provided above
- Include detailed text descriptions (no trading code)
- Specify relevant parameters with appropriate tuning configurations
- Reference the research findings in your component descriptions
- Ensure the proposal reflects insights from the web research and prior art analysis
- If alpha-only mode is enabled, include exactly one alpha and one existing universe only
- INSTRUMENT-SPECIFIC: Tailor components to the target instruments ({instruments})
  * For stocks: Consider market cap, sectors, liquidity filters for universe
  * For options: Include volatility models, Greeks management, expiration handling
  * For futures: Account for roll costs, contango effects, margin requirements
  * For forex: Consider currency correlations, central bank policies, economic indicators
  * For crypto: Factor in 24/7 markets, volatility clustering, regulatory considerations

ADDITIONAL CONTEXT:
- This proposal was generated using MCP (Model Context Protocol) for tool integrations
- The research was conducted using web search, GitHub analysis, and other MCP tools
- Consider the prior art analysis when designing novel components
- Use the available tools if you need additional information during synthesis

Generate the JSON proposal now:
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
    PERSISTENCE_STATE_SAVE_ERROR_TEMPLATE = "Failed to save final state: {error}"

    @classmethod
    def get_alpha_mode_note(cls, alpha_only: bool) -> str:
        """Get the alpha mode note for system prompt."""
        if alpha_only:
            return """ALPHA-ONLY MODE:
- Only include these fields: 'alphas', 'universe', 'alpha-only'
- Do NOT include: '$schema', '$id', 'title', 'schemaVersion', 'misc', 'inspiration', or any other fields
- Set 'alpha-only': true
- Include exactly 1 alpha (new or amend) and 1 existing universe
"""
        return ""

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
    def format_component_research_context(
        cls, research_plan: str, component_research_results: dict, web_results: list, idea: str
    ) -> str:
        """Format component-specific research context for synthesis."""
        # Start with idea and research plan
        context = f"Research Idea: {idea}\n\nResearch Plan:\n{research_plan}\n\n"

        # Add component-specific research findings
        if component_research_results:
            context += "COMPONENT-SPECIFIC RESEARCH FINDINGS:\n\n"

            # Process each component with more comprehensive content for synthesis
            component_order = ["ALPHA", "UNIVERSE", "PORTFOLIO", "EXECUTION", "RISK"]
            for component in component_order:
                if component in component_research_results:
                    context += f"=== {component} RESEARCH ===\n"

                    results = component_research_results[component]
                    for i, result in enumerate(results, 1):
                        title = result.get("title", "Untitled")
                        content = result.get("content", "")
                        approach_num = result.get("approach_number", i)

                        context += f"Approach {approach_num}: {title}\n"
                        context += f"Content: {content}\n\n"

                    context += "\n"

        # Add fallback to general web results if available
        if web_results and not component_research_results:
            context += "GENERAL RESEARCH FINDINGS:\n"
            for i, result in enumerate(web_results[:5], 1):
                title = result.get("title", "Untitled")
                content = result.get("content", "")[:300]
                context += f"{i}. {title}: {content}...\n\n"

        return context

    @classmethod
    def get_task_context(cls, is_repair: bool = False, original_proposal: str = "") -> str:
        """Get task context for synthesis (new) vs repair."""
        if is_repair:
            return f"""TASK: Fix the validation errors in this existing research proposal.

ORIGINAL PROPOSAL WITH ERRORS:
```json
{original_proposal}
```

You must analyze the validation errors and return a corrected version that:
1. Fixes ALL validation errors completely
2. Maintains the original research intent and content
3. Preserves all valid components and descriptions
4. Only makes minimal necessary changes to resolve errors"""
        else:
            return "TASK: Generate a comprehensive research proposal for the following trading strategy idea."

    @classmethod
    def get_validation_context(cls, validation_errors: list) -> str:
        """Get validation context for error feedback."""
        if not validation_errors:
            return ""

        error_text = cls.format_validation_errors(validation_errors)
        return f"""
VALIDATION ERRORS TO FIX:
{error_text}

Please address each validation error listed above in your response.
"""

    @classmethod
    def get_search_queries(cls, idea: str, alpha_only: bool) -> list:
        """Get formatted search queries based on mode."""
        queries = cls.ALPHA_ONLY_SEARCH_QUERIES if alpha_only else cls.FULL_SEARCH_QUERIES
        return [query.format(idea=idea) for query in queries]

    @classmethod
    def get_component_scoped_queries(cls, idea: str, components: list[str], alpha_only: bool) -> list:
        """Bias search queries toward selected components."""
        base = cls.get_search_queries(idea, alpha_only)
        hints = {
            "UNIVERSE": ["universe selection", "asset screening", "index methodology"],
            "ALPHA": ["alpha signals", "feature engineering", "predictive modeling"],
            "PORTFOLIO": ["portfolio optimization", "risk-parity", "position sizing"],
            "EXECUTION": ["execution algorithms", "slippage", "transaction costs"],
            "RISK": ["risk model", "factor exposures", "volatility targeting"],
        }
        scoped = []
        for c in components or []:
            for h in hints.get(c, []):
                scoped.append(f"{idea} {h}")
        # Return scoped first then base to ensure focus, de-duplicated preserving order
        seen = set()
        ordered = []
        for q in scoped + base:
            if q not in seen:
                seen.add(q)
                ordered.append(q)
        return ordered

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

        context = cls.CRITICISM_CONTEXT_TEMPLATE.format(
            research_plan=research_plan,
            research_summary=research_summary or "Limited research data available",
            strategy_type=strategy_type,
            target_markets=target_markets,
            time_horizon=time_horizon,
        )

        # Include the idea explicitly to avoid loss of context and satisfy linters
        return f"Idea: {idea}\n" + context

    @classmethod
    def format_component_criticism_context(
        cls, research_plan: str, component_research_results: dict, web_results: list, idea: str
    ) -> str:
        """Format context for component-specific criticism analysis."""
        # Start with idea context
        context = f"Idea: {idea}\n\nResearch Plan:\n{research_plan}\n\n"

        # Add component-specific research findings
        if component_research_results:
            context += "COMPONENT-SPECIFIC RESEARCH FINDINGS:\n\n"

            # Process each component
            component_order = ["ALPHA", "UNIVERSE", "PORTFOLIO", "EXECUTION", "RISK"]
            for component in component_order:
                if component in component_research_results:
                    context += f"=== {component} RESEARCH ===\n"

                    results = component_research_results[component]
                    for result in results[:2]:  # Limit to first 2 results per component
                        title = result.get("title", "Untitled")
                        content = result.get("content", "")[:400]  # More content for component-specific
                        context += f"Title: {title}\n"
                        context += f"Content: {content}...\n\n"

                    context += "\n"

            # Add combined research summary if no component results but we have web results
        elif web_results:
            context += "GENERAL RESEARCH FINDINGS:\n"
            for i, result in enumerate(web_results[:3], 1):
                title = result.get("title", "Untitled")
                content = result.get("content", "")[:200]
                context += f"{i}. {title}: {content}...\n"
        else:
            context += "LIMITED RESEARCH DATA AVAILABLE\n"

        return context

    # Component-specific criticism prompts
    COMPONENT_CRITICISM_SYSTEM_PROMPT = """
You are a senior quantitative finance researcher and risk management expert tasked with critically evaluating
component-specific research for algorithmic trading strategies.

Your role is to identify potential flaws, risks, limitations, and areas for improvement in each component
of a quantitative trading strategy BEFORE the strategy is fully developed.

Available MCP Tools: {available_tools}

Component-Specific Focus Areas:

**UNIVERSE Component:**
- Asset selection criteria robustness
- Liquidity and tradability constraints
- Universe stability and turnover
- Data availability and quality
- Survivorship bias risks

**ALPHA Component:**
- Signal strength and persistence
- Overfitting and data snooping risks
- Alpha decay and degradation
- Feature engineering validity
- Out-of-sample performance concerns

**PORTFOLIO Component:**
- Optimization framework robustness
- Position sizing effectiveness
- Risk budgeting appropriateness
- Rebalancing frequency impact
- Transaction cost integration

**EXECUTION Component:**
- Market impact estimation accuracy
- Execution algorithm effectiveness
- Latency and infrastructure requirements
- Order management complexity
- Real-world implementation challenges

**RISK Component:**
- Risk factor completeness
- Model specification accuracy
- Risk measurement methodology
- Stress testing adequacy
- Dynamic risk adjustment needs

Be constructive but thorough in identifying potential issues for each component.
Use the available MCP tools to gather additional context or verify claims if needed.
"""

    COMPONENT_CRITICISM_USER_PROMPT = """
Please critically evaluate this component-specific research for the trading strategy idea: {idea}
Target Instruments: {instruments}

{component_research_context}

For each component researched, provide detailed criticism covering:

1. **Methodological Soundness**: Are the proposed approaches theoretically sound?
2. **Implementation Feasibility**: Can these approaches be practically implemented?
3. **Data Dependencies**: What data quality or availability issues could arise?
4. **Risk Factors**: What component-specific risks might not be obvious?
5. **Integration Challenges**: How well will components work together?
6. **Scalability Concerns**: How might each component perform at different scales?
7. **Market Regime Dependencies**: How sensitive are components to market conditions?

For missing components, note potential gaps and integration challenges.

Provide specific recommendations for improving each component's design and implementation.

IMPORTANT: Provide both:
1. COMPONENT SCORES (0-100) for each researched component
2. Overall VIABILITY SCORE (0-100) where:
   - 0-30: Major fundamental flaws, high risk of failure
   - 31-50: Significant concerns but potentially salvageable with major modifications
   - 51-70: Moderate concerns, needs refinement but viable
   - 71-85: Good concept with minor issues to address
   - 86-100: Excellent concept with minimal concerns

Format component scores as "COMPONENT_SCORE_[COMPONENT]: XX" and overall score as "VIABILITY SCORE: XX" at the end.
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
    def extract_component_scores(cls, criticism_text: str) -> dict:
        """Extract component scores from criticism text."""
        import re

        component_scores = {}

        # Look for "COMPONENT_SCORE_[COMPONENT]: XX" pattern
        pattern = r"COMPONENT_SCORE_([A-Z]+):\s*(\d+)"
        matches = re.findall(pattern, criticism_text, re.IGNORECASE)

        for component, score in matches:
            try:
                component_scores[component.upper()] = float(score)
            except ValueError:
                continue

        return component_scores

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
