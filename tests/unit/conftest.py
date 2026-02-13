"""
Unit test configuration.
"""

import importlib
import sys

import pytest


@pytest.fixture(autouse=True, scope="function")
def reset_research_prompts():
    """Reset ResearchPrompts to ensure clean state for each unit test."""
    # Complete module reset
    modules_to_remove = []
    for module_name in sys.modules:
        if module_name.startswith("agent"):
            modules_to_remove.append(module_name)

    for module_name in modules_to_remove:
        del sys.modules[module_name]

    # Fresh import
    from agent.prompts import ResearchPrompts

    # Reset thresholds to defaults
    ResearchPrompts.set_thresholds(min_viability_score=51, max_planning_iterations=3)

    yield

    # No cleanup needed - next test will reset again
