#!/usr/bin/env python3
"""
Simple test to verify the synthesize node changes work correctly.
"""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.prompts import ResearchPrompts


def test_component_research_context_formatting():
    """Test the new component research context formatting function."""
    print("=== Testing Component Research Context Formatting ===")

    # Test data
    research_plan = "Develop cryptocurrency trading strategy with momentum and mean reversion"
    component_research_results = {
        "ALPHA": [
            {
                "title": "Alpha Research Approach 1: Momentum Strategy",
                "content": "Momentum strategies in crypto markets show strong performance when using 12-1 month lookbacks. Key considerations include volatility scaling and transaction cost management.",
                "approach_number": 1,
                "component": "ALPHA",
            },
            {
                "title": "Alpha Research Approach 2: Mean Reversion",
                "content": "Mean reversion works well in crypto during consolidation periods. Optimal parameters are 20-day lookback with 2 standard deviation bands.",
                "approach_number": 2,
                "component": "ALPHA",
            },
        ],
        "UNIVERSE": [
            {
                "title": "Universe Research: Top Cryptocurrency Selection",
                "content": "Analysis shows top 30-50 cryptocurrencies by market cap provide optimal balance of liquidity and diversification. Minimum criteria: $100M market cap, $10M daily volume.",
                "approach_number": 1,
                "component": "UNIVERSE",
            }
        ],
        "RISK": [
            {
                "title": "Risk Management: Volatility-Based Position Sizing",
                "content": "Crypto markets require enhanced risk management due to extreme volatility. Implement volatility-based position sizing with maximum 10% per asset exposure.",
                "approach_number": 1,
                "component": "RISK",
            }
        ],
    }

    web_results = []
    idea = "Cryptocurrency momentum and mean reversion strategy"

    # Test the formatting
    try:
        formatted_context = ResearchPrompts.format_component_research_context(
            research_plan, component_research_results, web_results, idea
        )

        print("✓ Component research context formatting executed successfully")

        # Validate content
        assert f"Research Idea: {idea}" in formatted_context
        assert "Research Plan:" in formatted_context
        assert research_plan in formatted_context
        assert "COMPONENT-SPECIFIC RESEARCH FINDINGS:" in formatted_context
        assert "=== ALPHA RESEARCH ===" in formatted_context
        assert "=== UNIVERSE RESEARCH ===" in formatted_context
        assert "=== RISK RESEARCH ===" in formatted_context
        assert "Approach 1: Alpha Research Approach 1: Momentum Strategy" in formatted_context
        assert "Approach 2: Alpha Research Approach 2: Mean Reversion" in formatted_context

        print("✓ All content validation checks passed")

        # Check that full content is included (not truncated)
        assert "Momentum strategies in crypto markets show strong performance" in formatted_context
        assert "Mean reversion works well in crypto during consolidation" in formatted_context
        assert "Analysis shows top 30-50 cryptocurrencies" in formatted_context
        assert "Crypto markets require enhanced risk management" in formatted_context

        print("✓ Full content inclusion validated")

        return True

    except Exception as e:
        print(f"❌ Error in component research context formatting: {e}")
        return False


def test_fallback_to_web_results():
    """Test fallback to web results when no component research available."""
    print("\n=== Testing Fallback to Web Results ===")

    research_plan = "Simple trading strategy research"
    component_research_results = {}  # Empty
    web_results = [
        {
            "title": "Trading Strategy Overview",
            "content": "General overview of trading strategies including momentum, mean reversion, and arbitrage approaches for various markets.",
        },
        {
            "title": "Risk Management Best Practices",
            "content": "Best practices for risk management in algorithmic trading including position sizing, stop losses, and portfolio diversification.",
        },
    ]
    idea = "Basic trading strategy"

    try:
        formatted_context = ResearchPrompts.format_component_research_context(
            research_plan, component_research_results, web_results, idea
        )

        print("✓ Fallback formatting executed successfully")

        # Should contain web results instead of component results
        assert "GENERAL RESEARCH FINDINGS:" in formatted_context
        assert "Trading Strategy Overview" in formatted_context
        assert "Risk Management Best Practices" in formatted_context
        assert "COMPONENT-SPECIFIC RESEARCH FINDINGS:" not in formatted_context

        print("✓ Fallback to web results validated")

        return True

    except Exception as e:
        print(f"❌ Error in fallback formatting: {e}")
        return False


def test_synthesize_node_imports():
    """Test that synthesize node can be imported with our changes."""
    print("\n=== Testing Synthesize Node Imports ===")

    try:
        from agent.nodes.synthesize import (
            _generate_component_by_component_proposal,
            _generate_single_component,
            synthesize_node,
        )

        print("✓ All synthesize node functions imported successfully")

        # Check function signatures
        import inspect

        # Check synthesize_node signature
        sig = inspect.signature(synthesize_node)
        assert "state" in sig.parameters
        assert "config" in sig.parameters
        print("✓ synthesize_node signature correct")

        # Check component-by-component function signature
        sig = inspect.signature(_generate_component_by_component_proposal)
        expected_params = [
            "llm_client",
            "schema",
            "idea",
            "research_plan",
            "component_search_results",
            "prior_art",
            "available_tools",
        ]
        for param in expected_params:
            assert param in sig.parameters, f"Missing parameter: {param}"
        print("✓ _generate_component_by_component_proposal signature correct")

        # Check single component function signature
        sig = inspect.signature(_generate_single_component)
        expected_params = [
            "llm_client",
            "component_name",
            "schema_key",
            "idea",
            "research_plan",
            "component_research",
            "available_tools",
        ]
        for param in expected_params:
            assert param in sig.parameters, f"Missing parameter: {param}"
        print("✓ _generate_single_component signature correct")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking functions: {e}")
        return False


def test_config_boolean_env():
    """Test the new get_boolean_env method."""
    print("\n=== Testing Config Boolean Environment Variable Method ===")

    try:
        # Create a minimal config instance for testing the method
        # We'll test the method directly without full config initialization
        import os

        from agent.config import Config

        # Test the method exists
        assert hasattr(Config, "get_boolean_env"), "get_boolean_env method not found"
        print("✓ get_boolean_env method exists")

        # Create a mock config instance to test the method
        config = type("MockConfig", (), {})()
        config.get_boolean_env = Config.get_boolean_env.__get__(config, type(config))

        # Test different boolean values
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("", False),
            ("random", False),
        ]

        for test_value, expected in test_cases:
            os.environ["TEST_BOOL_VAR"] = test_value
            result = config.get_boolean_env("TEST_BOOL_VAR", False)
            assert result == expected, f"Failed for value '{test_value}': got {result}, expected {expected}"

        # Clean up
        if "TEST_BOOL_VAR" in os.environ:
            del os.environ["TEST_BOOL_VAR"]

        print("✓ Boolean environment variable parsing works correctly")

        return True

    except Exception as e:
        print(f"❌ Error testing config boolean env: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Synthesize Node Changes")
    print("=" * 50)

    tests = [
        ("Component Research Context Formatting", test_component_research_context_formatting),
        ("Fallback to Web Results", test_fallback_to_web_results),
        ("Synthesize Node Imports", test_synthesize_node_imports),
        ("Config Boolean Environment", test_config_boolean_env),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nResult: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! The synthesize node changes are working correctly.")
        print("\nKey improvements verified:")
        print("• Component research context formatting")
        print("• Fallback to web results when needed")
        print("• Function imports and signatures")
        print("• Configuration boolean parsing")
        print("\nThe modified synthesize node is ready for use!")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please review the implementation.")


if __name__ == "__main__":
    main()
