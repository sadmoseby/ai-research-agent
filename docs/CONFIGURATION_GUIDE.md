# Configuration Guide

## Overview

The Lean Research Agent supports extensive configuration through environment variables, allowing customization of LLM providers, node behavior, MCP tools, and workflow settings.

## Configuration Hierarchy

1. **Global Defaults**: Base settings applied to all components
2. **Provider-Specific**: Settings for individual LLM providers
3. **Node-Specific**: Per-node overrides for models, tools, and behavior
4. **Runtime**: Command-line arguments and temporary overrides

## Core Configuration

### Required API Keys

```bash
# Required for all functionality
OPENAI_API_KEY="your-openai-key"

# Optional but recommended
GITHUB_TOKEN="your-github-token"      # For prior art checking
TAVILY_API_KEY="your-tavily-key"      # For fallback web search
ANTHROPIC_API_KEY="your-anthropic-key"  # For Claude models
GOOGLE_API_KEY="your-google-key"      # For Gemini models
```

### Global LLM Settings

```bash
# Default provider and model
DEFAULT_LLM_PROVIDER="openai"
MODEL="gpt-4o"
TEMPERATURE="0.7"
MAX_TOKENS="4000"

# Global MCP settings
USE_MCP="true"
```

## Multi-Provider Configuration

### Provider-Specific Models

```bash
# OpenAI models
OPENAI_MODEL="gpt-4o"
OPENAI_TEMPERATURE="0.7"
OPENAI_MAX_TOKENS="4000"

# Anthropic models
ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
ANTHROPIC_TEMPERATURE="0.7"
ANTHROPIC_MAX_TOKENS="4000"

# Gemini models
GEMINI_MODEL="gemini-1.5-pro"
GEMINI_TEMPERATURE="0.7"
GEMINI_MAX_TOKENS="4000"

# Ollama models (local)
OLLAMA_MODEL="llama3.1:8b"
OLLAMA_BASE_URL="http://localhost:11434"
```

### Node-Specific Provider Selection

```bash
# Use different providers for different tasks
PLAN_PROVIDER="anthropic"           # Claude for planning
WEB_RESEARCH_PROVIDER="openai"      # GPT for web research
PRIOR_ART_PROVIDER="gemini"         # Gemini for code analysis
CRITICISM_PROVIDER="anthropic"      # Claude for criticism
SYNTHESIZE_PROVIDER="openai"        # GPT for synthesis
VALIDATE_PROVIDER="gemini"          # Gemini for validation
PERSIST_PROVIDER="ollama"           # Local model for persistence
```

## Per-Node Configuration

### Model and Parameter Overrides

```bash
# Override global settings for specific nodes
PLAN_MODEL="gpt-3.5-turbo"
PLAN_TEMPERATURE="0.1"              # Lower for more focused planning

WEB_RESEARCH_MODEL="gpt-4o"
WEB_RESEARCH_MAX_TOKENS="8000"      # More tokens for research

CRITICISM_TEMPERATURE="0.9"         # Higher for creative criticism
SYNTHESIZE_MAX_TOKENS="6000"        # Adequate for proposal generation
```

### MCP Tool Access Control

```bash
# Per-node MCP tool access
# Per-Node tool configuration (OpenAI Responses API with web search)
WEB_RESEARCH_TOOLS="web_search"    # OpenAI web search capability
CRITICISM_TOOLS=""                 # No specific tools needed
SYNTHESIZE_TOOLS="web_search"      # For structured outputs
PERSIST_TOOLS="filesystem"         # File system operations
GITHUB_ISSUE_TOOLS="gh_cli"        # GitHub CLI for issue creation
```

## Node Enable/Disable Configuration

### Selective Node Execution

```bash
# Disable specific nodes (all enabled by default)
PLAN_ENABLED=true
WEB_RESEARCH_ENABLED=true
CRITICISM_ENABLED=false             # Skip quality checks for speed
SYNTHESIZE_ENABLED=true             # Core synthesis - keep enabled
PERSIST_ENABLED=true                # File persistence - keep enabled
GITHUB_ISSUE_ENABLED=false          # Optional GitHub integration
```

### Configuration Patterns

#### Fast Prototyping Mode
```bash
CRITICISM_ENABLED=false
WEB_RESEARCH_MAX_TOKENS=2000
```

#### Comprehensive Research Mode
```bash
# All nodes enabled (default)
WEB_RESEARCH_MAX_TOKENS=8000
CRITICISM_TEMPERATURE=0.9
```

#### Debug Mode
```bash
LOG_LEVEL=DEBUG
LOG_TO_FILE=true
```

