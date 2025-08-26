# Per-Node Configuration

The Lean Research Agent now supports per-node configuration, allowing you to customize settings like model, temperature, max_tokens, and use_mcp for individual nodes in the workflow.

## Configuration Structure

The configuration system consists of:

- **Global defaults**: Applied to all nodes unless overridden
- **Node-specific settings**: Override global defaults for specific nodes

## Setting Per-Node Configuration

### Via Environment Variables

Use the pattern `{NODE_NAME_UPPER}_{SETTING}`:

```bash
# Global settings
export OPENAI_MODEL="gpt-4o"
export TEMPERATURE="0.7"
export USE_MCP="true"

# Node-specific overrides
export SYNTHESIZE_MODEL="gpt-4o-mini"        # Use cheaper model for synthesis
export CRITICISM_TEMPERATURE="0.9"           # Higher creativity for criticism
export WEB_RESEARCH_MAX_TOKENS="8000"        # More tokens for web research
export VALIDATE_USE_MCP="false"              # Disable MCP for validation
```

### Programmatically

```python
from agent.config import Config

config = Config.from_env()

# Set node-specific configuration
config.set_node_config("plan", model="gpt-3.5-turbo", temperature=0.1)
config.set_node_config("synthesize", model="gpt-4o-mini", max_tokens=6000)
```

## Available Nodes

- `plan` - Research planning
- `web_research` - Web search and data gathering
- `prior_art` - GitHub code search for prior implementations
- `criticism` - Critical analysis of research approach
- `synthesize` - Proposal generation
- `validate` - Schema validation
- `persist` - File output

## Available Settings Per Node

- `model` - OpenAI model to use (e.g., "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo")
- `use_mcp` - Whether to use Model Context Protocol (true/false)
- `temperature` - Sampling temperature (0.0-2.0)
- `max_tokens` - Maximum tokens in response (integer)

## Usage in Nodes

Nodes receive a `Config` object with node-specific settings applied as defaults:

```python
def my_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    # config.model will be the node-specific model if set,
    # otherwise the global default
    client = AsyncOpenAI(api_key=config.openai_api_key)
    response = await client.chat.completions.create(
        model=config.model,  # Uses node-specific model
        temperature=config.temperature,  # Uses node-specific temperature
        # ...
    )
```

## Configuration Inheritance

1. Global defaults are set in the Config class
2. Environment variables override global defaults
3. Node-specific environment variables override both
4. Programmatic `set_node_config()` calls override everything

## Example Use Cases

- **Cost optimization**: Use `gpt-4o-mini` for less critical nodes
- **Performance tuning**: Higher temperatures for creative tasks, lower for analytical
- **Resource management**: More tokens for research nodes, fewer for validation
- **Feature toggling**: Disable MCP for specific nodes during debugging
