# MCP Tool Access Configuration Guide

This document explains how to configure MCP (Model Context Protocol) tool access per node in the Lean Research Agent.

## Overview

The system now uses a **global MCP client registry** with **per-node tool access control**. This means:

1. **Global MCP Clients**: All MCP client configurations are defined globally and shared
2. **Node Tool Access**: Each node specifies which global MCP tools it has access to
3. **Clean Separation**: Client configuration is separate from access control

## Architecture

### Global MCP Clients

- Defined once in the global configuration
- Shared across all nodes
- Can be customized via environment variables

### Node Tool Access

- Each node specifies which MCP tools it can use
- References global MCP clients by name
- Lightweight and flexible

## Configuration Structure

### MCPClientConfig (Global)

```python
@dataclass
class MCPClientConfig:
    name: str  # Unique identifier (e.g., "web_search", "github")
    server_type: str  # Type of MCP server
    enabled: bool = True
    command: Optional[str] = None  # Command to start the server
    args: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    api_key_env: Optional[str] = None
    config_params: Dict[str, any] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
```

### NodeConfig (Per-Node)

```python
@dataclass
class NodeConfig:
    model: Optional[str] = None
    use_mcp: Optional[bool] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    mcp_tools: List[str] = field(default_factory=list)  # Tool names this node can access
```

## Environment Variable Configuration

### Node MCP Tool Access

Specify which global MCP tools a node can access:

```bash
# Format: {NODE_NAME_UPPER}_MCP_TOOLS = "tool1,tool2,tool3"
export WEB_RESEARCH_MCP_TOOLS="web_search,tavily,github"
export SYNTHESIZE_MCP_TOOLS="web_search"
export PRIOR_ART_MCP_TOOLS="github"
export PLAN_MCP_TOOLS="web_search,filesystem"
```

### Global MCP Client Overrides

Override global MCP client settings:

```bash
# Format: MCP_{CLIENT_NAME_UPPER}_{SETTING}
export MCP_TAVILY_TIMEOUT="60"
export MCP_TAVILY_ENABLED="true"
export MCP_WEB_SEARCH_MAX_RETRIES="5"

# JSON configuration parameters
export MCP_TAVILY_CONFIG='{"search_depth": "deep", "include_raw_content": true}'
export MCP_GITHUB_CONFIG='{"repo_access": "all", "include_forks": false}'
```

## Available Global MCP Clients

The system automatically creates these global MCP clients based on available API keys:

### 1. Web Search

- **Name**: `web_search`
- **Type**: `web_search`
- **Requires**: `OPENAI_API_KEY`
- **Command**: `npx @modelcontextprotocol/server-web-search`

### 2. GitHub

- **Name**: `github`
- **Type**: `github`
- **Requires**: `GITHUB_TOKEN`
- **Command**: `npx @modelcontextprotocol/server-github`

### 3. Tavily

- **Name**: `tavily`
- **Type**: `tavily`
- **Requires**: `TAVILY_API_KEY`
- **Command**: `npx @modelcontextprotocol/server-tavily`

### 4. Filesystem

- **Name**: `filesystem`
- **Type**: `filesystem`
- **Requires**: None (always available)
- **Command**: `npx @modelcontextprotocol/server-filesystem`

## Programmatic Configuration

### Managing Global MCP Clients

```python
from agent.config import Config, MCPClientConfig

config = Config.from_env()

# Add a custom global MCP client
database_client = MCPClientConfig(
    name="database",
    server_type="database",
    command="python",
    args=["-m", "mcp_servers.database"],
    config_params={
        "connection_string": "postgresql://localhost/research",
        "read_only": True
    }
)

config.add_global_mcp_client(database_client)

# Get all global clients
global_clients = config.get_global_mcp_clients()

# Remove a global client (also removes from all nodes)
config.remove_global_mcp_client("database")
```

### Managing Node Tool Access

```python
# Add tool access to a node
config.add_mcp_tool_to_node("synthesize", "database")

# Remove tool access from a node
config.remove_mcp_tool_from_node("web_research", "tavily")

# Get tools available to a node
tools = config.get_node_mcp_tools("web_research")
# Returns: ["web_search", "github"]

# Get actual client configurations for a node
clients = config.get_node_mcp_clients("web_research")
# Returns: [MCPClientConfig(...), MCPClientConfig(...)]
```

## Usage in Nodes

Nodes can access their MCP tools through the standard configuration:

```python
def my_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    # Get node configuration (includes tool access)
    node_config = config.get_node_config("my_node_name")

    # Available tool names
    available_tools = node_config["mcp_tools"]

    # Actual client configurations
    available_clients = node_config["mcp_clients"]

    # Use specific tools
    for client in available_clients:
        if client.name == "web_search" and client.enabled:
            # Use web search
            pass
        elif client.name == "github" and client.enabled:
            # Use GitHub search
            pass
```

## Example Configurations

### Research Node (Web Research)

```bash
export WEB_RESEARCH_MCP_TOOLS="web_search,tavily,github"
export MCP_TAVILY_CONFIG='{"search_depth": "deep"}'
```

### Code Analysis Node (Prior Art)

```bash
export PRIOR_ART_MCP_TOOLS="github"
export MCP_GITHUB_CONFIG='{"repo_access": "all"}'
```

### Lightweight Node (Synthesize)

```bash
export SYNTHESIZE_MCP_TOOLS="web_search"
```

### Filesystem Operations Node

```bash
export PERSIST_MCP_TOOLS="filesystem"
export MCP_FILESYSTEM_CONFIG='{"allowed_directories": ["/workspace", "/data"]}'
```

## Default Behavior

### Global Clients

- Automatically created based on available API keys
- `web_search` if `OPENAI_API_KEY` is available
- `github` if `GITHUB_TOKEN` is available
- `tavily` if `TAVILY_API_KEY` is available
- `filesystem` always available

### Node Tool Access

- If no specific tools configured and `use_mcp=true`: All available global clients
- If `use_mcp=false`: No MCP tools available
- If specific tools configured: Only those tools

## Benefits of This Approach

1. **DRY Principle**: Client configurations defined once, used many times
2. **Flexibility**: Easy to grant/revoke tool access per node
3. **Maintainability**: Single place to update client configurations
4. **Security**: Fine-grained access control per node
5. **Scalability**: Easy to add new tools or nodes

## Migration Guide

If upgrading from the previous system:

**Old Way** (per-node clients):

```bash
export WEB_RESEARCH_MCP_CLIENTS="web_search,github"
export WEB_RESEARCH_GITHUB_TIMEOUT="45"
```

**New Way** (global clients + node access):

```bash
export WEB_RESEARCH_MCP_TOOLS="web_search,github"  # What tools this node can use
export MCP_GITHUB_TIMEOUT="45"  # Global client configuration
```

## Troubleshooting

### Common Issues

1. **Tool Not Available**: Check that the tool exists in global clients
2. **Access Denied**: Verify the node has access to the tool via `MCP_TOOLS`
3. **Client Not Working**: Check global client configuration and API keys

### Debug Commands

```python
# List all global clients
config = Config.from_env()
print("Global clients:", list(config.get_global_mcp_clients().keys()))

# Check node tool access
for node in config.get_all_node_names():
    tools = config.get_node_mcp_tools(node)
    print(f"{node}: {tools}")
```
