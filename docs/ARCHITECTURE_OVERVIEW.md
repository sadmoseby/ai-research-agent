# Lean Research Agent - Architecture Overview

## Current System Architecture

The Lean Research Agent is a comprehensive research workflow system built on LangGraph with advanced features for generating quantitative finance research proposals.

## Core Components

### 1. Workflow Engine (LangGraph)
- **File**: `agent/graph.py`
- **Features**: Checkpointed state management, conditional routing, node enable/disable
- **Nodes**: plan → web_research → prior_art → criticism → synthesize → validate → persist

### 2. Configuration System
- **File**: `agent/config.py`
- **Features**: Global and per-node configuration, multi-provider LLM support, MCP tool access control
- **Environment**: Extensive environment variable support for all settings

### 3. State Management
- **File**: `agent/state.py`
- **Features**: Typed state with workflow tracking, tool usage tracking, criticism scores

### 4. Node System
- **Directory**: `agent/nodes/`
- **Files**: plan.py, web_research.py, prior_art.py, criticism.py, synthesize.py, validate.py, persist.py
- **Features**: Individual node configuration, MCP tool integration, comprehensive logging

### 5. Tool Integration (MCP)
- **Directory**: `agent/tools/`
- **Files**: mcp_client.py, github_api.py, tavily_tool.py
- **Features**: Standardized tool protocol, per-node tool access, fallback mechanisms

### 6. LLM Client System
- **File**: `agent/llm_client.py`
- **Features**: Multi-provider support (OpenAI, Anthropic, Gemini, Ollama), unified API, structured outputs

### 7. Prompt Management
- **File**: `agent/prompts.py`
- **Features**: Centralized prompt organization, tool-aware prompts, context formatting

## Key Features

### Conditional Restart Logic
- **Prior Art Restart**: Triggered when 3+ similar implementations found
- **Criticism Score Restart**: Triggered when viability score < 51/100
- **Iteration Limits**: Maximum 3 planning iterations to prevent infinite loops

### Node Enable/Disable System
- **Selective Execution**: Enable/disable individual workflow nodes
- **Automatic Routing**: Graph automatically routes around disabled nodes
- **Use Cases**: Fast prototyping, debugging, resource management

### Multi-Provider LLM Support
- **Providers**: OpenAI, Anthropic (Claude), Google (Gemini), Ollama (local)
- **Per-Node Configuration**: Different providers for different tasks
- **Fallback Logic**: Automatic provider availability detection

### MCP Tool Integration
- **Global Registry**: Centralized MCP client management
- **Per-Node Access**: Fine-grained tool access control
- **Tool Types**: web_search, github, tavily, filesystem

### Comprehensive Logging
- **Graph-Level**: Workflow execution, routing decisions
- **Node-Level**: Individual node execution, tool usage, errors
- **Configurable**: DEBUG, INFO, WARNING, ERROR levels with file output

## Workflow Details

### Standard Flow
```
START → plan → web_research → prior_art → criticism → synthesize → validate → persist → END
```

### Conditional Routing
- **prior_art** can restart planning if significant prior art found
- **criticism** can restart planning if low viability score
- **validate** can repair via synthesize on validation errors

### Alpha-Only Mode
- Enforces exactly one alpha (new or amend) and one existing universe
- Simpler, focused proposals for alpha generation research

## Configuration Examples

### Basic Setup
```bash
export OPENAI_API_KEY="your-key"
export GITHUB_TOKEN="your-token"
export TAVILY_API_KEY="your-key"
```

### Node-Specific Configuration
```bash
export SYNTHESIZE_PROVIDER="anthropic"
export WEB_RESEARCH_PROVIDER="openai"
export CRITICISM_TEMPERATURE="0.9"
export VALIDATE_USE_MCP="false"
```

### Node Enable/Disable
```bash
export CRITICISM_ENABLED=false
export PRIOR_ART_ENABLED=false
```

## Output

### Schema Compliance
- Strict validation against `schema/lean-research-schema.jsonc`
- JSON Schema Draft 2020-12 format
- Automatic repair attempts on validation failure

### File Output
- Proposals saved to `proposals/<slug>.json`
- Detailed validation reports
- Alpha-only mode support

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
