# Lean Research Agent - Architecture Overview

## Current System Architecture

The Lean Research Agent is a comprehensive research workflow system built on LangGraph with advanced features for generating quantitative finance research proposals.

## Core Components

### 1. Workflow Engine (LangGraph)
- **File**: `agent/graph.py`
- **Features**: Checkpointed state management, conditional routing, node enable/disable
- **Nodes**: plan → web_research → criticism → synthesize → persist → github_issue

### 2. Configuration System
- **File**: `agent/config.py`
- **Features**: Global and per-node configuration, multi-provider LLM support, MCP tool access control
- **Environment**: Extensive environment variable support for all settings

### 3. State Management
- **File**: `agent/state.py`
- **Features**: Typed state with workflow tracking, tool usage tracking, criticism scores

### 4. Node System
- **Directory**: `agent/nodes/`
- **Files**: plan.py, web_research.py, criticism.py, synthesize.py, persist.py, github_issue.py
- **Features**: Individual node configuration, OpenAI Responses API with web search, comprehensive logging

### 5. Tool Integration
- **OpenAI Responses API**: Web search tool for research gathering
- **GitHub CLI**: Issue creation via gh CLI tool
- **Features**: Direct API integration, structured outputs, fallback mechanisms

### 6. LLM Client System
- **File**: `agent/llm_client.py`
- **Features**: Multi-provider support (OpenAI, Anthropic, Gemini, Ollama), unified API, structured outputs

### 7. Prompt Management
- **File**: `agent/prompts.py`
- **Features**: Centralized prompt organization, tool-aware prompts, context formatting

## Key Features

### Conditional Restart Logic
- **Criticism Score Restart**: Triggered when viability score < 51/100
- **Iteration Limits**: Maximum 3 planning iterations to prevent infinite loops
- **Quality Improvement**: Each iteration refines approach based on identified issues

### Node Enable/Disable System
- **Selective Execution**: Enable/disable individual workflow nodes
- **Automatic Routing**: Graph automatically routes around disabled nodes
- **Use Cases**: Fast prototyping, debugging, resource management

### Multi-Provider LLM Support
- **Providers**: OpenAI, Anthropic (Claude), Google (Gemini), Ollama (local)
- **Per-Node Configuration**: Different providers for different tasks
- **Fallback Logic**: Automatic provider availability detection

### OpenAI Integration
- **Responses API**: Comprehensive web search with structured outputs
- **Web Search Tool**: Direct access to current information
- **Structured Outputs**: JSON schema validation built into API calls

### Comprehensive Logging
- **Graph-Level**: Workflow execution, routing decisions
- **Node-Level**: Individual node execution, tool usage, errors
- **Configurable**: DEBUG, INFO, WARNING, ERROR levels with file output

## Workflow Details

### Standard Flow
```
START → plan → web_research → criticism → synthesize → persist → github_issue → END
```

### Conditional Routing
- **criticism** can restart planning if low viability score
- **synthesize** includes built-in validation with automatic retry
- **persist** conditionally routes to github_issue if enabled

### Alpha-Only Mode
- Enforces exactly one alpha (new or amend) and one existing universe
- Simpler, focused proposals for alpha generation research

## Configuration Examples

### Basic Setup
```bash
export OPENAI_API_KEY="your-key"  # Required
export GITHUB_TOKEN="your-token"  # Optional, for issue creation
```

### Node-Specific Configuration
```bash
export SYNTHESIZE_PROVIDER="anthropic"
export WEB_RESEARCH_PROVIDER="openai"
export CRITICISM_TEMPERATURE="0.9"
```

### Node Enable/Disable
```bash
export CRITICISM_ENABLED=false
export GITHUB_ISSUE_ENABLED=false
```

### GitHub Issue Upload
```bash
export UPLOAD_TO_GITHUB=true
export GITHUB_OWNER="your-org"
export GITHUB_REPOSITORY="your-repo"
```

## Output

### Schema Compliance
- Validation against `schema/lean-research-schema.jsonc`
- JSON Schema Draft 2020-12 format
- Built-in validation via OpenAI Structured Outputs

### File Output
- Proposals saved to `proposals/<slug>.json`
- Optional GitHub issue creation with proposal details
- Alpha-only mode support with simplified schema

## Development

### Adding New Nodes
1. Create node file in `agent/nodes/`
2. Add to enabled nodes list in `agent/config.py`
3. Register in `agent/graph.py`
4. Add prompts to `agent/prompts.py`

### Adding New Tools
1. Create tool client in `agent/tools/`
2. Add MCP client configuration
3. Configure per-node tool access
4. Update tool-aware prompts

## Architecture Benefits

- **Modularity**: Clear separation of concerns across components
- **Configurability**: Extensive configuration options for different use cases
- **Reliability**: Checkpointed state management and error recovery
- **Extensibility**: Easy addition of new nodes, tools, and providers
- **Observability**: Comprehensive logging and state tracking
- **Quality Control**: Conditional restart logic and criticism evaluation
