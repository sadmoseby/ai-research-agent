#!/usr/bin/env python3
"""
Simple test script to verify the Lean Research Agent setup.
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from agent.config import Config
    from agent.state import ResearchState

    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_config():
    """Test configuration loading."""
    try:
        # Test schema loading
        config = Config(openai_api_key="test_key")
        schema = config.get_schema()
        print(f"✅ Schema loaded with {len(schema.get('properties', {}))} root properties")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def test_state():
    """Test state structure."""
    try:
        state = ResearchState(
            idea="test strategy",
            alpha_only=True,
            slug="test",
            current_step="plan",
            repair_attempts=0,
        )
        print("✅ State structure valid")
        return True
    except Exception as e:
        print(f"❌ State test failed: {e}")
        return False


def test_proposals_dir():
    """Test proposals directory creation."""
    try:
        proposals_dir = Path("proposals")
        proposals_dir.mkdir(exist_ok=True)
        print("✅ Proposals directory ready")
        return True
    except Exception as e:
        print(f"❌ Proposals directory test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing Lean Research Agent setup...\n")

    tests = [
        ("Configuration", test_config),
        ("State Management", test_state),
        ("File System", test_proposals_dir),
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"Testing {name}...")
        if test_func():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The agent is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.template to .env")
        print("2. Add your OPENAI_API_KEY to .env")
        print("3. Run: python main.py propose --idea 'your research idea'")
    else:
        print("❌ Some tests failed. Please check the setup.")
        sys.exit(1)


if __name__ == "__main__":
    main()
