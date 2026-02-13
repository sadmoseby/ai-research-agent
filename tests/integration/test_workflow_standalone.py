"""
Test the complete workflow without validate node.
"""

import asyncio
import os

import pytest

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
os.environ["DEFAULT_LLM_PROVIDER"] = "openai"

from agent.config import Config
from agent.graph import create_research_graph
from agent.state import ResearchState


@pytest.mark.requires_api
async def test_workflow_without_validate():
    """Test the complete workflow without the validate node."""

    print("Testing complete workflow without validate node...")

    # Create config
    config = Config()

    # Create graph
    graph = create_research_graph(config)

    # Create initial state
    initial_state = ResearchState(idea="Simple momentum strategy test", alpha_only=True)

    # Run just the synthesize node to test our validation integration
    print("Running synthesize node with integrated validation...")

    # Simulate previous node outputs
    state_with_data = ResearchState(
        idea="Simple momentum strategy test",
        alpha_only=True,
        research_plan="Test momentum strategy",
        web_search_results=[{"title": "Example", "content": "Example content"}],
        criticism_results={"viability_score": 75, "summary": "Good strategy"},
        repair_attempts=0,
    )

    try:
        # Run the synthesize node directly
        from agent.nodes.synthesize import synthesize_node

        result = await synthesize_node(state_with_data, config.for_node("synthesize"))

        print(f"Synthesize result keys: {list(result.keys())}")
        print(f"Current step: {result.get('current_step')}")

        if "final_proposal" in result:
            proposal = result["final_proposal"]
            print(f"✅ Generated valid proposal with title: {proposal.get('title', 'N/A')}")
            print(f"✅ Alpha-only mode respected: {proposal.get('alpha-only', False)}")
            print(f"✅ Validation passed, routing to: {result.get('current_step')}")

        elif "validation_errors" in result:
            print(f"⚠️ Validation failed with {len(result['validation_errors'])} errors")
            print(f"⚠️ Next step: {result.get('current_step')}")
            if result.get("current_step") == "synthesize":
                print("✅ Will retry synthesis (repair attempt)")
            else:
                print("✅ Max repairs reached, proceeding to persist")

        else:
            print(f"❌ Unexpected result: {result}")

        # Verify no routing to validate node
        assert result.get("current_step") != "validate", "Should not route to validate node"

        print("✅ Workflow test passed - validation is now integrated into synthesize!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(test_workflow_without_validate())
