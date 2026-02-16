#!/usr/bin/env python3
"""
Test script to run just the persist + github_issue nodes against an existing proposal.

Usage:
    .venv/bin/python test_persist_github.py [proposal_json_path]

Example:
    .venv/bin/python test_persist_github.py proposals/develop_a_momentum_based_alpha_strategy_using_rsi.json
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agent.config import Config
from agent.nodes.github_issue import github_issue_node
from agent.nodes.persist import persist_node


async def main(proposal_path: str):
    config = Config.from_dotenv()

    proposal_file = Path(proposal_path)
    if not proposal_file.exists():
        print(f"❌ Proposal file not found: {proposal_file}")
        sys.exit(1)

    with open(proposal_file, encoding="utf-8") as f:
        proposal = json.load(f)

    slug = proposal_file.stem  # filename without extension
    print(f"📄 Loaded proposal: {proposal_file} ({proposal_file.stat().st_size // 1024}KB)")

    state = {
        "final_proposal": proposal,
        "slug": slug,
        "output_dir": str(proposal_file.parent),
        "upload_to_github": config.upload_to_github,
        "idea": config.idea or slug,
        "branch_name": config.branch_name or "",
        "image_name": config.image_name or "",
    }

    # Run persist node
    print("\n--- Running persist node ---")
    persist_result = await persist_node(state, config)
    state.update(persist_result)

    if persist_result.get("error"):
        print(f"❌ Persist failed: {persist_result['error']}")
        sys.exit(1)

    print(f"✅ issue.md written to: {persist_result.get('issue_path')}")

    if not config.upload_to_github:
        print("ℹ️  UPLOAD_TO_GITHUB=false — skipping GitHub issue creation")
        return

    # Run github_issue node
    print("\n--- Running github_issue node ---")
    github_result = await github_issue_node(state, config)

    if github_result.get("error"):
        print(f"❌ GitHub issue failed: {github_result['error']}")
        sys.exit(1)

    print(f"✅ GitHub issue created: {github_result.get('github_issue_url')}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "proposals/develop_a_momentum_based_alpha_strategy_using_rsi.json"
    asyncio.run(main(path))
