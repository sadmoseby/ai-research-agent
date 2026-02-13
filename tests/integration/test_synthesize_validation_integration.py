"""
Test the validation MCP integration in synthesize node.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
os.environ["DEFAULT_LLM_PROVIDER"] = "openai"
os.environ["SYNTHESIZE_ENABLED"] = "true"
os.environ["SYNTHESIZE_PROVIDER"] = "openai"
os.environ["SYNTHESIZE_MCP_TOOLS"] = "validation"

from agent.config import Config
from agent.nodes.synthesize import synthesize_node
from agent.state import ResearchState


@pytest.mark.requires_api
async def test_synthesize_with_validation():
    """Test that synthesize node includes validation functionality."""

    # Create test state
    state = ResearchState(
        idea="Simple momentum strategy",
        alpha_only=True,
        research_plan="Test momentum strategy with price data",
        web_search_results=[],
        criticism_results={"viability_score": 75, "summary": "Good strategy"},
        repair_attempts=0,
    )

    try:
        print("Testing synthesize node with integrated validation...")

        # Create config from environment
        config = Config()

        result = await synthesize_node(state, config)

        print(f"Result keys: {list(result.keys())}")

        # Check if we have either final_proposal (validation passed) or
        # validation_errors (validation failed but handled)
        if "final_proposal" in result:
            print("✅ Validation passed and proposal generated successfully")
            proposal = result["final_proposal"]
            print(f"Proposal has title: {'title' in proposal}")
            print(f"Proposal is alpha-only: {proposal.get('alpha-only', False)}")

        elif "validation_errors" in result:
            print("⚠️ Validation failed but was handled gracefully")
            print(f"Validation errors: {result['validation_errors']}")

        else:
            print("❌ Unexpected result structure")
            print(f"Full result: {result}")

        # Check that we're not routing to validate node anymore
        assert result.get("current_step") in [
            "persist",
            "synthesize",
        ], f"Unexpected next step: {result.get('current_step')}"

        print("✅ Synthesize node with validation integration test passed!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_synthesize_with_validation())
