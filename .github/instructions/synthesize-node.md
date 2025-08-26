---
applyTo:
  - "agent/nodes/synthesize.py"
  - "tests/test_synthesize_node.py"
  - "**/*synthesize*"
---

# Synthesize Node - GitHub Copilot Instructions


## Overview

You are working with the **Synthesize Node** (`agent/nodes/synthesize.py`) of the Lean Research Agent. This node is responsible for generating structured research proposals from research findings and context, using MCP (Model Context Protocol) tools and multi-provider LLM support. The synthesize node is the core component that transforms research data into valid JSON proposals conforming to `schema/lean-research-schema.jsonc`.

## Synthesize Node Architecture

### Primary Purpose
- **Transform research findings** into structured JSON proposals
- **Generate LEAN framework compatible** trading algorithm descriptions
- **Ensure schema compliance** with automatic validation and repair
- **Support alpha-only mode** for focused proposal generation

### Key Features
- **MCP Tool Integration**: Uses Model Context Protocol for structured outputs
- **Multi-Provider LLM Support**: Configurable LLM providers (OpenAI, Anthropic, Gemini, Ollama)
- **Validation & Repair Loop**: Automatic schema validation with up to 3 repair attempts
- **Alpha-Only Mode**: Simplified proposals with exactly one alpha and one universe
- **Research Context Integration**: Incorporates web research, prior art, and criticism data

## File Structure and Components

### Main Function: `synthesize_node(state, config)`
```python
async def synthesize_node(state: ResearchState, config: Config) -> Dict[str, Any]
```

**Input Processing:**
- `idea`: Original research concept
- `alpha_only`: Boolean flag for simplified proposals
- `research_plan`: Planning results from plan node
- `web_search_results`: Web research findings
- `prior_art_results`: GitHub search results and novelty assessment
- `validation_errors`: Previous validation failures for repair attempts

**Output Structure:**
- `final_proposal`: Valid JSON proposal conforming to schema
- `validation_errors`: Any remaining validation issues
- `validation_report`: Detailed validation status
- `repair_attempts`: Number of schema repair attempts made
- `current_step`: Next workflow step ("persist")

### Helper Function: `_generate_proposal()`
```python
async def _generate_proposal(llm_client, schema, idea, research_context, alpha_only, available_tools, component_names, validation_errors, original_proposal) -> Optional[Dict[str, Any]]
```

## MCP Tool Integration

### Required MCP Tools
- **web_search**: For structured output generation and validation
- **validation**: Schema validation and error reporting (via MCP client)

### Tool Usage Patterns
```python
# Create node-specific MCP client
mcp_client = MCPClient(config, llm_client, node_name="synthesize")
available_tools = mcp_client.get_available_tool_names()

# Validate proposal using MCP
validation_result = await mcp_client.validate_proposal(proposal)
```

### Fallback Behavior
- **Tool Unavailable**: Continues with basic JSON generation
- **Validation Failure**: Returns proposal with error annotations
- **MCP Connection Issues**: Graceful degradation to direct LLM calls

## Error Handling and Recovery

### Exception Types and Responses
```python
try:
    # Synthesis and validation logic
except MCPToolError as e:
    return {"error": f"MCP synthesis failed: {str(e)}", "current_step": "persist"}
except (RuntimeError, ValueError, TypeError) as e:
    return {"error": f"Synthesis failed: {str(e)}", "current_step": "persist"}
```

### State Management
- **Repair Attempts Tracking**: Prevents infinite repair loops
- **Error Context Preservation**: Maintains error history for debugging
- **Step Progression**: Always routes to "persist" step regardless of success/failure

## Development Guidelines

### Adding New Synthesis Features
1. **Extend `_generate_proposal()`** for new synthesis logic
2. **Update prompt templates** in `agent/prompts.py`
3. **Add configuration options** in `agent/config.py`
4. **Test validation behavior** with various proposal types

### Debugging Synthesis Issues
1. **Enable debug logging**: `LOG_LEVEL=DEBUG`
2. **Check MCP tool availability**: Review available_tools output
3. **Validate schema compliance**: Use `scripts/validate_proposal.py`
4. **Test repair logic**: Intentionally create invalid proposals

### Performance Optimization
- **Model Selection**: Use faster models for simple repairs
- **Token Limits**: Adjust max_tokens based on proposal complexity
- **Tool Efficiency**: Minimize MCP calls for simple operations
- **Context Pruning**: Limit research context size for large datasets

## Integration Points

### Upstream Dependencies
- **Plan Node**: Provides research_plan and strategic focus
- **Web Research Node**: Supplies web_search_results for market context
- **Prior Art Node**: Provides prior_art_results for novelty assessment
- **Criticism Node**: Supplies criticism analysis for informed synthesis

### Downstream Dependencies
- **Validate Node**: Receives final_proposal for additional validation
- **Persist Node**: Saves final_proposal to disk with metadata

### State Flow
```
Input: ResearchState with research findings
↓
Synthesis: Transform findings into JSON proposal
↓
Validation: Schema compliance checking
↓
Repair Loop: Fix validation errors (up to 3 attempts)
↓
Output: final_proposal + validation_status + repair_attempts
```

## Quality Assurance

### Schema Compliance Requirements
- **Required Fields**: Must include all mandatory schema fields
- **Data Types**: Correct typing for all proposal components
- **Component Structure**: Valid LEAN framework component organization
- **Alpha-Only Constraints**: Exactly one alpha + one universe when enabled

### Content Quality Standards
- **Trading Logic**: Plain-language descriptions only (no code)
- **Market Context**: Incorporate relevant market research
- **Risk Awareness**: Include findings from criticism analysis
- **Novelty Assessment**: Address prior art findings appropriately

### Testing and Validation
- **Unit Tests**: Individual function testing in `tests/`
- **Integration Tests**: Full workflow testing with mock data
- **Schema Validation**: Automated checking against JSON schema
- **Quality Metrics**: Validation success rate and repair effectiveness

## Usage Examples

### Basic Synthesis
```python
state = {
    "idea": "momentum-based alpha strategy",
    "alpha_only": False,
    "research_plan": "Focus on price momentum indicators...",
    "web_search_results": [...],
    "prior_art_results": {...},
}
result = await synthesize_node(state, config)
```

### Alpha-Only Mode
```python
state = {
    "idea": "mean reversion strategy",
    "alpha_only": True,
    "research_plan": "Simple mean reversion approach...",
    # ... other state data
}
result = await synthesize_node(state, config)
```

### Repair Mode
```python
state = {
    # ... initial state data
    "validation_errors": ["Missing required field: universe"],
    "repair_attempts": 1,
}
result = await synthesize_node(state, config)
```
