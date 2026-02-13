#!/usr/bin/env python3
"""
Demo script showing how to configure node enable/disable functionality.
"""

# Instructions for using node enable/disable configuration:

print(
    """
🎛️  Node Enable/Disable Configuration Demo
===========================================

The research agent now supports turning individual nodes on and off via environment variables.

🔧 Configuration Methods:

1. Environment Variables:
   Set {NODE_NAME}_ENABLED=true/false to control individual nodes.

   Examples:
   export CRITICISM_ENABLED=false     # Disable criticism node
   export GITHUB_ISSUE_ENABLED=false  # Disable GitHub issue creation
   export WEB_RESEARCH_ENABLED=true   # Explicitly enable web research

2. Supported Node Names:
   - PLAN_ENABLED
   - WEB_RESEARCH_ENABLED
   - CRITICISM_ENABLED
   - SYNTHESIZE_ENABLED
   - PERSIST_ENABLED
   - GITHUB_ISSUE_ENABLED

🚀 Usage Examples:

# Run with criticism disabled for speed
export CRITICISM_ENABLED=false
python main.py propose --idea "momentum trading strategy"

# Run with only core synthesis
export PLAN_ENABLED=false
export WEB_RESEARCH_ENABLED=false
export CRITICISM_ENABLED=false
python main.py propose --idea "mean reversion strategy"

# Run with full pipeline (default)
python main.py propose --idea "pairs trading strategy"

📋 Node Descriptions:

• plan: Initial research planning and strategy formation
• web_research: Comprehensive web research using OpenAI
• criticism: Critical analysis and feedback loop
• synthesize: Generate and validate the research proposal JSON
• persist: Save the final proposal to disk
• github_issue: Create GitHub issue from proposal (optional)

⚠️  Important Notes:

1. At least one node must be enabled
2. Critical nodes (synthesize, persist) should typically remain enabled
3. Disabling nodes affects the quality vs speed tradeoff
4. The graph automatically routes around disabled nodes

🎯 Use Cases:

• Fast prototyping: Disable criticism
• Core synthesis only: Disable plan, web_research, criticism
• Research-heavy: Keep all nodes enabled (default)
• Debug/testing: Disable individual nodes to isolate issues

"""
)

# Test the configuration programmatically
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from agent.config import Config

    # Set minimal environment for demo
    os.environ["OPENAI_API_KEY"] = "demo-key"

    print("📊 Current Configuration:")
    config = Config.from_env()
    print(f"   Enabled nodes: {config.get_enabled_nodes()}")
    print(f"   Disabled nodes: {config.get_disabled_nodes()}")

    print("\n🧪 Testing individual node status:")
    for node in config.get_all_node_names():
        status = "✅ enabled" if config.is_node_enabled(node) else "❌ disabled"
        print(f"   {node}: {status}")

except ImportError as e:
    print(f"⚠️  Cannot run config demo (missing dependencies: {e})")
    print("   But the environment variable configuration will still work!")
