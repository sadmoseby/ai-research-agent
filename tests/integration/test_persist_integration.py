"""
Simple integration test for the modified persist node.
"""

import asyncio
import json
import tempfile
from pathlib import Path

from agent.config import Config
from agent.nodes.persist import persist_node
from agent.state import ResearchState


async def test_persist_node_dual_save():
    """Test that persist node saves both proposal and state."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory for test
        original_cwd = Path.cwd()
        try:
            import os

            os.chdir(temp_dir)

            # Create test state
            test_state = ResearchState()
            test_state["final_proposal"] = {
                "title": "Test Strategy",
                "summary": "A test strategy for verification",
                "alphas": {"new": [{"name": "TestAlpha", "text": "Simple test alpha"}]},
            }
            test_state["slug"] = "test_dual_save"
            test_state["validation_report"] = "Test validation passed"
            test_state["web_search_results"] = [{"title": "Search Result", "url": "http://example.com"}]
            test_state["current_step"] = "persist"

            # Create config
            config = Config()

            # Run persist node
            result = await persist_node(test_state, config)

            # Verify results
            assert result["error"] is None, f"Persist failed with error: {result.get('error')}"
            assert "proposal_path" in result
            assert "state_path" in result

            # Verify files exist
            proposal_path = Path(result["proposal_path"])
            state_path = Path(result["state_path"])

            assert proposal_path.exists(), f"Proposal file not created: {proposal_path}"
            assert state_path.exists(), f"State file not created: {state_path}"

            # Verify proposal content
            with open(proposal_path) as f:
                saved_proposal = json.load(f)
            assert saved_proposal["title"] == "Test Strategy"
            assert "alphas" in saved_proposal

            # Verify state content
            with open(state_path) as f:
                saved_state = json.load(f)
            assert saved_state["slug"] == "test_dual_save"
            assert saved_state["validation_report"] == "Test validation passed"
            assert saved_state["current_step"] == "persist"
            assert "web_search_results" in saved_state
            # Verify final_proposal was excluded from state
            assert "final_proposal" not in saved_state

            print("✅ All tests passed!")
            print(f"✅ Proposal saved to: {proposal_path}")
            print(f"✅ State saved to: {state_path}")

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    asyncio.run(test_persist_node_dual_save())
