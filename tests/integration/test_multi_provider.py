"""
Test script for multi-provider LLM configuration.
"""

import asyncio
import os

from agent.config import Config
from agent.llm_client import LLMClient
from agent.tools.mcp_client import MCPClient


async def test_providers():
    """Test different LLM providers."""
    print("🔍 Testing Multi-Provider LLM Configuration\n")

    # Test 1: Load configuration
    print("1. Loading configuration...")
    try:
        config = Config.from_env()
        print(f"   ✅ Loaded config with default provider: {config.default_config.llm_provider.provider}")
        print(f"   ✅ Available providers: {config.get_available_providers()}")

        if not config.get_available_providers():
            print("   ❌ No providers configured! Please set at least one API key.")
            return

    except Exception as e:
        print(f"   ❌ Config loading failed: {e}")
        return

    # Test 2: Test LLM client with default provider
    print("\n2. Testing default LLM client...")
    try:
        llm_client = LLMClient(config)
        provider_info = llm_client.get_provider_info()
        print(f"   ✅ Default provider: {provider_info['provider']}")
        print(f"   ✅ Model: {provider_info['model']}")

        # Test a simple completion
        response = await llm_client.chat_completion(
            [
                {
                    "role": "user",
                    "content": "Say 'Hello from' followed by the name of your AI model in exactly 5 words.",
                }
            ]
        )
        print(f"   ✅ Response: {response.strip()}")

    except Exception as e:
        print(f"   ❌ Default LLM client test failed: {e}")

    # Test 3: Test node-specific configurations
    print("\n3. Testing node-specific configurations...")
    node_names = ["synthesize", "web_research", "criticism"]

    for node_name in node_names:
        try:
            node_config = config.get_node_config(node_name)
            print(f"   📝 {node_name}:")
            print(f"      Provider: {node_config['provider']}")
            print(f"      Model: {node_config['model']}")
            print(f"      MCP Tools: {node_config['mcp_tools']}")

            # Test node-specific LLM client
            node_llm = LLMClient(config, node_name)
            node_provider_info = node_llm.get_provider_info()
            print(f"      ✅ Active: {node_provider_info['provider']} ({node_provider_info['model']})")

        except Exception as e:
            print(f"      ❌ Node {node_name} failed: {e}")

    # Test 4: Test MCP client with different providers
    print("\n4. Testing MCP client with multiple providers...")
    try:
        llm_client = LLMClient(config, node_name="synthesize")
        mcp_client = MCPClient(config, llm_client, node_name="synthesize")
        available_tools = mcp_client.get_available_tool_names()
        provider_info = mcp_client.get_provider_info()

        print(f"   ✅ MCP Provider: {provider_info['provider']} ({provider_info['model']})")
        print(f"   ✅ Available tools: {available_tools}")

        # Test structured generation
        if available_tools:
            print("   🧪 Testing structured proposal generation...")
            schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "provider_used": {"type": "string"},
                },
                "required": ["title", "summary", "provider_used"],
            }

            system_prompt = "You are a research assistant. Generate a brief research proposal."
            user_prompt = (
                f"Create a proposal about testing LLM providers. "
                f"Include the provider you are: {provider_info['provider']}"
            )

            result = await mcp_client.generate_proposal(system_prompt, user_prompt, schema)
            print("   ✅ Generated proposal:")
            print(f"      Title: {result.get('title', 'N/A')}")
            print(f"      Summary: {result.get('summary', 'N/A')[:100]}...")
            print(f"      Provider: {result.get('provider_used', 'N/A')}")

    except Exception as e:
        print(f"   ❌ MCP client test failed: {e}")

    # Test 5: Test provider availability
    print("\n5. Testing provider availability...")
    available_providers = LLMClient.get_available_providers()
    for provider, available in available_providers.items():
        status = "✅ Available" if available else "❌ Not installed"
        print(f"   {provider}: {status}")

    print("\n🎉 Multi-provider testing complete!")


def print_example_configs():
    """Print example configurations for different scenarios."""
    print("\n📋 Example Configurations:")

    print("\n🔹 Basic OpenAI + Anthropic Setup:")
    print("export OPENAI_API_KEY='sk-...'")
    print("export ANTHROPIC_API_KEY='sk-ant-...'")
    print("export DEFAULT_LLM_PROVIDER='anthropic'")
    print("export SYNTHESIZE_PROVIDER='anthropic'")
    print("export WEB_RESEARCH_PROVIDER='openai'")

    print("\n🔹 Cost-Optimized Setup:")
    print("export OPENAI_API_KEY='sk-...'")
    print("export DEFAULT_LLM_PROVIDER='openai'")
    print("export MODEL='gpt-4o-mini'  # Cheaper default")
    print("export SYNTHESIZE_MODEL='gpt-4o'  # Premium for synthesis")

    print("\n🔹 Local + Cloud Hybrid:")
    print("export ENABLE_OLLAMA='true'")
    print("export OLLAMA_MODEL='llama3.1'")
    print("export OPENAI_API_KEY='sk-...'")
    print("export DEFAULT_LLM_PROVIDER='ollama'")
    print("export SYNTHESIZE_PROVIDER='openai'  # Cloud for complex tasks")

    print("\n🔹 Multi-Provider Research Setup:")
    print("export OPENAI_API_KEY='sk-...'")
    print("export ANTHROPIC_API_KEY='sk-ant-...'")
    print("export GOOGLE_API_KEY='AI...'")
    print("export DEFAULT_LLM_PROVIDER='openai'")
    print("export SYNTHESIZE_PROVIDER='anthropic'")
    print("export CRITICISM_PROVIDER='gemini'")


async def main():
    """Main test function."""
    print("🤖 AI Research Agent - Multi-Provider LLM Test")
    print("=" * 50)

    # Check if any API keys are set
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY"),
        "Ollama": os.getenv("ENABLE_OLLAMA"),
    }

    configured_keys = [name for name, key in api_keys.items() if key]

    if not configured_keys:
        print("❌ No API keys configured!")
        print_example_configs()
        return

    print(f"✅ Configured providers: {', '.join(configured_keys)}")

    await test_providers()
    print_example_configs()


if __name__ == "__main__":
    asyncio.run(main())