## Logging Configuration

### Basic Logging Setup

```bash
LOG_LEVEL="INFO"                    # DEBUG, INFO, WARNING, ERROR
LOG_TO_FILE=false                   # Enable file logging
LOG_FILE_PATH="research_agent.log"
MAX_LOG_FILE_SIZE=10485760          # 10MB
BACKUP_COUNT=3                      # Number of backup files

# Component-specific logging
ENABLE_NODE_LOGGING=true            # Log individual node execution
ENABLE_GRAPH_LOGGING=true           # Log workflow execution
```

### Advanced Logging

```bash
# Custom log format
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Disable specific loggers if needed
DISABLE_MCP_LOGGING=false
DISABLE_PROVIDER_LOGGING=false
```

## Workflow Configuration

### Conditional Restart Settings

```bash
# Criticism scoring thresholds
MIN_VIABILITY_SCORE=51              # Minimum score to proceed
MAX_PLANNING_ITERATIONS=3           # Maximum restart attempts
ENABLE_CRITICISM_RESTART=true       # Allow criticism-based restarts
```

### Alpha-Only Mode Configuration

```bash
# Force alpha-only mode for all proposals
FORCE_ALPHA_ONLY=false

# Alpha-only specific settings
ALPHA_ONLY_MAX_TOKENS=3000          # Smaller proposals
ALPHA_ONLY_TEMPERATURE=0.5          # More focused
```

## Programmatic Configuration

### Using Config Class

```python
from agent.config import Config

# Load from environment
config = Config.from_env()

# Override specific settings
config.set_node_config("synthesize",
                      model="claude-3-5-sonnet-20241022",
                      temperature=0.8,
                      max_tokens=5000)

# Check configuration
print(f"Enabled nodes: {config.get_enabled_nodes()}")
print(f"Web research tools: {config.get_mcp_tools_for_node('web_research')}")
```

### Custom Configuration Loading

```python
import os
from agent.config import Config

# Set custom environment
os.environ.update({
    "SYNTHESIZE_PROVIDER": "anthropic",
    "CRITICISM_ENABLED": "false",
    "LOG_LEVEL": "DEBUG"
})

config = Config.from_env()
```

## Environment File Setup

### .env File Example

```bash
# Core API Keys
OPENAI_API_KEY=sk-your-openai-key
GITHUB_TOKEN=ghp_your-github-token  # Optional, for issue creation
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Provider Configuration
DEFAULT_LLM_PROVIDER=openai
SYNTHESIZE_PROVIDER=anthropic
CRITICISM_PROVIDER=anthropic

# Node Configuration
CRITICISM_ENABLED=true
GITHUB_ISSUE_ENABLED=false
WEB_RESEARCH_MAX_TOKENS=6000

# GitHub Integration (optional)
UPLOAD_TO_GITHUB=false
GITHUB_OWNER=your-org
GITHUB_REPOSITORY=your-repo

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false
```

## Validation and Troubleshooting

### Configuration Validation

```python
from agent.config import Config

try:
    config = Config.from_env()
    print("✅ Configuration valid")
    print(f"Enabled nodes: {config.get_enabled_nodes()}")
    print(f"Default provider: {config.llm.provider}")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

### Common Configuration Issues

1. **Missing API Keys**: Ensure required keys are set
2. **Invalid Provider**: Check provider name spelling
3. **Model Not Available**: Verify model exists for provider
4. **Tool Access Denied**: Check MCP tool configuration
5. **No Nodes Enabled**: At least one node must be enabled

### Debug Commands

```bash
# Check current configuration
python -c "from agent.config import Config; c=Config.from_env(); print('Providers:', c.get_available_providers())"

# Test specific node configuration
python -c "from agent.config import Config; c=Config.from_env(); print('Node config:', c.for_node('synthesize'))"

# Check MCP tool availability
python -c "from agent.tools.mcp_client import MCPClient; from agent.config import Config; c=Config.from_env(); client=MCPClient(c, 'web_research'); print('Tools:', client.get_available_tool_names())"
```

## Best Practices

### Development
- Use `.env` file for local development
- Enable debug logging during development
- Disable expensive nodes for faster iteration

### Production
- Use environment variables, not `.env` files
- Enable all quality nodes (criticism)
- Configure appropriate logging levels
- Set up log rotation for file logging
- Configure GitHub integration if needed

### Performance
- Use faster models for less critical nodes
- Adjust token limits based on node requirements
- Disable unused MCP tools to reduce overhead
- Consider local models (Ollama) for simple tasks
