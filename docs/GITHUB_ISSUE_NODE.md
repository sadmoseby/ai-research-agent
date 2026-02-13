# GitHub Issue Node

## Overview

The `github_issue` node creates GitHub issues from generated research proposals using the GitHub CLI (`gh` command). This node is **optional** and only executes when explicitly enabled via configuration.

## Purpose

- Automatically create GitHub issues containing research proposals
- Integrate research workflow with GitHub project management
- Enable tracking and discussion of generated proposals
- Optional step that doesn't block the main research workflow

## Configuration

### Environment Variables

```bash
# Enable GitHub issue creation
GITHUB_ISSUE_ENABLED=true
UPLOAD_TO_GITHUB=true

# Repository configuration
GITHUB_OWNER=your-org-name
GITHUB_REPOSITORY=your-repo-name

# Authentication (required for gh CLI)
GITHUB_TOKEN=ghp_your_github_token
```

### Prerequisites

1. **GitHub CLI installed**: The `gh` command must be available
   ```bash
   # Install on macOS
   brew install gh

   # Install on Linux
   sudo apt install gh  # or appropriate package manager
   ```

2. **GitHub Token**: Set `GITHUB_TOKEN` environment variable or authenticate via `gh auth login`

3. **Repository Access**: Token must have permissions to create issues in the target repository

## Workflow Integration

### Standard Flow

```
... → synthesize → persist → github_issue → END
```

### Conditional Routing

The `persist` node conditionally routes to `github_issue`:

- If `UPLOAD_TO_GITHUB=true` AND `GITHUB_ISSUE_ENABLED=true` → create issue
- Otherwise → skip to END

### Example Configurations

#### Enabled (with issue creation)
```bash
export UPLOAD_TO_GITHUB=true
export GITHUB_ISSUE_ENABLED=true
export GITHUB_OWNER=myorg
export GITHUB_REPOSITORY=research-proposals
python main.py propose --idea "momentum strategy"
```

#### Disabled (default)
```bash
# Don't set UPLOAD_TO_GITHUB or set to false
python main.py propose --idea "momentum strategy"
```

## Implementation Details

### File Location
- **Path**: `agent/nodes/github_issue.py`
- **Function**: `github_issue_node(state: ResearchState, config: Config)`

### Input Requirements

From state:
- `issue_path`: Path to the markdown file created by persist node
- `idea` or `slug`: Used for issue title

From config:
- `github_token`: Authentication token
- `github_owner`: Repository owner/organization
- `github_repository`: Repository name

### GitHub CLI Command

The node executes:
```bash
gh issue create \
  --title "Research Proposal: {idea}" \
  --body-file {issue_path} \
  --repo {owner}/{repo}
```

### Output

Returns to state:
- `github_issue_url`: URL of created issue (on success)
- `error`: Error message (on failure)

## Issue Format

The issue body is created by the persist node as a markdown file containing:

```markdown
# Research Proposal: {idea}

## Research Context
- Alpha-only mode: Yes/No
- Components: [list]

## Proposal Summary
[JSON proposal formatted as markdown]

## Key Features
- Strategy description
- Target instruments
- Risk parameters
- Expected behavior

## Next Steps
1. Review proposal
2. Implement algorithm
3. Run backtests
4. Evaluate results
```

## Error Handling

### Common Errors

1. **gh CLI not found**
   ```
   Error: gh command not found. Please install GitHub CLI.
   ```
   **Solution**: Install gh CLI or disable the node

2. **Authentication failed**
   ```
   Error: gh auth status failed
   ```
   **Solution**: Set GITHUB_TOKEN or run `gh auth login`

3. **Repository not found**
   ```
   Error: repository not found or access denied
   ```
   **Solution**: Verify GITHUB_OWNER and GITHUB_REPOSITORY, check permissions

4. **Issue path missing**
   ```
   Error: No issue path in state
   ```
   **Solution**: Ensure persist node ran successfully

### Graceful Degradation

- Node failures don't block the workflow
- Errors are logged but don't prevent proposal generation
- State includes error information for debugging

## Node Enable/Disable

### Disable GitHub Integration

```bash
# Method 1: Disable node entirely
export GITHUB_ISSUE_ENABLED=false

# Method 2: Don't trigger upload
export UPLOAD_TO_GITHUB=false
# (GITHUB_ISSUE_ENABLED can remain true)

# Method 3: Both
unset UPLOAD_TO_GITHUB
unset GITHUB_ISSUE_ENABLED
```

### Benefits of Disabling

- Faster execution (no GitHub API calls)
- No GitHub CLI dependency required
- Useful for local development/testing
- Can still save proposals locally via persist node

## Use Cases

### Development Workflow
1. Generate proposal locally
2. Review JSON output
3. Manually create issue if needed

### Production Workflow
1. Auto-generate proposals
2. Auto-create GitHub issues
3. Team reviews in GitHub
4. Track implementation progress

### Integration with CI/CD
```yaml
# GitHub Actions example
- name: Generate Research Proposal
  env:
    UPLOAD_TO_GITHUB: true
    GITHUB_ISSUE_ENABLED: true
    GITHUB_OWNER: ${{ github.repository_owner }}
    GITHUB_REPOSITORY: ${{ github.event.repository.name }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python main.py propose --idea "${{ inputs.strategy_idea }}"
```

## Best Practices

1. **Token Security**: Use GitHub secrets, never commit tokens
2. **Repository Organization**: Use dedicated repo for research proposals
3. **Issue Labels**: Consider adding labels via gh CLI `--label` flag
4. **Assignees**: Auto-assign issues using `--assignee` flag
5. **Milestones**: Link to milestones using `--milestone` flag

## Future Enhancements

Potential additions to the node:

- **Labels**: Automatic labeling based on proposal content
- **Projects**: Add issues to GitHub Projects
- **Templates**: Use issue templates for consistent formatting
- **Comments**: Post analysis results as comments
- **Status**: Update issue status based on implementation progress
