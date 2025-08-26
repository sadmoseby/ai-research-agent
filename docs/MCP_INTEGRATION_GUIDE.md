# MCP (Model Context Protocol) Integration Guide

## Overview

The Lean Research Agent uses Model Context Protocol (MCP) for standardized communication with external tools and services. This provides consistent APIs, security controls, and extensibility across different tool types.

## What is MCP?

Model Context Protocol is a standardized protocol for AI systems to communicate with external tools. It offers:

- **Standardized Interface**: Consistent API across different tools
- **Security**: Controlled access to external resources
- **Efficiency**: Optimized communication patterns
- **Extensibility**: Easy addition of new tools and services

## Current MCP Integrations

### Web Search Tools
- **OpenAI MCP Server**: Primary web search via OpenAI's web search tool
- **Tavily MCP Server**: Academic and research-focused search fallback
- **Usage**: web_research node, fallback search capabilities

### GitHub Integration
- **GitHub MCP Server**: Code repository search for prior art checking
- **Usage**: prior_art node for finding existing implementations
- **Features**: Repository discovery, code analysis, similarity assessment

### Proposal Generation
- **OpenAI MCP Server**: Structured output generation with JSON schema
- **Usage**: synthesize node for proposal generation
- **Features**: Schema validation, structured outputs, fallback to direct API

## Architecture

### Global MCP Client Registry
- **File**: `agent/tools/mcp_client.py`
- **Purpose**: Centralized management of all MCP client connections
- **Features**: Client caching, availability checking, error handling

### Per-Node Tool Access Control
- **Configuration**: Each node specifies which MCP tools it can access
- **Benefits**: Security, resource optimization, clear responsibilities
- **Implementation**: Node-specific client initialization with tool filtering

## Configuration

### Global MCP Client Configuration

```python
@dataclass
class MCPClientConfig:
    name: str                    # Unique identifier (e.g., "web_search", "github")
    server_type: str            # Type of MCP server
    enabled: bool = True
    command: Optional[str] = None       # Command to start the server
    args: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    api_key_env: Optional[str] = None
    config_params: Dict[str, any] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
```

### Per-Node Tool Access

```python
@dataclass
class NodeConfig:
    enabled: bool = True
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    use_mcp: bool = True
    mcp_tools: List[str] = field(default_factory=list)  # Which MCP tools this node can access
    provider: Optional[str] = None
```

### Environment Variables

```bash
# Global MCP Control
USE_MCP=true

# API Keys (still required for MCP servers)
OPENAI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
TAVILY_API_KEY=your_key_here

# Per-Node Tool Access
WEB_RESEARCH_MCP_TOOLS="web_search,tavily"
PRIOR_ART_MCP_TOOLS="github"
SYNTHESIZE_MCP_TOOLS="web_search"
```

## Node-Specific Tool Requirements

### Planning Node (`plan`)
- **Purpose**: Create research plans and search strategies
- **Required Tools**: `filesystem` (optional)
- **MCP Usage**: Limited, mainly for template storage

### Web Research Node (`web_research`)
- **Purpose**: Conduct web-based research
- **Required Tools**: `web_search` (primary), `tavily` (fallback)
- **MCP Usage**: Heavy usage for search operations

### Prior Art Node (`prior_art`)
- **Purpose**: Search for existing implementations
- **Required Tools**: `github` (primary)
- **MCP Usage**: GitHub API integration for code search

### Criticism Node (`criticism`)
- **Purpose**: Critical analysis of research proposals
- **Required Tools**: None specific (uses LLM directly)
- **MCP Usage**: Minimal, mainly for context storage

### Synthesis Node (`synthesize`)
- **Purpose**: Generate structured proposals
- **Required Tools**: `web_search` (for structured outputs)
- **MCP Usage**: OpenAI MCP for structured generation

### Validation Node (`validate`)
- **Purpose**: Schema validation and repair
- **Required Tools**: None specific
- **MCP Usage**: None (uses jsonschema library)

### Persistence Node (`persist`)
- **Purpose**: Save research proposals and final workflow state to disk
- **Required Tools**: `filesystem` (optional)
- **MCP Usage**: Minimal, file operations
- **Outputs**: Two files - `{slug}.json` (proposal) and `{slug}_state.json` (workflow state)

## Implementation Details

### MCP Client Initialization

```python
# Node-specific client with tool filtering
mcp_client = MCPClient(config, node_name="web_research")
available_tools = mcp_client.get_available_tool_names()
```

### Tool Availability Checking

```python
# Check if specific tool is available
if mcp_client.has_tool("web_search"):
    # Use MCP tool
    result = await mcp_client.call_tool("web_search", params)
else:
    # Fallback to direct API
    result = await fallback_search(query)
```

### Error Handling and Fallbacks

```python
try:
    # Attempt MCP tool usage
    result = await mcp_client.use_web_search(query)
except MCPToolError:
    # Fall back to direct API calls
    result = await direct_search_api(query)
```

## Tool Descriptions for LLMs

When nodes use MCP tools, the LLM is informed about available tools:

```python
def format_available_tools(tools: List[str]) -> str:
    """Format tool descriptions for LLM prompts."""
    descriptions = {
        "web_search": "Search the web for current information and research",
        "github": "Search GitHub repositories for code and implementations",
        "tavily": "Academic and research-focused web search",
        "filesystem": "Read and write files for data persistence"
    }
    return "\n".join([f"- {tool}: {descriptions.get(tool, 'Tool description not available')}"
                     for tool in tools])
```

## Benefits of MCP Integration

### For Developers
- **Consistent APIs**: Same interface pattern across all tools
- **Easy Testing**: Mock MCP servers for development
- **Clear Dependencies**: Explicit tool requirements per node

### For Users
- **Reliability**: Standardized error handling and retries
- **Security**: Controlled tool access and permissions
- **Performance**: Optimized communication protocols

### For Operations
- **Monitoring**: Centralized tool usage tracking
- **Configuration**: Unified tool configuration system
- **Debugging**: Clear tool interaction logs

## Future Extensions

The MCP architecture supports easy addition of new tools:

- **Database Connectors**: SQL, NoSQL database access
- **APIs Services**: Financial data APIs, market data feeds
- **File Processors**: PDF parsing, document analysis
- **Calculation Engines**: Mathematical computation services

## Troubleshooting

### Common Issues

1. **Tool Not Available**: Check MCP server configuration and API keys
2. **Permission Denied**: Verify node has access to required tools
3. **Connection Timeout**: Adjust timeout settings in MCP configuration
4. **Fallback Behavior**: Ensure fallback mechanisms are properly configured

### Debug Commands

```bash
# Check MCP tool availability
python -c "from agent.tools.mcp_client import MCPClient; print(MCPClient.check_availability())"

# Test specific tool access
python -c "from agent.config import Config; c=Config.from_env(); print(c.get_mcp_tools_for_node('web_research'))"
```
