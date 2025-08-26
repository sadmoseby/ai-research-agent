# MCP Tool Integration and Configuration

This document explains how each agent node uses MCP (Model Context Protocol) tools and how to configure tool access per node.

## Overview

Each node in the research agent workflow can be configured with different MCP tools based on its specific needs. This allows for:

1. **Optimized resource usage** - Nodes only get access to tools they need
2. **Better security** - Limit tool access on a per-node basis
3. **Clear tool responsibility** - Each node knows exactly which tools it has available
4. **Informed LLM prompts** - LLMs are told which tools they can use

## Node-Specific Tool Requirements

### Planning Node (`plan`)

**Purpose**: Create research plans and search strategies
**Required Tools**:

- `filesystem` (optional) - For saving/loading planning templates

**LLM Instructions**:

- Told about available tools in prompt
- Can reference tool capabilities when creating research plans

### Web Research Node (`web_research`)

**Purpose**: Conduct web-based research on the idea
**Required Tools**:

- `web_search` - Primary web search via OpenAI MCP server
- `tavily` - Academic and research-focused search
- `filesystem` (optional) - For caching search results

**LLM Instructions**:

- Informed about available search tools
- Can choose optimal search strategy based on available tools
- Falls back gracefully if tools fail

### Prior Art Node (`prior_art`)

**Purpose**: Search for existing implementations and similar approaches
**Required Tools**:

- `github` - Search GitHub repositories for code
- `filesystem` (optional) - For local prior art databases

**LLM Instructions**:

- Told about GitHub search capabilities
- Can adapt search strategy based on tool availability

### Criticism Node (`criticism`)

**Purpose**: Critically evaluate research proposals
**Required Tools**:

- `web_search` (optional) - For additional fact-checking
- `tavily` (optional) - For academic verification
- `filesystem` (optional) - For accessing risk databases

**LLM Instructions**:

- Informed about verification tools available
- Can request additional research if tools available
- Adapts criticism depth based on tool access

### Synthesis Node (`synthesize`)

**Purpose**: Generate structured research proposals
**Required Tools**:

- `web_search` - For additional detail verification
- `github` - For implementation examples
- `tavily` - For academic context
- `filesystem` - For template access and intermediate saves

**LLM Instructions**:

- Told about all available tools for comprehensive synthesis
- Can request additional information during generation
- Uses tools to verify technical details

### Validation Node (`validate`)

**Purpose**: Validate proposals against schema
**Required Tools**:

- `filesystem` - For schema access and validation reports

**LLM Instructions**:

- Basic tool information for schema operations

### Persistence Node (`persist`)

**Purpose**: Save final proposals
**Required Tools**:

- `filesystem` - For saving proposals to disk

**LLM Instructions**:

- Basic file operations information

## Configuration Methods

### Environment Variables

Configure tools per node using environment variables:

```bash
# Planning node tools
export PLAN_MCP_TOOLS="filesystem"

# Web research node tools
export WEB_RESEARCH_MCP_TOOLS="web_search,tavily"

# Prior art node tools
export PRIOR_ART_MCP_TOOLS="github,filesystem"

# Criticism node tools
export CRITICISM_MCP_TOOLS="web_search,tavily"

# Synthesis node tools (all available)
export SYNTHESIZE_MCP_TOOLS="web_search,github,tavily,filesystem"

# Validation and persistence
export VALIDATE_MCP_TOOLS="filesystem"
export PERSIST_MCP_TOOLS="filesystem"
```

### Programmatic Configuration

```python
from agent.config import Config

config = Config.from_env()

# Get node-specific configuration
web_research_config = config.get_node_config("web_research")
print(f"Web research tools: {web_research_config['mcp_tools']}")

# Check if a node has a specific tool
from agent.tools.mcp_client import MCPClient
client = MCPClient(config, node_name="web_research")
if client.has_tool("web_search"):
    print("Web search available for web research node")
```

## Prompt Integration

Each node's prompts now include tool information:

```python
# Example from synthesis node
system_prompt = ResearchPrompts.SYNTHESIS_SYSTEM_PROMPT.format(
    alpha_mode_note=alpha_mode_note,
    repair_context=repair_context,
    available_tools=ResearchPrompts.format_available_tools(available_tools)
)
```

This tells the LLM:

- Which tools are available
- What each tool can do
- How to request tool usage

## Tool Usage Patterns

### Fallback Behavior

Nodes gracefully handle missing tools:

```python
# Web research with fallback
if mcp_client.has_tool("web_search"):
    results = await mcp_client.web_search(query)
elif mcp_client.has_tool("tavily"):
    results = await mcp_client.tavily_search(query)
else:
    # Generate error placeholder
    results = [{"error": "No search tools available"}]
```

### Tool Combination

Nodes can combine multiple tools:

```python
# Prior art search using multiple tools
github_results = []
if mcp_client.has_tool("github"):
    github_results = await mcp_client.github_search(query)

if mcp_client.has_tool("filesystem"):
    cached_results = await mcp_client.read_cache(query)
    github_results.extend(cached_results)
```

### LLM Tool Requests

LLMs can request tool usage during generation:

```
Available MCP Tools:
- web_search: Web search for research and market data
- github: GitHub code search for prior art analysis
- tavily: Academic research search via Tavily

If you need additional information during synthesis, use the available MCP tools to:
- Verify technical details via web search
- Check for additional prior art via GitHub search
- Access academic sources via Tavily
```

## Default Tool Assignments

If no specific configuration is provided, nodes get these default tools:

- **Planning**: No tools (planning is primarily logic-based)
- **Web Research**: web_search, tavily (if API keys available)
- **Prior Art**: github (if GitHub token available)
- **Criticism**: web_search (for fact-checking)
- **Synthesis**: All available tools
- **Validation**: filesystem
- **Persistence**: filesystem

## Security Considerations

1. **API Key Isolation**: Each tool requires its own API key
2. **Per-Node Limits**: Nodes only get tools they need
3. **Graceful Degradation**: System works even with limited tools
4. **Audit Trail**: Tool usage is logged in state

## Monitoring and Debugging

Track tool usage in the research state:

```python
state = {
    "mcp_tools_available": ["web_search", "tavily"],
    "mcp_tools_used": ["web_search"],
    # ... other state
}
```

This helps with:

- Understanding which tools were actually used
- Debugging tool failures
- Optimizing tool assignments
- Cost tracking per tool

## Best Practices

1. **Minimal Tool Sets**: Only assign tools that nodes actually need
2. **Fallback Planning**: Always have fallback behavior for missing tools
3. **Informed Prompts**: Tell LLMs about available tools
4. **Graceful Errors**: Handle tool failures without breaking the workflow
5. **State Tracking**: Record tool usage for debugging and optimization
