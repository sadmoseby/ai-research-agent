"""
Unit tests for research state management.
"""

from agent.state import ResearchState


class TestResearchState:
    """Test research state functionality."""

    def test_research_state_initialization(self):
        """Test basic state initialization."""
        state = ResearchState(
            idea="test momentum strategy",
            alpha_only=True,
            slug="test-momentum",
            current_step="plan",
            planning_iteration=0,
            should_restart_planning=False,
        )

        assert state["idea"] == "test momentum strategy"
        assert state["alpha_only"] is True
        assert state["slug"] == "test-momentum"
        assert state["current_step"] == "plan"
        assert state["planning_iteration"] == 0
        assert state["should_restart_planning"] is False

    def test_research_state_defaults(self):
        """Test state with minimal required fields."""
        state = ResearchState(idea="test strategy", alpha_only=False, slug="test", current_step="plan")

        assert state["idea"] == "test strategy"
        assert state["alpha_only"] is False
        assert state["slug"] == "test"
        assert state["current_step"] == "plan"

    def test_state_progression(self):
        """Test state progression through workflow steps."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="plan")

        # Progress through workflow steps
        workflow_steps = ["plan", "web_research", "prior_art", "criticism", "synthesize", "validate", "persist"]

        for step in workflow_steps:
            state["current_step"] = step
            assert state["current_step"] == step

    def test_research_data_accumulation(self):
        """Test accumulating research data."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="plan")

        # Add plan data
        state["research_plan"] = "momentum-based strategy analysis"
        state["search_queries"] = ["momentum trading", "trend following"]

        # Add web research data
        state["web_search_results"] = [{"title": "Momentum Trading", "url": "example.com"}]

        assert state["research_plan"] == "momentum-based strategy analysis"
        assert len(state["search_queries"]) == 2
        assert len(state["web_search_results"]) == 1

    def test_restart_logic_tracking(self):
        """Test restart logic tracking."""
        state = ResearchState(
            idea="test strategy", alpha_only=True, slug="test", current_step="criticism", should_restart_planning=False
        )

        # Set restart condition
        state["should_restart_planning"] = True
        state["restart_reason"] = "Low quality score"

        assert state["should_restart_planning"] is True
        assert state["restart_reason"] == "Low quality score"

    def test_planning_iterations_tracking(self):
        """Test planning iterations tracking."""
        state = ResearchState(
            idea="test strategy", alpha_only=True, slug="test", current_step="plan", planning_iteration=0
        )

        # Increment planning iterations
        state["planning_iteration"] = 1
        assert state["planning_iteration"] == 1

        state["planning_iteration"] = 2
        assert state["planning_iteration"] == 2

    def test_mcp_tools_tracking(self):
        """Test MCP tools availability and usage tracking."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="web_research")

        # Track available tools
        state["mcp_tools_available"] = ["web_search", "tavily", "github"]

        # Track used tools
        state["mcp_tools_used"] = ["web_search", "tavily"]

        assert len(state["mcp_tools_available"]) == 3
        assert len(state["mcp_tools_used"]) == 2
        assert "web_search" in state["mcp_tools_used"]

    def test_criticism_tracking(self):
        """Test criticism results and scoring."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="criticism")

        # Add criticism results
        state["criticism_results"] = {
            "novelty_score": 75,
            "feasibility_score": 85,
            "overall_assessment": "Good potential",
        }
        state["criticism_score"] = 80.0

        assert state["criticism_results"]["novelty_score"] == 75
        assert state["criticism_score"] == 80.0

    def test_validation_tracking(self):
        """Test validation error tracking."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="validate")

        # Add validation errors
        state["validation_errors"] = ["Missing required field: universe", "Invalid alpha format"]
        state["validation_report"] = "Schema validation failed"

        assert len(state["validation_errors"]) == 2
        assert state["validation_report"] == "Schema validation failed"

    def test_final_output_tracking(self):
        """Test final proposal and output tracking."""
        state = ResearchState(idea="test strategy", alpha_only=True, slug="test", current_step="persist")

        # Add final proposal
        state["final_proposal"] = {
            "title": "Test Momentum Strategy",
            "alphas": {"new": [{"name": "TestAlpha", "text": "Buy momentum"}]},
        }
        state["proposal_path"] = "/proposals/test-momentum.json"

        assert state["final_proposal"]["title"] == "Test Momentum Strategy"
        assert state["proposal_path"] == "/proposals/test-momentum.json"

    def test_alpha_only_mode(self):
        """Test alpha-only mode behavior."""
        alpha_state = ResearchState(idea="test alpha strategy", alpha_only=True, slug="test-alpha", current_step="plan")

        full_state = ResearchState(idea="test full strategy", alpha_only=False, slug="test-full", current_step="plan")

        assert alpha_state["alpha_only"] is True
        assert full_state["alpha_only"] is False
