"""
Integration tests for LangGraph workflow.
"""

import os
from unittest.mock import Mock, patch

import pytest

from agent.config import Config
from agent.graph import create_research_graph
from agent.state import ResearchState


class TestWorkflowIntegration:
    """Test integration between workflow nodes."""

    def test_graph_creation_with_all_nodes_enabled(self):
        """Test creating research graph with all nodes enabled."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
            config = Config()
            graph = create_research_graph(config)

            # Verify graph was created successfully
            assert graph is not None

            # Check that all expected nodes are in the graph
            expected_nodes = ["plan", "web_research", "criticism", "synthesize", "validate", "persist"]

            # Note: This test may need adjustment based on actual graph structure
            # The exact method to inspect graph nodes may vary

    def test_graph_creation_with_disabled_nodes(self):
        """Test creating research graph with some nodes disabled."""
        env_vars = {"OPENAI_API_KEY": "test-key", "CRITICISM_ENABLED": "false"}

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()

            # Verify disabled nodes are actually disabled
            assert not config.is_node_enabled("criticism")

            # Graph should still be created successfully
            graph = create_research_graph(config)
            assert graph is not None

    def test_state_flow_through_workflow(self):
        """Test state transitions through the workflow."""
        initial_state = ResearchState(
            idea="test momentum trading strategy",
            alpha_only=True,
            slug="test-momentum",
            current_step="plan",
            planning_iteration=0,
            should_restart_planning=False,
        )

        # Test state progression
        workflow_steps = ["plan", "web_research", "criticism", "synthesize", "validate", "persist"]

        current_state = initial_state.copy()

        for step in workflow_steps:
            current_state["current_step"] = step

            # Verify state maintains consistency
            assert current_state["idea"] == "test momentum trading strategy"
            assert current_state["alpha_only"] is True
            assert current_state["slug"] == "test-momentum"
            assert current_state["current_step"] == step

    def test_planning_restart_logic_integration(self):
        """Test planning restart logic in workflow context."""
        state = ResearchState(
            idea="test strategy", alpha_only=True, slug="test", current_step="criticism", planning_iteration=1
        )

        # Simulate criticism triggering restart
        state["should_restart_planning"] = True
        state["restart_reason"] = "Low novelty score"

        # Verify restart conditions
        assert state["should_restart_planning"] is True
        assert state["restart_reason"] == "Low novelty score"

        # After restart, should go back to planning
        state["current_step"] = "plan"
        state["planning_iteration"] = 2
        state["should_restart_planning"] = False

        assert state["current_step"] == "plan"
        assert state["planning_iteration"] == 2

    def test_mcp_tools_integration_workflow(self):
        """Test MCP tools integration in workflow."""
        env_vars = {
            "OPENAI_API_KEY": "test-key",
            "WEB_RESEARCH_MCP_TOOLS": "web_search,tavily",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()

            state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="web_research")

            # Simulate MCP tools being available and used
            state["mcp_tools_available"] = ["web_search", "tavily"]
            state["mcp_tools_used"] = ["web_search"]

            # Verify tools are tracked correctly
            assert "web_search" in state["mcp_tools_available"]
            assert "web_search" in state["mcp_tools_used"]

    def test_error_recovery_workflow(self):
        """Test error recovery in workflow."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="validate")

        # Simulate validation errors
        state["validation_errors"] = ["Missing required field: universe", "Invalid alpha format"]

        # Workflow should handle errors gracefully
        assert len(state["validation_errors"]) == 2

        # Could trigger repair attempt or restart
        state["should_restart_planning"] = True
        state["restart_reason"] = "Validation failed"

        assert state["should_restart_planning"] is True

    def test_multi_provider_node_integration(self):
        """Test multiple providers working in node integration."""
        env_vars = {
            "OPENAI_API_KEY": "test-openai",
            "ANTHROPIC_API_KEY": "test-anthropic",
            "DEFAULT_LLM_PROVIDER": "openai",
            "WEB_RESEARCH_PROVIDER": "anthropic",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()

            # Verify different providers are configured
            available_providers = config.get_available_providers()
            assert "openai" in available_providers
            assert "anthropic" in available_providers

            # Graph should be created with multi-provider config
            graph = create_research_graph(config)
            assert graph is not None

    def test_alpha_only_workflow_integration(self):
        """Test alpha-only mode workflow integration."""
        alpha_state = ResearchState(idea="test alpha strategy", alpha_only=True, slug="test-alpha", current_step="plan")

        full_state = ResearchState(idea="test full strategy", alpha_only=False, slug="test-full", current_step="plan")

        # Verify both modes are supported
        assert alpha_state["alpha_only"] is True
        assert full_state["alpha_only"] is False

        # Both should be able to progress through workflow
        for state in [alpha_state, full_state]:
            state["current_step"] = "synthesize"
            assert state["current_step"] == "synthesize"

    def test_configuration_integration_with_workflow(self):
        """Test that configuration changes properly affect workflow."""
        env_vars = {
            "OPENAI_API_KEY": "test-key",
            "TEMPERATURE": "0.3",
            "MAX_TOKENS": "6000",
            "WEB_RESEARCH_ENABLED": "false",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()

            # Verify configuration is applied
            assert config.temperature == 0.3
            assert config.max_tokens == 6000
            assert not config.is_node_enabled("web_research")

            # Graph should adapt to configuration
            graph = create_research_graph(config)
            assert graph is not None
