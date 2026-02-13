# Tool Integration Guide

## Overview

The Lean Research Agent uses a **hybrid architecture** combining OpenAI's Responses API (with native web search) and Model Context Protocol (MCP) for standardized tool communication. This provides the best of both worlds: powerful built-in capabilities from OpenAI and extensible tool integration via MCP.

## Architecture Overview

### Primary: OpenAI Responses API
- **Web Search**: Native web search tool via OpenAI
- **Structured Outputs**: JSON schema validation built into API
- **Streaming**: Real-time response streaming
- **Reliability**: Managed by OpenAI infrastructure

### Secondary: MCP Tools
- **Validation**: Schema validation and repair via ValidationMCPTool
- **Filesystem**: File operations and persistence
- **GitHub CLI**: Issue creation via gh CLI tool
- **Extensibility**: Easy addition of custom tools

## What is MCP?

Model Context Protocol is a standardized protocol for AI systems to communicate with external tools. In this system, MCP is used for:

- **Schema Validation**: Validating proposals against JSON schema
- **File Operations**: Filesystem access for persistence
- **Tool Extensibility**: Easy addition of custom tools

## Current Tool Integrations

### OpenAI Responses API (Primary)
- **Web Search**: Comprehensive web search with real-time data
- **Usage**: web_research node for gathering research
- **Features**: Native integration, structured outputs, streaming responses

### MCP Tools (Secondary)

#### Validation Tool
- **Implementation**: ValidationMCPTool in `agent/tools/validation_mcp_tool.py`
- **Usage**: synthesize node for schema validation and repair
- **Features**: JSON schema validation, error reporting, repair suggestions

#### GitHub CLI Integration
- **Implementation**: github_issue node using gh CLI
- **Usage**: Creating GitHub issues from proposals
- **Features**: Issue creation, authentication via GH_TOKEN

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
# Required API Keys
OPENAI_API_KEY=your_key_here        # For web search via Responses API
GITHUB_TOKEN=your_token_here        # Optional, for GitHub issue creation

# Node Control
CRITICISM_ENABLED=true
GITHUB_ISSUE_ENABLED=false

# GitHub Integration (optional)
UPLOAD_TO_GITHUB=false
GITHUB_OWNER=your-org
GITHUB_REPOSITORY=your-repo
```

## Node-Specific Tool Requirements

### Planning Node (`plan`)
- **Purpose**: Create research plans and search strategies
- **Tools**: None specific
- **Integration**: Uses LLM for planning logic

### Web Research Node (`web_research`)
- **Purpose**: Conduct comprehensive web-based research
- **Tools**: OpenAI Responses API with web search
- **Integration**: Native OpenAI web search tool

### Criticism Node (`criticism`)
- **Purpose**: Critical analysis of research proposals
- **Tools**: None specific (uses LLM directly)
- **Integration**: LLM-based evaluation

### Synthesis Node (`synthesize`)
- **Purpose**: Generate structured proposals with validation
- **Tools**: ValidationMCPTool for schema validation
- **Integration**: MCP validation tool + OpenAI structured outputs

### Persistence Node (`persist`)
- **Purpose**: Save proposals to filesystem
- **Tools**: Filesystem operations
- **Integration**: Direct file I/O

### GitHub Issue Node (`github_issue`)
- **Purpose**: Create GitHub issues from proposals
- **Tools**: GitHub CLI (gh command)
- **Integration**: Subprocess call to gh CLI

## Implementation Details

### ValidationMCPTool Usage

The ValidationMCPTool is used in the synthesize node for schema validation:

```python
from agent.tools.validation_mcp_tool import ValidationMCPTool

# Initialize validation tool
validation_tool = ValidationMCPTool(config)

# Validate proposal
result = validation_tool.validate_proposal(proposal_json)

if result["is_valid"]:
    print("Proposal is valid!")
else:
    print(f"Validation errors: {result['errors']}")
```

```python
# Node-specific client with tool filtering
mcp_client = MCPClient(config, node_name="web_research")
available_tools = mcp_client.get_available_tool_names()
```

### OpenAI Responses API Usage

The web_research node uses OpenAI's native web search:

```python
from agent.llm_client import LLMClient

# Initialize LLM client with web search capability
llm_client = LLMClient(config, node_name="web_research")

# Conduct research with web search tool
response = await llm_client.chat_completion(
    messages=[{"role": "user", "content": "Research momentum trading strategies"}],
    tools=["web_search"]  # Enable web search tool
)
```

### Error Handling

```python
try:
    # Attempt validation
    result = validation_tool.validate_proposal(proposal)
    if not result["is_valid"]:
        # Handle validation errors
        errors = result["errors"]
        # Attempt repair...
except Exception as e:
    logger.error(f"Validation failed: {e}")
    # Fallback handling
```

## Benefits of Hybrid Architecture

### OpenAI Responses API
- **Native Web Search**: Built-in, reliable web search capability
- **Structured Outputs**: JSON schema validation at API level
- **Streaming**: Real-time response streaming
- **Managed Infrastructure**: No server management needed

### MCP Tools
- **Validation**: Robust schema validation with detailed error reporting
- **Extensibility**: Easy addition of custom tools
- **Local Tools**: GitHub CLI and filesystem operations
- **Testing**: Easy mocking for development

## Future Extensions

The hybrid architecture supports easy addition of new capabilities:

### Via OpenAI
- **Function Calling**: Custom tools via OpenAI function calling
- **File Search**: Document search capabilities
- **Code Interpreter**: Python execution

### Via MCP
- **Database Connectors**: SQL, NoSQL database access
- **Custom Validators**: Domain-specific validation rules
- **File Processors**: PDF parsing, document analysis

## Troubleshooting

### Common Issues

1. **Validation Fails**: Check JSON schema matches proposal structure
2. **GitHub Issue Creation Fails**: Verify gh CLI is installed and GH_TOKEN is set
3. **Web Search Issues**: Check OPENAI_API_KEY and API limits

### Debug Commands

```bash
# Test validation tool
python -c "from agent.tools.validation_mcp_tool import ValidationMCPTool; from agent.config import Config; t=ValidationMCPTool(Config.from_env()); print('Validation tool ready')"

# Test GitHub CLI
gh --version

# Verify OpenAI API
python -c "import openai; print('OpenAI SDK installed')"
```
