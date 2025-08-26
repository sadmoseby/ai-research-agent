# Logging System for AI Research Agent

This document describes the comprehensive logging system implemented for the AI Research Agent.

## Overview

The logging system provides detailed visibility into the operation of the research agent workflow, including:

- **Graph-level logging**: Overall workflow execution and routing decisions
- **Node-level logging**: Individual node execution, inputs, outputs, and errors
- **Configurable logging levels**: DEBUG, INFO, WARNING, ERROR
- **File and console output**: Optional file logging with rotation
- **Structured logging**: Consistent format across all components

## Configuration

### LoggingConfig Class

The logging system is configured through the `LoggingConfig` dataclass in `agent/config.py`:

```python
@dataclass
class LoggingConfig:
    level: str = "INFO"                    # Logging level (DEBUG, INFO, WARNING, ERROR)
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_node_logging: bool = True       # Enable logging for individual nodes
    enable_graph_logging: bool = True      # Enable logging for graph operations
    log_to_file: bool = False             # Write logs to file
    log_file_path: str = "research_agent.log"  # Log file path
    max_log_file_size: int = 10 * 1024 * 1024  # 10MB max file size
    backup_count: int = 3                 # Number of backup files to keep
```

### Environment Variables

You can configure logging via environment variables (if implemented in your config loading):

- `LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `LOG_TO_FILE`: Enable file logging (true/false)
- `LOG_FILE_PATH`: Custom log file path

## Usage

### Basic Setup

```python
from agent.config import Config

# Create config
config = Config.from_env()

# Setup logging (should be called once at startup)
config.setup_logging()
```

### Getting Loggers

```python
from agent.config import get_logger

# Get a logger for any component
logger = get_logger("my_component")
logger.info("This is an info message")
logger.debug("This is a debug message")
logger.warning("This is a warning")
logger.error("This is an error")
```

## Logger Hierarchy

The system uses a hierarchical logger structure under the `research_agent` namespace:

```
research_agent.graph           # Main workflow logging
research_agent.nodes.plan      # Planning node
research_agent.nodes.web_research  # Web research node
research_agent.nodes.prior_art    # Prior art checking node
research_agent.nodes.criticism    # Criticism node
research_agent.nodes.synthesize   # Synthesis node
research_agent.nodes.validate     # Validation node
research_agent.nodes.persist      # Persistence node
```

## Logging Features by Component

### Graph Level (`research_agent.graph`)

Logs include:

- Graph creation and compilation
- Node execution start/completion
- Routing decisions between nodes
- Error handling and recovery

Example output:

```
2025-08-26 14:44:47,290 - research_agent.graph - INFO - Creating research graph with configuration
2025-08-26 14:44:47,291 - research_agent.graph - INFO - Starting execution of node: plan
2025-08-26 14:44:47,292 - research_agent.graph - INFO - Prior art routing decision: should_restart=False -> criticism
```

### Node Level

Each node logs:

- **Start/completion**: When node execution begins and ends
- **Input processing**: Analysis of received state
- **Tool usage**: Available MCP tools and their usage
- **Results**: Summary of outputs and decisions
- **Errors**: Detailed error information with stack traces

#### Plan Node (`research_agent.nodes.plan`)

- Planning iterations and restart reasons
- Search query generation
- Available tools assessment

#### Web Research Node (`research_agent.nodes.web_research`)

- Search query processing
- Tool availability and fallback strategies
- Search result counts and sources

#### Prior Art Node (`research_agent.nodes.prior_art`)

- GitHub search operations
- Repository discovery and analysis
- Prior art verdict and reasoning

#### Criticism Node (`research_agent.nodes.criticism`)

- Research proposal evaluation
- LLM interaction for criticism generation
- Analysis context formatting

#### Synthesis Node (`research_agent.nodes.synthesize`)

- Research data compilation
- Proposal structure generation
- Schema compliance preparation

#### Validation Node (`research_agent.nodes.validate`)

- Schema validation results
- Error detection and reporting
- Repair attempt tracking

#### Persist Node (`research_agent.nodes.persist`)

- File writing operations
- Output format generation
- Success/failure reporting

## Log Message Format

All log messages follow this format:

```
TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE
```

Example:

```
2025-08-26 14:44:47,291 - research_agent.nodes.plan - INFO - Planning completed successfully with 5 search queries
```

## File Logging

When enabled, file logging provides:

- **Rotation**: Automatic file rotation when size limit is reached
- **Backup retention**: Configurable number of backup files
- **Persistent storage**: All log messages saved for later analysis

## Performance Considerations

The logging system is designed to be:

- **Low overhead**: Minimal impact on execution time
- **Lazy evaluation**: Uses lazy % formatting for better performance
- **Configurable**: Can be disabled or reduced in production

## Debugging and Troubleshooting

### Debug Level Logging

Set `level: "DEBUG"` for detailed troubleshooting:

- Tool availability checks
- State transitions
- Detailed error context
- Internal decision logic

### Common Log Patterns

**Successful execution:**

```
INFO - Starting [node] node execution
DEBUG - [node] received state keys: [...]
INFO - Successfully completed [node]: [summary]
```

**Error handling:**

```
WARNING - [Tool] search failed for query 'X': [reason]
ERROR - Error in node [node]: [error message]
```

**Routing decisions:**

```
INFO - [Node] routing decision: [condition] -> [next_node]
```

## Testing

Use the included test script to verify logging setup:

```bash
python3 test_logging.py
```

This will:

- Test all logger components
- Create a test log file
- Verify configuration
- Display sample log entries

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Detailed troubleshooting info
   - INFO: General operational messages
   - WARNING: Recoverable issues
   - ERROR: Serious problems

2. **Use lazy formatting**:

   ```python
   # Good
   logger.info("Processing %d items", count)

   # Avoid
   logger.info(f"Processing {count} items")
   ```

3. **Include context**:
   - Node names in messages
   - Operation outcomes
   - Relevant parameters

4. **Handle sensitive data**:
   - Don't log API keys or secrets
   - Truncate long content when appropriate
   - Use data lengths instead of full content

## Integration with Existing Code

The logging system is already integrated into:

- ✅ Graph workflow and routing
- ✅ All node implementations
- ✅ CLI entry points
- ✅ Configuration management

All nodes now include comprehensive logging without breaking existing functionality.
