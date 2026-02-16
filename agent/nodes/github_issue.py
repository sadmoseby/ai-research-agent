"""
GitHub Issue creation node using the gh CLI tool.
"""

import os
import subprocess
import tempfile
from typing import Any, Dict, Optional

GITHUB_BODY_LIMIT = 65536

from ..config import Config, get_logger
from ..state import ResearchState

# Get logger for this node
logger = get_logger("nodes.github_issue")


def _build_gh_env(token: Optional[str]) -> Dict[str, str]:
    """Return an env dict with GH_TOKEN set when a token is provided."""
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    return env


async def github_issue_node(state: ResearchState, config: Config) -> Dict[str, Any]:
    """Create a GitHub issue from the persisted issue.md using the gh CLI."""
    logger.info("Starting GitHub issue creation node")

    issue_path = state.get("issue_path")
    idea = config.idea or state.get("idea") or config.slug or state.get("slug", "research_proposal")

    if not issue_path:
        error_msg = "No issue path in state - ensure persist node ran successfully"
        logger.error(error_msg)
        return {"error": error_msg}

    github_token = config.github_token
    github_repo: Optional[str] = None

    owner = config.github_owner or ""
    repo = config.github_repository or ""
    if owner and repo:
        github_repo = f"{owner}/{repo}"
        logger.info("Using GitHub repo from config: %s", github_repo)

    if github_token:
        logger.info("GitHub token loaded from config")

    title = f"Research Proposal: {idea}"

    # Read and truncate body if it exceeds GitHub's limit
    with open(issue_path, encoding="utf-8") as f:
        body = f.read()
    if len(body) > GITHUB_BODY_LIMIT:
        truncation_note = "\n\n_(proposal truncated — full JSON saved locally)_"
        original_len = len(body)
        body = body[: GITHUB_BODY_LIMIT - len(truncation_note)] + truncation_note
        logger.warning("Issue body truncated from %d to %d chars", original_len, len(body))

    # Write (possibly truncated) body to a temp file for gh CLI
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(body)
        tmp_path = tmp.name

    cmd = ["gh", "issue", "create", "--title", title, "--body-file", tmp_path]
    if github_repo:
        cmd.extend(["--repo", github_repo])

    logger.info("Running: %s", " ".join(cmd))
    print(f"🐙 Creating GitHub issue: {title}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=_build_gh_env(github_token),
        )
    except subprocess.TimeoutExpired:
        os.unlink(tmp_path)
        error_msg = "gh issue create timed out after 30 seconds"
        logger.error(error_msg)
        return {"error": error_msg}
    except FileNotFoundError:
        os.unlink(tmp_path)
        error_msg = "gh CLI not found - ensure GitHub CLI is installed and in PATH"
        logger.error(error_msg)
        return {"error": error_msg}
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if result.returncode != 0:
        error_msg = f"gh issue create failed: {result.stderr.strip()}"
        logger.error(error_msg)
        return {"error": error_msg}

    # gh issue create prints the new issue URL to stdout
    issue_url = result.stdout.strip()
    logger.info("Successfully created GitHub issue: %s", issue_url)
    print(f"✅ GitHub issue created: {issue_url}")

    return {"github_issue_url": issue_url}
