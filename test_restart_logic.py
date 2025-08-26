#!/usr/bin/env python3
"""
Test script for the restart logic in the research agent.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agent.prompts import ResearchPrompts


def test_prior_art_restart_logic():
    """Test prior art restart conditions."""
    print("Testing prior art restart logic...")

    # Test case 1: Novel idea (no restart)
    prior_art_novel = {
        "verdict": "novel",
        "total_found": 0,
        "reasoning": "No similar implementations found",
    }
    should_restart, reason = ResearchPrompts.should_restart_for_prior_art(prior_art_novel)
    assert not should_restart, f"Novel idea should not restart, but got: {reason}"
    print("✅ Novel idea correctly identified as no restart needed")

    # Test case 2: Few similar implementations (no restart)
    prior_art_few = {
        "verdict": "similar",
        "total_found": 2,
        "reasoning": "Found 2 potentially related implementations",
    }
    should_restart, reason = ResearchPrompts.should_restart_for_prior_art(prior_art_few)
    assert not should_restart, f"Few implementations should not restart, but got: {reason}"
    print("✅ Few implementations correctly identified as no restart needed")

    # Test case 3: Many similar implementations (restart)
    prior_art_many = {
        "verdict": "similar",
        "total_found": 5,
        "reasoning": "Found 5 related implementations",
    }
    should_restart, reason = ResearchPrompts.should_restart_for_prior_art(prior_art_many)
    assert should_restart, f"Many implementations should restart, but got restart={should_restart}"
    assert "similar implementations" in reason.lower(), f"Reason should mention similar implementations: {reason}"
    print("✅ Many implementations correctly identified as restart needed")


def test_criticism_restart_logic():
    """Test criticism score restart conditions."""
    print("\nTesting criticism restart logic...")

    # Test case 1: High score (no restart)
    should_restart, reason = ResearchPrompts.should_restart_for_criticism(75.0, 1)
    assert not should_restart, f"High score should not restart, but got: {reason}"
    print("✅ High viability score correctly identified as no restart needed")

    # Test case 2: Low score (restart)
    should_restart, reason = ResearchPrompts.should_restart_for_criticism(35.0, 1)
    assert should_restart, f"Low score should restart, but got restart={should_restart}"
    assert "viability score" in reason.lower(), f"Reason should mention viability score: {reason}"
    print("✅ Low viability score correctly identified as restart needed")

    # Test case 3: Low score but max iterations reached (no restart)
    should_restart, reason = ResearchPrompts.should_restart_for_criticism(35.0, 3)
    assert not should_restart, f"Max iterations should prevent restart, but got restart={should_restart}"
    assert "maximum" in reason.lower(), f"Reason should mention maximum iterations: {reason}"
    print("✅ Maximum iterations correctly prevents restart")


def test_score_extraction():
    """Test viability score extraction from criticism text."""
    print("\nTesting score extraction...")

    # Test case 1: Clear score format
    text1 = "This proposal has some issues. VIABILITY SCORE: 65"
    score1 = ResearchPrompts.extract_viability_score(text1)
    assert score1 == 65.0, f"Expected 65.0, got {score1}"
    print("✅ Clear score format extracted correctly")

    # Test case 2: Alternative format
    text2 = "The viability is moderate at 78 out of 100"
    score2 = ResearchPrompts.extract_viability_score(text2)
    assert score2 == 78.0, f"Expected 78.0, got {score2}"
    print("✅ Alternative score format extracted correctly")

    # Test case 3: No score found (default)
    text3 = "This is a criticism without any numerical score"
    score3 = ResearchPrompts.extract_viability_score(text3)
    assert score3 == 50.0, f"Expected default 50.0, got {score3}"
    print("✅ Default score returned when no score found")


def test_configuration_constants():
    """Test configuration constants."""
    print("\nTesting configuration constants...")

    assert ResearchPrompts.MIN_VIABILITY_SCORE == 51, "Min viability score should be 51"
    assert ResearchPrompts.MAX_PLANNING_ITERATIONS == 3, "Max planning iterations should be 3"
    assert ResearchPrompts.PRIOR_ART_THRESHOLD == 3, "Prior art threshold should be 3"
    print("✅ Configuration constants are correct")


if __name__ == "__main__":
    print("🧪 Running restart logic tests...\n")

    try:
        test_prior_art_restart_logic()
        test_criticism_restart_logic()
        test_score_extraction()
        test_configuration_constants()

        print("\n🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
