---
name: github-cli
description: Execute GitHub CLI (gh) commands for repository management, issues, pull requests, workflows, and releases. Use when the user wants to interact with GitHub repositories, create/manage issues or PRs, trigger workflows, or perform any GitHub operations. Covers both solo developer workflows and team collaboration patterns.
---

# GitHub CLI (gh) Skill

This skill provides comprehensive GitHub CLI integration for managing repositories, issues, pull requests, workflows, and releases through the `gh` command-line tool.

## Prerequisites

- GitHub CLI (`gh`) must be installed and authenticated
- Active internet connection for GitHub API access
- Appropriate permissions for the target repository

## Quick Command Reference

### Common Commands

```bash
# Repository operations
gh repo view [owner/repo]                    # View repository details
gh repo clone <owner/repo>                   # Clone a repository
gh repo fork <owner/repo>                    # Fork a repository
gh repo create [name]                        # Create a new repository

# Issue operations
gh issue list                                # List issues
gh issue view <number>                       # View issue details
gh issue create                              # Create an issue (interactive)
gh issue close <number>                      # Close an issue

# Pull request operations
gh pr list                                   # List pull requests
gh pr view <number>                          # View PR details
gh pr create                                 # Create a PR (interactive)
gh pr checkout <number>                      # Check out a PR locally
gh pr merge <number>                         # Merge a pull request
gh pr review <number>                        # Review a pull request

# Workflow operations
gh workflow list                             # List workflows
gh workflow view <workflow>                  # View workflow details
gh workflow run <workflow>                   # Trigger a workflow
gh run list                                  # List workflow runs
gh run view <run-id>                         # View run details
gh run watch <run-id>                        # Watch a run in real-time

# Release operations
gh release list                              # List releases
gh release view <tag>                        # View release details
gh release create <tag>                      # Create a release
```

## Command Execution Pattern

When executing gh commands:

1. **Check context**: Verify you're in the correct repository directory or use `-R owner/repo` flag
2. **Use appropriate flags**: Add `--json` for structured output when parsing is needed
3. **Handle errors gracefully**: Parse stderr and provide clear error messages
4. **Confirm destructive actions**: Always confirm before deleting, merging, or closing

Example execution:
```bash
# Get JSON output for parsing
gh issue list --json number,title,state,labels

# Specify repository explicitly
gh pr view 42 -R octocat/Hello-World

# Use flags for non-interactive operations
gh pr create --title "Feature" --body "Description" --base main
```

## Detailed Guides (Load as Needed)

For comprehensive workflows and advanced usage, refer to these detailed guides:

### Repository Management
See [REPO.md](REPO.md) for:
- Creating and configuring repositories
- Cloning and forking workflows
- Repository settings and management
- Branch protection and settings

### Issue Management
See [ISSUES.md](ISSUES.md) for:
- Creating and managing issues
- Labels, milestones, and projects
- Issue templates and automation
- Searching and filtering issues

### Pull Request Workflows
See [PR.md](PR.md) for:
- Creating and managing pull requests
- Code review workflows
- PR checks and status
- Merge strategies and options

### GitHub Actions & Workflows
See [WORKFLOW.md](WORKFLOW.md) for:
- Listing and viewing workflows
- Triggering workflow runs
- Monitoring and debugging runs
- Working with workflow artifacts

### Release Management
See [RELEASE.md](RELEASE.md) for:
- Creating and managing releases
- Uploading release assets
- Draft releases and pre-releases
- Release automation patterns

### Team Collaboration
See [TEAM.md](TEAM.md) for:
- Multi-developer workflows
- Code review best practices
- Branch strategies for teams
- Managing permissions and teams

### Solo Developer Workflows
See [SOLO-DEV.md](SOLO-DEV.md) for:
- Personal project workflows
- Quick PR and issue patterns
- Efficient solo development with gh
- Personal automation tips

## Helper Scripts

The `scripts/` directory contains helper scripts for common operations:

- `create-feature-branch.sh` - Create and push a feature branch
- `pr-workflow.sh` - Complete PR creation workflow
- `issue-from-todo.sh` - Create issues from TODO comments
- `sync-fork.sh` - Sync a fork with upstream

Execute scripts as needed:
```bash
bash scripts/create-feature-branch.sh "feature-name"
```

## Best Practices

### 1. Always verify context
```bash
# Check current repository
gh repo view

# Or specify repository explicitly
gh issue list -R owner/repo
```

### 2. Use structured output for automation
```bash
# JSON output for parsing
gh pr list --json number,title,state | jq '.[] | select(.state == "OPEN")'

# Template output for custom formatting
gh issue list --template '{{range .}}{{.number}}: {{.title}}{{"\n"}}{{end}}'
```

### 3. Combine with git commands
```bash
# Create feature branch, push, and open PR
git checkout -b feature/new-feature
git push -u origin feature/new-feature
gh pr create --fill
```

### 4. Use aliases for common workflows
```bash
# Configure gh aliases
gh alias set prc 'pr create --fill'
gh alias set prv 'pr view --web'
```

## Error Handling

Common errors and solutions:

**Authentication errors**:
```bash
# Re-authenticate
gh auth login
gh auth status  # Verify authentication
```

**Permission errors**:
- Verify you have appropriate access to the repository
- Check if the repository is private and you're authenticated with the correct account

**Not in a git repository**:
- Use the `-R owner/repo` flag to specify the repository explicitly
- Or navigate to the repository directory first

## Output Formatting

The gh CLI supports multiple output formats:

```bash
# JSON output (best for parsing)
gh issue list --json number,title,state

# Template output (custom formatting)
gh pr list --template '{{range .}}PR #{{.number}}: {{.title}}{{"\n"}}{{end}}'

# Default terminal output (human-readable)
gh issue list
```

## Tips and Tricks

1. **Interactive mode**: Omit flags to get interactive prompts
   ```bash
   gh pr create  # Interactive PR creation
   ```

2. **Open in browser**: Use `--web` flag to open in browser
   ```bash
   gh issue view 42 --web
   gh pr view 123 --web
   ```

3. **Shell completion**: Enable for faster command entry
   ```bash
   gh completion -s bash > /etc/bash_completion.d/gh
   ```

4. **Configuration**: Customize gh behavior
   ```bash
   gh config set editor vim
   gh config set pager less
   ```

## When to Use This Skill

Use this skill when the user wants to:
- Create or manage GitHub repositories
- Work with issues, pull requests, or discussions
- Trigger or monitor GitHub Actions workflows
- Create or manage releases
- Perform any GitHub operation from the command line
- Automate GitHub workflows
- Follow team collaboration patterns
- Implement solo developer workflows

## Next Steps

Based on the user's request, load the appropriate detailed guide:
- Repository operations → Load REPO.md
- Issue management → Load ISSUES.md
- Pull request workflows → Load PR.md
- Workflow/Actions operations → Load WORKFLOW.md
- Release operations → Load RELEASE.md
- Team collaboration → Load TEAM.md
- Solo development → Load SOLO-DEV.md
