"""
Example script showing how to use different LLM providers with the research agent.
"""

import asyncio
import os

from agent.config import Config
from agent.llm_client import LLMClient


async def example_provider_usage():
    """Demonstrate using different providers."""

    # Example 1: Basic setup with environment variables
    print("=== Example 1: Basic Multi-Provider Setup ===\n")

    # Set some example environment variables (in practice, these would be in .env)
    os.environ["OPENAI_API_KEY"] = "sk-example"  # Replace with real key for testing
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-example"  # Replace with real key
    os.environ["DEFAULT_LLM_PROVIDER"] = "anthropic"

    config = Config.from_env()
    print(f"Available providers: {config.get_available_providers()}")
    print(f"Default provider: {config.default_provider}")

    # Example 2: Using default provider
    print("\n=== Example 2: Using Default Provider ===\n")

    llm_client = LLMClient(config)
    provider_info = llm_client.get_provider_info()
    print(f"Using provider: {provider_info['provider']} with model: {provider_info['model']}")

    # Example 3: Node-specific configuration
    print("\n=== Example 3: Node-Specific Configuration ===\n")

    # Configure different providers for different nodes
    os.environ["SYNTHESIZE_PROVIDER"] = "anthropic"
    os.environ["WEB_RESEARCH_PROVIDER"] = "openai"

    # Reload config to pick up changes
    config = Config.from_env()

    # Create node-specific clients
    synthesize_client = LLMClient(config, "synthesize")
    web_research_client = LLMClient(config, "web_research")

    synthesize_info = synthesize_client.get_provider_info()
    web_research_info = web_research_client.get_provider_info()

    print(f"Synthesize node using: {synthesize_info['provider']} ({synthesize_info['model']})")
    print(f"Web research node using: {web_research_info['provider']} ({web_research_info['model']})")

    # Example 4: Dynamic provider selection
    print("\n=== Example 4: Dynamic Provider Selection ===\n")

    available_providers = config.get_available_providers()
    for provider in available_providers:
        try:
            # Get provider-specific configuration
            provider_config = config.get_provider_config(provider)
            if provider_config:
                print(f"{provider.upper()}:")
                print(f"  Model: {provider_config.model}")
                print(f"  Temperature: {provider_config.temperature}")
                print(f"  Max Tokens: {provider_config.max_tokens}")
        except Exception as e:
            print(f"  Error accessing {provider}: {e}")

    # Example 5: Provider-specific features
    print("\n=== Example 5: Provider Capabilities ===\n")

    capabilities = {
        "openai": ["Chat", "JSON Mode", "Function Calling", "Vision (GPT-4o)"],
        "anthropic": ["Chat", "Large Context (Claude)", "Code Analysis"],
        "gemini": ["Chat", "Multimodal", "Large Context"],
        "ollama": ["Local Deployment", "Privacy", "Custom Models", "No API Costs"],
    }

    for provider, features in capabilities.items():
        provider_available = provider in available_providers
        status = "✅ Available" if provider_available else "❌ Not configured"
        print(f"{provider.upper()}: {status}")
        if provider_available:
            for feature in features:
                print(f"  • {feature}")

    print("\n=== Example 6: Configuration Patterns ===\n")

    # Pattern 1: Cost optimization
    print("💰 Cost Optimization Pattern:")
    print("  • Use GPT-4o-mini for simple tasks (web research, planning)")
    print("  • Use GPT-4o/Claude for complex tasks (synthesis, criticism)")
    print("  • Use Ollama for development/testing")

    # Pattern 2: Quality optimization
    print("\n🎯 Quality Optimization Pattern:")
    print("  • Use Claude Opus for synthesis (best reasoning)")
    print("  • Use GPT-4o for web research (good at summarization)")
    print("  • Use Gemini for criticism (different perspective)")

    # Pattern 3: Privacy-focused
    print("\n🔒 Privacy-Focused Pattern:")
    print("  • Use Ollama for sensitive research")
    print("  • Use cloud providers only for public data")
    print("  • Keep all data processing local when possible")

    # Pattern 4: Research specialization
    print("\n🔬 Research Specialization Pattern:")
    print("  • Use Claude for academic writing and analysis")
    print("  • Use GPT-4o for technical implementation")
    print("  • Use Gemini for creative ideation")
    print("  • Use Ollama for iteration and refinement")


def print_configuration_examples():
    """Print example .env configurations."""
    print("\n" + "=" * 60)
    print("CONFIGURATION EXAMPLES")
    print("=" * 60)

    print("\n🔹 Basic Multi-Provider Setup:")
    print(
        """
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DEFAULT_LLM_PROVIDER="anthropic"
"""
    )

    print("🔹 Cost-Optimized Research Setup:")
    print(
        """
export OPENAI_API_KEY="sk-..."
export DEFAULT_LLM_PROVIDER="openai"
export MODEL="gpt-4o-mini"
export SYNTHESIZE_MODEL="gpt-4o"
export CRITICISM_MODEL="gpt-4o"
"""
    )

    print("🔹 Quality-Focused Setup:")
    print(
        """
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AI..."
export DEFAULT_LLM_PROVIDER="anthropic"
export SYNTHESIZE_PROVIDER="anthropic"
export SYNTHESIZE_MODEL="claude-3-opus-20240229"
export CRITICISM_PROVIDER="gemini"
export WEB_RESEARCH_PROVIDER="openai"
"""
    )

    print("🔹 Local Development with Cloud Backup:")
    print(
        """
export ENABLE_OLLAMA="true"
export OLLAMA_MODEL="llama3.1:70b"
export OPENAI_API_KEY="sk-..."
export DEFAULT_LLM_PROVIDER="ollama"
export SYNTHESIZE_PROVIDER="openai"
"""
    )

    print("🔹 Research Team Setup (Different Specializations):")
    print(
        """
# Academic writing specialist
export SYNTHESIZE_PROVIDER="anthropic"
export SYNTHESIZE_MODEL="claude-3-opus-20240229"

# Technical research specialist
export WEB_RESEARCH_PROVIDER="openai"
export PRIOR_ART_PROVIDER="openai"

# Critical analysis specialist
export CRITICISM_PROVIDER="gemini"
export VALIDATE_PROVIDER="gemini"
"""
    )


if __name__ == "__main__":
    print("🤖 AI Research Agent - Multi-Provider Examples")
    print("=" * 50)

    # Run the async examples
    asyncio.run(example_provider_usage())

    # Print configuration examples
    print_configuration_examples()

    print("\n✨ Ready to use multiple LLM providers with your research agent!")
    print("💡 See docs/MULTI_PROVIDER_CONFIG.md for more details.")
