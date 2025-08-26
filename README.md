# Lean Research Agent

A comprehensive research agent that generates structured research proposals for quantitative finance algorithms, conforming to the Lean Research Engine schema.

## Features

- **LangGraph Orchestration**: Checkpointed state management for reliable execution
- **OpenAI Integration**: Uses OpenAI's Responses API with web search tool and Structured Outputs
- **Prior Art Checking**: GitHub code search for novelty assessment
- **Schema Validation**: Strict JSON schema validation using Draft 2020-12
- **Alpha-Only Mode**: Focused proposals for alpha generation research
- **Fallback Search**: Tavily integration for additional web search capabilities

## Quick Start

### 1. Setup

```bash
# Clone and navigate to the project
cd ai-research-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# At minimum, you need OPENAI_API_KEY
```

### 3. Generate a Research Proposal

```bash
# Basic proposal
python main.py propose --idea "momentum-based alpha using RSI divergence"

# Alpha-only proposal (simpler, focused on alpha generation)
python main.py propose --idea "mean reversion strategy for ETFs" --alpha-only

# Custom output filename
python main.py propose --idea "volatility arbitrage" --slug vol_arb_strategy
```

- 🎯 **Alpha-Only Mode**: Supports focused alpha-only proposals for streamlined research
- ✅ **Schema Validation**: Ensures all outputs conform to the required JSON schema format

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-research-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.template .env
# Edit .env and add your API keys
```

### Required API Keys

- **OPENAI_API_KEY** (required): For LLM and web search functionality
- **GITHUB_TOKEN** (optional): For prior art checking via GitHub API
- **TAVILY_API_KEY** (optional): For fallback web search

## Usage

### Command Line Interface

Generate a comprehensive research proposal:

```bash
python main.py propose --idea "momentum-based sector rotation strategy"
```

Generate an alpha-only proposal:

```bash
python main.py propose --idea "mean reversion trading" --alpha-only
```

Custom output filename:

```bash
python main.py propose --idea "volatility arbitrage" --slug "vol_arb_strategy"
```

### Python API

```python
from agent.config import Config
from agent.graph import create_research_graph
from agent.state import ResearchState

# Configure
config = Config.from_env()
graph = create_research_graph(config)

# Create initial state
state = ResearchState(
    idea="pairs trading strategy",
    alpha_only=False,
    slug="pairs_trading",
    current_step="plan"
)

# Run research
result = await graph.ainvoke(state)
print(f"Proposal saved to: {result['proposal_path']}")
print(f"Workflow state saved to: {result['state_path']}")
```

## Workflow

The agent follows a structured research workflow:

1. **📋 Planning**: Analyzes the idea and creates a research plan with targeted search queries
2. **🌐 Web Research**: Conducts comprehensive web searches using multiple sources
3. **🔍 Prior Art Check**: Searches GitHub for similar implementations
4. **⚗️ Synthesis**: Generates structured proposal using OpenAI with schema validation
5. **✅ Validation**: Validates against JSON schema with automatic repair attempts
6. **💾 Persistence**: Saves both the final proposal and complete workflow state to `proposals/` directory

## Output Format

All proposals conform to the [Lean Research Schema](schema/lean-research-schema.jsonc) and include:

- **Alpha strategies** with detailed methodologies
- **Risk management** frameworks
- **Portfolio construction** approaches
- **Execution** specifications
- **Universe definitions**
- **Tunable parameters** with optimization ranges

### Alpha-Only Mode

When using `--alpha-only`, the output is restricted to:

- Exactly one alpha component (new or amend)
- Exactly one existing universe component
- Focused on alpha generation methodology

## Project Structure

```
ai-research-agent/
├── agent/
│   ├── config.py          # Configuration management
│   ├── state.py           # State definitions
│   ├── graph.py           # LangGraph workflow
│   ├── nodes/             # Workflow nodes
│   │   ├── plan.py        # Research planning
│   │   ├── web_research.py # Web search
│   │   ├── prior_art.py   # GitHub search
│   │   ├── synthesize.py  # Proposal generation
│   │   ├── validate.py    # Schema validation
│   │   └── persist.py     # File persistence
│   └── tools/             # External API tools
│       ├── github_api.py  # GitHub integration
│       └── tavily_tool.py # Tavily search
├── schema/
│   └── lean-research-schema.jsonc  # Output schema
├── proposals/             # Generated proposals
├── cli.py                # Command line interface
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

## Configuration

The agent supports several configuration options via environment variables:

- `OPENAI_API_KEY`: Required for all AI operations
- `OPENAI_MODEL`: Model to use (default: gpt-4o)
- `GITHUB_TOKEN`: Optional for prior art checking
- `TAVILY_API_KEY`: Optional for fallback web search

## Development

### Adding New Nodes

1. Create a new file in `agent/nodes/`
2. Implement the node function with signature `(state: ResearchState, config: Config) -> Dict[str, Any]`
3. Update `agent/graph.py` to include the new node
4. Add appropriate state transitions

### Extending Tools

1. Create new tool classes in `agent/tools/`
2. Follow the existing API patterns
3. Add configuration support in `config.py`
4. Integrate into relevant nodes

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open a GitHub issue or contact the development team.
