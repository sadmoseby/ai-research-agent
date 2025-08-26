# Multi-Provider Configuration Examples

This document shows how to configure different LLM providers for the research agent.

## Basic Setup

Set your API keys in environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export GITHUB_TOKEN="your-github-token"
export TAVILY_API_KEY="your-tavily-key"
```

## Provider Selection

### Default Provider

```bash
# Set the default provider for all nodes
export DEFAULT_LLM_PROVIDER="anthropic"
```

### Node-Specific Providers

```bash
# Use different providers for different tasks
export SYNTHESIZE_PROVIDER="anthropic"    # Claude for synthesis
export WEB_RESEARCH_PROVIDER="openai"     # GPT for web research
export CRITICISM_PROVIDER="gemini"        # Gemini for criticism
export PRIOR_ART_PROVIDER="ollama"        # Local Ollama for prior art
```

## Model Configuration

### Global Settings

```bash
export MODEL="claude-3-5-sonnet-20241022"
export TEMPERATURE="0.7"
export MAX_TOKENS="4000"
```

### Provider-Specific Models

```bash
export OPENAI_MODEL="gpt-4o"
export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
export GEMINI_MODEL="gemini-1.5-pro"
export OLLAMA_MODEL="llama3.1:70b"
```

### Node-Specific Models

```bash
export SYNTHESIZE_MODEL="claude-3-opus-20240229"  # Use Opus for complex synthesis
export WEB_RESEARCH_MODEL="gpt-4o-mini"           # Use mini for simple research
```

## Ollama Setup

For local models using Ollama:

```bash
# Enable Ollama
export ENABLE_OLLAMA="true"
export OLLAMA_MODEL="llama3.1"
export OLLAMA_BASE_URL="http://localhost:11434"

# Make sure Ollama is running
ollama serve
ollama pull llama3.1
```

## Complete Example Configurations

### Configuration 1: OpenAI Primary with Anthropic for Synthesis

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DEFAULT_LLM_PROVIDER="openai"
export SYNTHESIZE_PROVIDER="anthropic"
export SYNTHESIZE_MODEL="claude-3-5-sonnet-20241022"
```

### Configuration 2: Anthropic Primary with Mixed Providers

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
export OPENAI_API_KEY="sk-..."

export DEFAULT_LLM_PROVIDER="anthropic"
export WEB_RESEARCH_PROVIDER="openai"
export CRITICISM_PROVIDER="gemini"

export ANTHROPIC_MODEL="claude-3-5-sonnet-20241022"
export OPENAI_MODEL="gpt-4o"
export GEMINI_MODEL="gemini-1.5-pro"
```

### Configuration 3: Local-First with Cloud Fallback

```bash
export ENABLE_OLLAMA="true"
export OLLAMA_MODEL="llama3.1:70b"
export OPENAI_API_KEY="sk-..."

export DEFAULT_LLM_PROVIDER="ollama"
export SYNTHESIZE_PROVIDER="openai"  # Use cloud for complex synthesis
```

## Cost Optimization Strategies

### Strategy 1: Use Cheaper Models for Simple Tasks

```bash
export DEFAULT_LLM_PROVIDER="openai"
export MODEL="gpt-4o-mini"                    # Cheaper default
export SYNTHESIZE_PROVIDER="openai"
export SYNTHESIZE_MODEL="gpt-4o"              # Premium for synthesis
```

### Strategy 2: Mixed Providers for Best Value

```bash
export DEFAULT_LLM_PROVIDER="anthropic"
export WEB_RESEARCH_PROVIDER="openai"
export WEB_RESEARCH_MODEL="gpt-4o-mini"       # Cheap for web research
export SYNTHESIZE_PROVIDER="anthropic"        # Claude for quality synthesis
```

## Error Handling

The system will automatically:

- Fall back to available providers if the preferred one fails
- Use the default provider if a node-specific provider isn't configured
- Validate that at least one provider is available on startup

## Checking Provider Status

You can check which providers are available in your code:

```python
from agent.llm_client import LLMClient

available = LLMClient.get_available_providers()
print(f"Available providers: {available}")
```
