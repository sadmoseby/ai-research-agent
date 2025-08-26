# Node Enable/Disable Configuration

The research agent supports configuring which nodes are enabled or disabled in the workflow. This allows for customization of the research pipeline based on specific needs, from fast prototyping to full research workflows.

## Configuration

### Environment Variables

Control individual nodes using environment variables with the pattern `{NODE_NAME}_ENABLED=true/false`:

```bash
# Disable specific nodes
export CRITICISM_ENABLED=false
export PRIOR_ART_ENABLED=false

# Explicitly enable nodes (optional, enabled by default)
export WEB_RESEARCH_ENABLED=true
```

### Supported Node Names

- `PLAN_ENABLED` - Initial research planning and strategy formation
- `WEB_RESEARCH_ENABLED` - Gather information from web sources
- `PRIOR_ART_ENABLED` - Check GitHub for existing implementations
- `CRITICISM_ENABLED` - Critical analysis and feedback loop
- `SYNTHESIZE_ENABLED` - Generate the research proposal JSON
- `VALIDATE_ENABLED` - Validate against the schema
- `PERSIST_ENABLED` - Save the final proposal to disk

## Usage Examples

### Fast Prototyping
Disable criticism and prior art checks for faster iteration:

```bash
export CRITICISM_ENABLED=false
export PRIOR_ART_ENABLED=false
python cli.py propose --idea "momentum trading strategy"
```

### Core Synthesis Only
Run only the essential synthesis and validation steps:

```bash
export PLAN_ENABLED=false
export WEB_RESEARCH_ENABLED=false
export PRIOR_ART_ENABLED=false
export CRITICISM_ENABLED=false
python cli.py propose --idea "mean reversion strategy"
```

### Full Pipeline (Default)
All nodes enabled for comprehensive research:

```bash
python cli.py propose --idea "pairs trading strategy"
```

### Debug/Testing
Disable specific nodes to isolate issues:

```bash
export PRIOR_ART_ENABLED=false  # Skip GitHub integration issues
python cli.py propose --idea "test strategy"
```

## Node Flow and Dependencies

The nodes execute in the following sequence when enabled:

```
START → plan → web_research → prior_art → criticism → synthesize → validate → persist → END
```

### Bypass Logic

When nodes are disabled, the workflow automatically routes around them:

- **Disabled nodes are skipped** entirely from the graph
- **Routing functions** automatically find the next enabled node
- **Restart logic** (from criticism/prior_art) respects node enablement
- **Validation repair** only routes to synthesize if it's enabled

### Special Routing

Some nodes have special routing logic that's preserved:

- **prior_art** → can restart planning or continue to criticism/synthesize
- **criticism** → can restart planning or continue to synthesize
- **validate** → can repair via synthesize or continue to persist

## Programmatic Usage

```python
from agent.config import Config

config = Config.from_env()

# Check which nodes are enabled/disabled
enabled_nodes = config.get_enabled_nodes()
disabled_nodes = config.get_disabled_nodes()

# Check individual nodes
if config.is_node_enabled("criticism"):
    print("Criticism node is enabled")

# Get all node names
all_nodes = config.get_all_node_names()
```

## Important Notes

1. **At least one node must be enabled** - the system will raise an error if all nodes are disabled
2. **Critical nodes** (synthesize, persist) should typically remain enabled for a functional workflow
3. **Quality vs Speed** - disabling nodes affects the research quality vs execution speed tradeoff
4. **Automatic routing** - the graph automatically handles disabled nodes without manual intervention

## Use Cases

### Development & Testing
- **Debug specific nodes** by disabling others
- **Test node isolation** to understand dependencies
- **Performance profiling** of individual components

### Production Workflows
- **Fast prototyping** mode for quick iterations
- **Research-heavy** mode for comprehensive analysis
- **Custom pipelines** for specific use cases

### Resource Management
- **Reduce API calls** by disabling web research
- **Skip expensive operations** like GitHub prior art search
- **Minimize LLM calls** by disabling criticism loops

## Error Handling

The system includes validation to ensure:
- At least one node remains enabled
- Critical workflow paths are maintained
- Proper error messages for invalid configurations

## Configuration Inheritance

Node configuration follows the existing per-node configuration pattern:
- Global defaults apply to all nodes
- Node-specific overrides via environment variables
- Explicit enabled/disabled settings take precedence
