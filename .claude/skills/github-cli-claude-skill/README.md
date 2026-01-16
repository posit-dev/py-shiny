# GitHub CLI Claude Skill

A comprehensive Claude Code skill that provides GitHub CLI (`gh`) integration for managing repositories, issues, pull requests, workflows, and releases. Designed for both solo developers and team-based workflows.

## Overview

This skill enables Claude to execute GitHub operations using the `gh` CLI, providing:

- **Repository Management**: Create, clone, fork, and configure repositories
- **Issue Tracking**: Create, manage, and track issues with labels and milestones
- **Pull Request Workflows**: Complete PR lifecycle from creation to merge
- **GitHub Actions**: Trigger, monitor, and manage workflow runs
- **Release Management**: Create and manage releases with artifacts
- **Team Collaboration**: Code review, sprint planning, and team coordination
- **Solo Developer Tools**: Optimized workflows for personal projects

## Installation

### Prerequisites

1. **GitHub CLI**: The skill requires `gh` CLI to be installed and authenticated.

   **Installation:**
   - macOS: `brew install gh`
   - Linux: See [GitHub CLI installation](https://github.com/cli/cli#installation)
   - Windows: `winget install --id GitHub.cli` or `choco install gh`

2. **Authentication**: Authenticate with GitHub
   ```bash
   gh auth login
   ```

3. **Claude Code**: This skill is designed for [Claude Code](https://code.claude.com)

### Install the Skill

#### Quick Install (One-Liner)

The easiest way to install:

```bash
# User-level (recommended - available in all projects)
bash <(curl -s https://raw.githubusercontent.com/doug-skinner/github-cli-claude-skill/main/install.sh)

# Or for project-specific installation
bash <(curl -s https://raw.githubusercontent.com/doug-skinner/github-cli-claude-skill/main/install.sh) --project
```

#### Option 1: Clone Directly

Install for all your projects:

```bash
# Clone directly into your user skills directory
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/doug-skinner/github-cli-claude-skill.git
```

That's it! The skill will be available in all Claude Code sessions.

#### Option 2: Project-Specific Installation

Install for a specific project only:

```bash
# Navigate to your project
cd /path/to/your/project

# Clone into project skills directory
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/doug-skinner/github-cli-claude-skill.git
```

#### Option 3: Download and Copy

If you don't want to use git:

1. Download this repository as a ZIP file
2. Extract it
3. Copy the `github-cli-claude-skill` folder to:
   - `~/.claude/skills/` for user-level
   - `your-project/.claude/skills/` for project-specific

#### Verify Installation

Restart Claude Code, then ask:
```
"List my open GitHub issues"
```

If the skill is installed correctly, Claude will execute the `gh` command to list your issues.

## Usage

### Basic Usage

Simply ask Claude to perform GitHub operations:

```
"Create a new issue for fixing the login bug"
"List all open pull requests"
"Create a new feature branch called user-authentication"
"Merge pull request #42"
"Create a release for version 1.0.0"
```

### Reference Documentation

The skill includes comprehensive reference documentation for different workflows:

- **[REPO.md](REPO.md)** - Repository management operations
- **[ISSUES.md](ISSUES.md)** - Issue tracking and management
- **[PR.md](PR.md)** - Pull request workflows
- **[WORKFLOW.md](WORKFLOW.md)** - GitHub Actions and workflows
- **[RELEASE.md](RELEASE.md)** - Release management
- **[TEAM.md](TEAM.md)** - Team collaboration workflows
- **[SOLO-DEV.md](SOLO-DEV.md)** - Solo developer workflows

Claude will automatically load these guides as needed based on your requests.

### Helper Scripts

The skill includes several helper scripts in the `scripts/` directory:

#### create-feature-branch.sh
Create and push a feature branch with optional issue linking:
```bash
bash scripts/create-feature-branch.sh user-authentication 42
```

#### pr-workflow.sh
Interactive PR creation workflow:
```bash
bash scripts/pr-workflow.sh
```

#### issue-from-todo.sh
Create GitHub issues from TODO comments in code:
```bash
bash scripts/issue-from-todo.sh --create
```

#### sync-fork.sh
Sync a forked repository with upstream:
```bash
bash scripts/sync-fork.sh main
```

## Examples

### Solo Developer Workflow

```
User: "I want to start a new feature for adding dark mode"

Claude executes:
1. Creates a feature branch: feature/dark-mode
2. Pushes the branch to GitHub
3. Creates an issue to track the work
4. Provides guidance on next steps
```

### Team Collaboration

```
User: "List all PRs that need my review"

Claude executes:
1. Queries PRs with review-requested:@me
2. Displays list with PR numbers, titles, and authors
3. Offers to check out a PR for local testing
```

### Release Management

```
User: "Create a new release for version 2.1.0"

Claude executes:
1. Verifies the version tag
2. Generates release notes from commits
3. Creates the GitHub release
4. Lists the release URL
```

## Workflow Examples

### Quick Feature Development
```bash
# 1. Create feature branch
bash scripts/create-feature-branch.sh new-feature

# 2. Make changes
# ... edit files ...

# 3. Create PR
bash scripts/pr-workflow.sh
```

### Team Code Review
```bash
# List PRs needing review
gh pr list --search "review-requested:@me"

# Check out and test PR
gh pr checkout 123

# Review and approve
gh pr review 123 --approve --body "LGTM!"
```

### Sprint Planning
```bash
# Assign issues to sprint milestone
gh issue edit 101 --milestone "Sprint 5"
gh issue edit 102 --milestone "Sprint 5"

# Assign to team members
gh issue edit 101 --add-assignee alice
gh issue edit 102 --add-assignee bob
```

## Features

### Repository Operations
- Create, clone, fork repositories
- Configure branch protection
- Manage repository settings
- Archive and delete repositories

### Issue Management
- Create and edit issues
- Labels, milestones, and projects
- Search and filter issues
- Bulk operations

### Pull Requests
- Create and manage PRs
- Code review workflow
- Merge strategies
- PR checks and status

### GitHub Actions
- List and trigger workflows
- Monitor workflow runs
- Download artifacts
- Manage secrets and variables

### Releases
- Create releases with assets
- Auto-generate release notes
- Manage pre-releases and drafts
- Download release assets

### Team Features
- Code owner assignments
- Review workflows
- Sprint planning tools
- Team metrics and reporting

### Solo Developer Tools
- Personal TODO tracking
- Quick PR workflows
- Efficient issue management
- Personal automation scripts

## Configuration

### Custom Aliases

You can create gh aliases for frequently used commands:

```bash
# Quick PR creation
gh alias set prc 'pr create --fill'

# Quick PR view in browser
gh alias set prv 'pr view --web'

# List my issues
gh alias set my 'issue list --assignee @me'
```

### Environment Variables

The skill respects standard gh CLI environment variables:

- `GH_TOKEN` - GitHub personal access token
- `GH_REPO` - Default repository (owner/repo format)
- `GH_HOST` - GitHub host (for GitHub Enterprise)

## Tips and Best Practices

### For Solo Developers
1. Use issues as your personal TODO list
2. Create PRs even for solo projects to track changes
3. Use draft PRs for work-in-progress
4. Release early and often
5. Automate repetitive tasks with scripts

### For Teams
1. Define clear code ownership with CODEOWNERS
2. Enforce branch protection on main branches
3. Use labels consistently
4. Regular issue triage
5. Track team velocity with milestones
6. Document decisions in issues/PRs

### General
1. Use `--json` output for scripting
2. Combine with git commands for powerful workflows
3. Enable shell completion for faster command entry
4. Use `--web` flag to open in browser when needed
5. Keep gh CLI updated for latest features

## Troubleshooting

### Authentication Issues
```bash
# Check authentication status
gh auth status

# Re-authenticate
gh auth login
```

### Permission Errors
- Verify you have appropriate access to the repository
- Check if the repository is private and you're authenticated with the correct account

### Command Not Found
- Ensure gh CLI is installed: `which gh`
- Verify gh is in your PATH

### Skill Not Loading
- Verify skill is in the correct directory
- Check SKILL.md has valid YAML frontmatter
- Restart Claude Code

## Contributing

Contributions are welcome! To contribute:

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub CLI Repository](https://github.com/cli/cli)
- [Claude Code Documentation](https://code.claude.com/docs)
- [Claude Agent Skills Guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills)

## License

This skill is provided as-is for use with Claude Code. See LICENSE file for details.

## Support

For issues or questions:
- GitHub CLI issues: [cli/cli issues](https://github.com/cli/cli/issues)
- Claude Code issues: [Anthropic support](https://support.anthropic.com)

## Version

Current version: 1.0.0

## Changelog

### 1.0.0 (Initial Release)
- Complete repository management
- Issue tracking and management
- Pull request workflows
- GitHub Actions integration
- Release management
- Team collaboration features
- Solo developer workflows
- Helper scripts
- Comprehensive documentation
