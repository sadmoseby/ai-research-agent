# MCP Integration Documentation

## Model Context Protocol (MCP) Integration

The Lean Research Agent now uses **Model Context Protocol (MCP)** for all external tool integrations, providing standardized, secure, and efficient communication with external services.

## What is MCP?

Model Context Protocol is a standardized protocol for secure communication between AI systems and external tools/services. It provides:

- **Standardized Interface**: Consistent API across different tools
- **Security**: Controlled access to external resources
- **Efficiency**: Optimized communication patterns
- **Extensibility**: Easy addition of new tools and services

## MCP Integration in the Agent

### Current MCP Integrations

1. **Web Search** (`web_search_node`)
   - Uses OpenAI MCP server for web search capabilities
   - Fallback to Tavily MCP server if available
   - Replaces direct OpenAI API calls with MCP protocol

2. **GitHub Search** (`prior_art_node`)
   - Uses GitHub MCP server for code repository search
   - Provides prior art checking capabilities
   - Replaces direct GitHub API calls with MCP protocol

3. **Proposal Generation** (`synthesize_node`)
   - Uses OpenAI MCP server for structured output generation
   - Maintains JSON schema validation through MCP
   - Provides fallback to direct API calls if MCP unavailable

### Configuration

MCP integration is controlled via environment variables:

```bash
# Enable/disable MCP (default: true)
USE_MCP=true

# API keys still required for MCP servers
OPENAI_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
TAVILY_API_KEY=your_key_here
```

### MCP Client Implementation

The `MCPClient` class (`agent/tools/mcp_client.py`) provides:

- **Unified Interface**: Single client for all MCP operations
- **Error Handling**: Graceful fallback when MCP servers unavailable
- **Resource Management**: Proper connection lifecycle management
- **Tool Abstraction**: High-level methods for common operations

### Key Benefits

1. **Standardization**: All tools use the same protocol interface
2. **Security**: MCP provides controlled access to external resources
3. **Reliability**: Built-in error handling and fallback mechanisms
4. **Maintainability**: Easier to add/remove/update tool integrations
5. **Future-Proof**: MCP is designed for evolving AI tool ecosystems

### Development Notes

When adding new tools or modifying existing ones:

1. **Use MCP First**: Always prefer MCP integration over direct API calls
2. **Provide Fallbacks**: Include graceful degradation when MCP unavailable
3. **Follow Patterns**: Use the established patterns in `MCPClient`
4. **Test Both Modes**: Ensure functionality works with and without MCP

### Current Limitations

- **Simulated Servers**: Some MCP servers are simulated for development
- **Fallback Required**: Direct API calls still needed as backup
- **Setup Complexity**: MCP servers require proper installation/configuration

### Future Enhancements

1. **Additional MCP Servers**: Integration with more specialized tools
2. **Custom MCP Servers**: Development of domain-specific MCP servers
3. **Enhanced Error Handling**: More sophisticated fallback strategies
4. **Performance Optimization**: Caching and connection pooling for MCP calls

## Usage Examples

### Web Search via MCP

```python
mcp_client = MCPClient(config)
results = await mcp_client.web_search("quantitative finance research")
await mcp_client.close()
```

### GitHub Search via MCP

```python
mcp_client = MCPClient(config)
repos = await mcp_client.github_search("trading algorithm python")
await mcp_client.close()
```

### Proposal Generation via MCP

```python
mcp_client = MCPClient(config)
proposal = await mcp_client.generate_proposal(
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    schema=json_schema
)
await mcp_client.close()
```

This MCP integration ensures the Lean Research Agent follows modern AI architecture patterns while maintaining backward compatibility and reliability.
