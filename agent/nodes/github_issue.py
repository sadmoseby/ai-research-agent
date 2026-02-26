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


def _create_github_branch(
    owner: str,
    repo: str,
    base_branch: str,
    new_branch: str,
    token: Optional[str],
) -> Optional[str]:
    """Create a new GitHub branch from the tip of base_branch.

    Returns an error message string on failure, or None on success.
    """
    env = _build_gh_env(token)
    full_repo = f"{owner}/{repo}"

    # 1. Resolve the SHA of the base branch
    get_sha_cmd = [
        "gh",
        "api",
        f"repos/{full_repo}/git/refs/heads/{base_branch}",
        "--jq",
        ".object.sha",
    ]
    logger.info("Resolving SHA of base branch '%s'", base_branch)
    result = subprocess.run(get_sha_cmd, capture_output=True, text=True, timeout=30, env=env)
    if result.returncode != 0:
        return f"Failed to resolve SHA for '{base_branch}': {result.stderr.strip()}"

    sha = result.stdout.strip()
    if not sha:
        return f"Empty SHA returned for branch '{base_branch}'"

    logger.info("Base branch '%s' is at SHA %s", base_branch, sha)

    # 2. Create the new branch pointing at that SHA
    create_cmd = [
        "gh",
        "api",
        f"repos/{full_repo}/git/refs",
        "--method",
        "POST",
        "-f",
        f"ref=refs/heads/{new_branch}",
        "-f",
        f"sha={sha}",
    ]
    logger.info("Creating branch '%s' from SHA %s", new_branch, sha)
    result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=30, env=env)
    if result.returncode != 0:
        return f"Failed to create branch '{new_branch}': {result.stderr.strip()}"

    logger.info("Successfully created branch '%s'", new_branch)
    return None  # success


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

    # --- Explicit branch creation ---
    new_branch_name = state.get("new_branch_name", "")
    base_branch = state.get("branch_name", "") or (config.branch_name or "")

    if new_branch_name and owner and repo:
        print(f"🌿 Creating branch '{new_branch_name}' from '{base_branch or 'main'}' ...")
        branch_error = _create_github_branch(
            owner=owner,
            repo=repo,
            base_branch=base_branch or "main",
            new_branch=new_branch_name,
            token=github_token,
        )
        if branch_error:
            logger.error("Branch creation failed: %s", branch_error)
            return {"error": f"Branch creation failed: {branch_error}"}
        print(f"✅ Branch '{new_branch_name}' created successfully")
    else:
        logger.warning(
            "Skipping branch creation (new_branch_name=%r, owner=%r, repo=%r)",
            new_branch_name,
            owner,
            repo,
        )

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
