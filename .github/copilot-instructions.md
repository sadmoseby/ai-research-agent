# Lean Research Agent - Copilot Instructions

## Overview

You are working with a **Lean Research Agent** that generates research proposal JSON files under the `proposals/` directory, conforming to the schema at `schema/lean-research-schema.jsonc`. The system has evolved significantly with advanced features for quality control, multi-provider LLM support, and comprehensive tool integration. The proposal will be used to generate a LEAN framework based trading algorithm.

## Current System Architecture

### Core Components
- **LangGraph Workflow**: Checkpointed state management with conditional routing
- **Multi-Provider LLM**: OpenAI, Anthropic (Claude), Gemini, and Ollama support
- **MCP Integration**: Model Context Protocol for standardized tool communication
- **Quality Control**: Criticism node and conditional restart logic
- **Configurable Pipeline**: Enable/disable individual workflow nodes

### Workflow Nodes
1. **plan** - Research planning and strategy formation
2. **web_research** - Web search using OpenAI/Tavily via MCP
3. **prior_art** - GitHub code search for novelty assessment
4. **criticism** - Quality evaluation with conditional restart logic
5. **synthesize** - Proposal generation using structured outputs
6. **validate** - JSON schema validation with repair attempts
7. **persist** - File output to proposals directory

## Key Requirements for Development

### Orchestration
- **LangGraph** with checkpointed state management
- **Conditional routing** based on quality metrics and prior art findings
- **Node enable/disable** configuration for different use cases

### LLM Integration
- **Multi-provider support** via unified `llm_client.py`
- **Per-node configuration** for models, temperature, max_tokens
- **Structured outputs** using Pydantic models and JSON schema
- **MCP tools** for web search, GitHub search, and file operations

### Quality Control
- **Criticism scoring** with restart logic (score < 51 triggers restart)
- **Prior art checking** with restart logic (3+ findings trigger restart)
- **Maximum 3 planning iterations** to prevent infinite loops
- **Schema validation** with automatic repair attempts

### Tool Integration
- **MCP (Model Context Protocol)** for standardized tool access
- **Per-node tool access control** via configuration
- **Fallback mechanisms** when tools unavailable
- **GitHub API** for prior art checking via MCP
- **Web search** via OpenAI MCP server with Tavily fallback

## Current Project Structure

```
/agent/
  __init__.py
  config.py              # Multi-provider config + node settings
  graph.py               # LangGraph workflow with conditional routing
  state.py               # Enhanced state with quality tracking
  llm_client.py          # Multi-provider LLM client
  prompts.py             # Centralized prompt management
  nodes/
    plan.py              # Planning with MCP tool awareness
    web_research.py      # Web search via MCP tools
    prior_art.py         # GitHub search with restart logic
    criticism.py         # Quality evaluation and scoring
    synthesize.py        # Proposal generation with context
    validate.py          # Schema validation with repair
    persist.py           # File persistence with reporting
  tools/
    mcp_client.py        # MCP protocol client
    github_api.py        # GitHub API integration
    tavily_tool.py       # Tavily search integration

/main.py                 # Entry point CLI
/cli.py                  # Legacy CLI (deprecated)
/requirements.txt
/schema/lean-research-schema.jsonc    # JSON schema with comments
/proposals/              # Output directory
/docs/                   # Comprehensive documentation
```

## Environment Variables

### Required
- `OPENAI_API_KEY` (required for web search and LLM)

### Optional but Recommended
- `GITHUB_TOKEN` (for prior art checking)
- `TAVILY_API_KEY` (for fallback web search)
- `ANTHROPIC_API_KEY` (for Claude models)
- `GOOGLE_API_KEY` (for Gemini models)

### Configuration Examples
- `SYNTHESIZE_PROVIDER="anthropic"` (use Claude for synthesis)
- `CRITICISM_ENABLED="false"` (disable quality checks for speed)
- `LOG_LEVEL="DEBUG"` (enable debug logging)
- `WEB_RESEARCH_MCP_TOOLS="web_search,tavily"` (tool access control)

## Run Commands

### Current Usage
```bash
# Basic proposal
python main.py propose --idea "momentum-based alpha strategy"

# Alpha-only mode (focused proposals)
python main.py propose --idea "mean reversion strategy" --alpha-only

# Custom output filename
python main.py propose --idea "volatility arbitrage" --slug "vol_arb"
```

### Legacy Support
```bash
# Still supported but deprecated
python cli.py propose --idea "pairs trading" --alpha-only
```

## Development Guidelines

### Adding New Nodes
1. Create node file in `agent/nodes/` with signature `(state: ResearchState, config: Config) -> Dict[str, Any]`
2. Add to node sequence in `agent/graph.py`
3. Add enable/disable support in `agent/config.py`
4. Add prompts to `agent/prompts.py`
5. Configure MCP tool access if needed

### Adding New Tools
1. Implement MCP client in `agent/tools/`
2. Add to global MCP configuration
3. Configure per-node tool access
4. Update tool-aware prompts

### Configuration Patterns
- Use environment variables for all settings
- Support per-node overrides (e.g., `SYNTHESIZE_MODEL="claude-3-5-sonnet"`)
- Provide sensible defaults
- Validate configuration at startup

## Quality and Validation

### Conditional Restart Logic
- **Prior art restart**: 3+ similar implementations found → restart planning
- **Criticism restart**: Viability score < 51/100 → restart planning
- **Iteration limit**: Maximum 3 planning cycles to prevent infinite loops

### Schema Compliance
- Strict validation against `schema/lean-research-schema.jsonc`
- Automatic repair attempts on validation failure
- Alpha-only mode enforcement (exactly one alpha + one universe)

### Error Handling
- Graceful fallbacks when tools unavailable
- Comprehensive logging for debugging
- Clear error messages for configuration issues

## Documentation

### Key Documentation Files
- `docs/ARCHITECTURE_OVERVIEW.md` - System architecture
- `docs/CONFIGURATION_GUIDE.md` - Comprehensive configuration
- `docs/MCP_INTEGRATION_GUIDE.md` - Tool integration details
- `docs/README.md` - Documentation index

### Implementation Rules

1. **No Trading Logic**: Only include plain-language descriptions in `text` fields
2. **Schema Compliance**: Always validate against the provided schema
3. **Quality Control**: Respect criticism scores and prior art findings
4. **Configuration**: Support per-node customization via environment variables
5. **Logging**: Use the centralized logging system for observability
6. **MCP Tools**: Leverage MCP for all external tool interactions
7. **Fallbacks**: Implement graceful degradation when tools unavailable

### Alpha-Only Mode
- Enforce exactly one alpha (`alphas.new` or `alphas.amend`)
- Enforce exactly one `universe.existing`
- All other model categories must be absent or empty
- Simpler, focused proposals for alpha generation research
