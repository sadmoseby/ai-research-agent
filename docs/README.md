# Documentation Index

## Quick Start
- [README.md](../README.md) - Main project overview and basic usage
- [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md) - Comprehensive configuration instructions
- [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) - System architecture and components
- [TESTING.md](./TESTING.md) - Comprehensive testing guide and development workflow

## Core Features

### Workflow and Nodes
- [CRITICISM_NODE.md](./CRITICISM_NODE.md) - Quality control and evaluation system
- [CONDITIONAL_RESTART.md](./CONDITIONAL_RESTART.md) - Automatic restart logic for quality assurance
- [NODE_ENABLE_DISABLE.md](./NODE_ENABLE_DISABLE.md) - Selective node execution for different use cases
- [GITHUB_ISSUE_NODE.md](./GITHUB_ISSUE_NODE.md) - GitHub issue creation from proposals

### Tool Integration
- [MCP_INTEGRATION_GUIDE.md](./MCP_INTEGRATION_GUIDE.md) - Hybrid architecture with OpenAI + MCP tools
- [MULTI_PROVIDER_IMPLEMENTATION.md](./MULTI_PROVIDER_IMPLEMENTATION.md) - Technical details of multi-LLM support

### System Components
- [LOGGING_SYSTEM.md](./LOGGING_SYSTEM.md) - Comprehensive logging configuration and usage
- [PROMPT_ORGANIZATION.md](./PROMPT_ORGANIZATION.md) - Centralized prompt management

## Development & Testing
- [TESTING.md](./TESTING.md) - Complete testing infrastructure guide
- [TESTING_IMPLEMENTATION_SUMMARY.md](./TESTING_IMPLEMENTATION_SUMMARY.md) - Testing implementation status and achievements

## Use Case Guides

### Development
- Enable debug logging: `LOG_LEVEL=DEBUG`
- Fast prototyping: `CRITICISM_ENABLED=false`
- Node isolation: Disable specific nodes for testing

### Production
- Full quality pipeline: All nodes enabled (default)
- Multi-provider setup: Different LLMs for different tasks
- Monitoring: File logging with rotation enabled

### GitHub Integration
- Issue creation: `UPLOAD_TO_GITHUB=true`
- Configure repository: `GITHUB_OWNER=org GITHUB_REPOSITORY=repo`
- Requires: GitHub token and gh CLI installed

## Configuration Quick Reference

### Essential Environment Variables
```bash
# Required
OPENAI_API_KEY="your-key"

# Optional
GITHUB_TOKEN="your-token"
ANTHROPIC_API_KEY="your-key"

# Node control
CRITICISM_ENABLED=true
GITHUB_ISSUE_ENABLED=false

# Provider selection
SYNTHESIZE_PROVIDER="anthropic"
WEB_RESEARCH_PROVIDER="openai"
```

### Common Commands
```bash
# Basic proposal
python main.py propose --idea "momentum strategy"

# Alpha-only proposal
python main.py propose --idea "mean reversion" --alpha-only

# Custom output
python main.py propose --idea "volatility arbitrage" --slug "vol_arb"
```

## Architecture Summary

### Workflow
```
START → plan → web_research → criticism → synthesize → persist → github_issue → END
```

### Key Features
- **Conditional Restart**: Quality-based planning iteration
- **Multi-Provider LLM**: OpenAI, Anthropic, Gemini, Ollama support
- **MCP Integration**: Standardized tool communication
- **Node Configuration**: Per-node settings and selective execution
- **Schema Validation**: Strict JSON schema compliance

### File Structure
```
agent/
├── config.py          # Configuration management
├── graph.py           # LangGraph workflow
├── state.py           # State definitions
├── prompts.py         # Centralized prompts
├── llm_client.py      # Multi-provider LLM client
├── nodes/             # Workflow nodes
│   ├── plan.py
│   ├── web_research.py
│   ├── prior_art.py
│   ├── criticism.py
│   ├── synthesize.py
│   ├── validate.py
│   └── persist.py
└── tools/             # External integrations
    ├── mcp_client.py
    ├── github_api.py
    └── tavily_tool.py
```

## Troubleshooting

### Common Issues
1. **Missing API Keys**: Check environment variables
2. **Tool Not Available**: Verify MCP configuration
3. **Validation Errors**: Check schema compliance
4. **No Output**: Ensure at least one node is enabled

### Debug Commands
```bash
# Check configuration
python -c "from agent.config import Config; print(Config.from_env().get_enabled_nodes())"

# Test MCP tools
python -c "from agent.tools.mcp_client import MCPClient; from agent.config import Config; print(MCPClient(Config.from_env(), 'web_research').get_available_tool_names())"

# Validate schema
python -c "from agent.config import Config; import json; schema=Config.from_env().get_schema(); print('Schema valid')"
```

## Getting Help

### For Configuration Issues
- Review [CONFIGURATION_GUIDE.md](./CONFIGURATION_GUIDE.md)
- Check environment variable syntax
- Verify API key validity

### For Workflow Issues
- Check [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)
- Enable debug logging
- Review node-specific documentation

### For Tool Integration Issues
- See [MCP_INTEGRATION_GUIDE.md](./MCP_INTEGRATION_GUIDE.md)
- Check tool availability
- Verify API credentials
