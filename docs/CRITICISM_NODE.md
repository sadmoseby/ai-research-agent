# Criticism Node Addition

## Overview

A new criticism node has been added to the research agent workflow to provide critical evaluation of research proposals before synthesis. This enhances the quality of generated proposals by identifying potential issues, risks, and areas for improvement.

**New Feature**: The workflow now includes conditional routing that restarts planning if:

1. Significant prior art is found (3+ similar implementations)
2. The proposal receives a low viability score (<51/100) from criticism

## Workflow Changes

The updated workflow now includes conditional routing:

1. **plan** → 2. **web_research** → 3. **prior_art**
   - If substantial prior art found → **restart plan**
   - Otherwise → 4. **criticism**
4. **criticism**
   - If low viability score → **restart plan**
   - Otherwise → 5. **synthesize** → 6. **validate** → 7. **persist**

### Restart Conditions

#### Prior Art Restart

- Triggered when 3+ similar implementations are found
- Helps ensure novel approaches rather than duplicating existing work
- Planning restarts with guidance to focus on differentiation

#### Criticism Score Restart

- Triggered when viability score is below 51/100
- Helps avoid pursuing fundamentally flawed strategies
- Planning restarts with guidance to address identified issues

#### Iteration Limits

- Maximum 3 planning iterations to prevent infinite loops
- After max iterations, workflow proceeds regardless of scores

## New Files Added

### `agent/nodes/criticism.py`

- Main criticism node implementation
- Uses OpenAI API for critical analysis
- Provides structured criticism results
- Includes error handling with fallback analysis

## State Changes

### `agent/state.py`

- Added `criticism_results: Optional[Dict[str, Any]]` field
- Added `criticism_score: Optional[float]` field
- Added `should_restart_planning: bool` field
- Added `restart_reason: Optional[str]` field
- Added `planning_iteration: int` field

## Prompt Changes

### `agent/prompts.py`

- Added `CRITICISM_SYSTEM_PROMPT`: Expert system prompt for critical evaluation
- Added `CRITICISM_USER_PROMPT`: Template for criticism requests
- Added `CRITICISM_CONTEXT_TEMPLATE`: Format for criticism context
- Added `format_criticism_context()`: Helper to format research context
- Added `format_criticism_summary()`: Helper to format criticism for synthesis
- Updated `RESEARCH_CONTEXT_TEMPLATE`: Now includes criticism summary

## Node Updates

### `agent/nodes/prior_art.py`

- Updated `current_step` to point to "criticism" instead of "synthesize"

### `agent/nodes/synthesize.py`

- Now includes criticism results in research context
- Uses `format_criticism_summary()` to include critical analysis
- Enhanced context provides better informed synthesis

### `agent/graph.py`

- Added criticism node to workflow
- Updated edge connections to include criticism step
- Maintains validation retry logic

## Criticism Node Features

### Analysis Focus Areas

1. **Market Structure Risks**: How changing market conditions might affect the strategy
2. **Data Dependencies**: Data quality and availability concerns
3. **Implementation Challenges**: Practical difficulties in live trading
4. **Risk Factors**: Non-obvious risks and limitations
5. **Alternative Explanations**: Other factors that could explain observed patterns
6. **Scalability Concerns**: Performance at different asset levels
7. **Regulatory Considerations**: Compliance and regulatory risks

### Output Structure

```python
{
    "criticism_text": "Detailed critical analysis...",
    "idea": "Original research idea",
    "viability_score": 75.0,  # 0-100 scale
    "research_quality": "analyzed|limited|unavailable",
    "risk_factors_identified": True|False,
    "recommendations_provided": True|False,
    "analysis_method": "mcp_criticism|fallback|error"
}
```

### Viability Scoring

- **0-30**: Major fundamental flaws, high risk of failure
- **31-50**: Significant concerns but potentially salvageable
- **51-70**: Moderate concerns, needs refinement but viable
- **71-85**: Good concept with minor issues to address
- **86-100**: Excellent concept with minimal concerns

### Error Handling

- Falls back to general advice if API fails
- Provides minimal criticism structure on complete failure
- Doesn't block workflow progression

## Benefits

1. **Quality Improvement**: Identifies potential issues before full development
2. **Risk Awareness**: Highlights risks that might be overlooked
3. **Better Synthesis**: Provides informed context for proposal generation
4. **Robustness**: Encourages consideration of edge cases and limitations
5. **Learning**: Helps users understand common pitfalls in quant strategies

## Usage Impact

The criticism node operates automatically in the workflow and doesn't require any changes to the CLI interface. Users will see:

- More robust and well-considered proposals
- Built-in risk assessment and mitigation suggestions
- Higher quality research outputs
- Better awareness of potential limitations

## Future Enhancements

- Specialized criticism for different strategy types
- Quantitative risk scoring
- Integration with market data for regime analysis
- Customizable criticism focus areas
- Historical performance analysis integration
