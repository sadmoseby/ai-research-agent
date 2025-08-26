#!/usr/bin/env python3
"""
Test script to verify logging setup for the research agent.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config, get_logger


def test_logging():
    """Test the logging setup."""
    # Create a minimal config for testing logging
    config = Config()
    config.openai_api_key = "test-key"  # Dummy key for testing

    # Enable file logging for testing
    config.logging.log_to_file = True
    config.logging.log_file_path = "test_research_agent.log"
    config.logging.level = "DEBUG"

    # Setup logging
    config.setup_logging()

    # Test graph logger
    graph_logger = get_logger("graph")
    graph_logger.info("Testing graph logger")
    graph_logger.debug("This is a debug message from graph")
    graph_logger.warning("This is a warning from graph")

    # Test node loggers
    node_names = [
        "plan",
        "web_research",
        "prior_art",
        "criticism",
        "synthesize",
        "validate",
        "persist",
    ]

    for node_name in node_names:
        logger = get_logger(f"nodes.{node_name}")
        logger.info("Testing %s node logger", node_name)
        logger.debug("Debug message from %s node", node_name)

    # Test routing decisions
    graph_logger.info("Prior art routing decision: should_restart=%s -> %s", False, "criticism")
    graph_logger.info("Criticism routing decision: should_restart=%s -> %s", False, "synthesize")
    graph_logger.info(
        "Validation routing decision: has_errors=%s, repair_attempts=%d -> %s",
        False,
        0,
        "persist",
    )

    print("✅ Logging test completed successfully!")
    print(f"📁 Check log file: {config.logging.log_file_path}")

    # Print some log statistics
    if Path(config.logging.log_file_path).exists():
        with open(config.logging.log_file_path, "r") as f:
            lines = f.readlines()
            print(f"📊 Log file contains {len(lines)} lines")

            # Show last few lines
            print("📝 Last few log entries:")
            for line in lines[-5:]:
                print(f"   {line.strip()}")


if __name__ == "__main__":
    test_logging()
