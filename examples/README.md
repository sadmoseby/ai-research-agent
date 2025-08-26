# AI Research Agent Examples

This directory contains example scripts demonstrating various features of the AI Research Agent.

## Available Examples

### Core Usage Examples
- `basic_usage.py` - Basic research workflow example
- `web_research_demo.py` - Web research functionality demonstration

### Configuration Examples
- `multi_provider_setup.py` - Multi-provider LLM configuration examples
- `mcp_configuration.py` - MCP (Model Context Protocol) tool setup
- `node_configuration.py` - Node enable/disable configuration
- `node_config_demo.py` - Interactive node configuration demo

### Advanced Feature Demos
- `component_synthesis_demo.py` - Component-by-component synthesis demonstration
- `multiple_approaches_demo.py` - Multiple research approaches per component
- `prompt_restructure_demo.py` - Updated prompt structure demonstration

## Running Examples

Make sure you have set up your environment variables in `.env`:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  # Optional
export GITHUB_TOKEN="your-github-token"        # Optional
export TAVILY_API_KEY="your-tavily-key"       # Optional
```

Then run any example:

```bash
python examples/basic_usage.py
python examples/multi_provider_setup.py
```

## Configuration Examples

See the individual example files for detailed configuration options and environment variable setups.
