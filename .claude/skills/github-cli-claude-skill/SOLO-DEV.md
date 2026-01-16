# Solo Developer Workflows

Optimized workflows and patterns for solo developers using the gh CLI.

## Table of Contents
- [Quick Start for Solo Projects](#quick-start-for-solo-projects)
- [Efficient Issue Management](#efficient-issue-management)
- [Fast PR Workflows](#fast-pr-workflows)
- [Personal Project Organization](#personal-project-organization)
- [Solo Release Management](#solo-release-management)
- [Automation for One](#automation-for-one)
- [Common Solo Workflows](#common-solo-workflows)

## Quick Start for Solo Projects

### Initialize new project

```bash
# 1. Create repository
gh repo create my-project \
  --public \
  --add-readme \
  --gitignore Node \
  --license MIT \
  --clone

cd my-project

# 2. Set up basic structure
mkdir -p src tests docs
echo "console.log('Hello, world!');" > src/index.js

# 3. Initial commit
git add .
git commit -m "feat: initial project setup"
git push

# 4. Enable GitHub Actions
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm test
EOF

git add .github/workflows/ci.yml
git commit -m "ci: add CI workflow"
git push

# 5. Create first issue for next task
gh issue create \
  --title "Add configuration system" \
  --body "Implement configuration loading from env vars and config file" \
  --label enhancement
```

### Quick project setup template

```bash
#!/bin/bash
# quick-project.sh - Quick project initialization

PROJECT_NAME="$1"
if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project-name>"
  exit 1
fi

# Create repo and clone
gh repo create "$PROJECT_NAME" --public --add-readme --clone
cd "$PROJECT_NAME"

# Basic structure
mkdir -p src tests docs .github/workflows

# Basic CI
cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: echo "Tests will go here"
EOF

# Commit setup
git add .
git commit -m "chore: initial project structure"
git push

echo "✅ Project $PROJECT_NAME created and initialized!"
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  # Start coding!"
```

## Efficient Issue Management

### Using issues as your personal TODO list

```bash
# Create issue from command line quickly
gh issue create --title "Fix: Handle null values in parser" --label bug

# Create multiple related issues quickly
for task in "Add tests" "Update docs" "Add error handling"; do
  gh issue create --title "$task" --label todo --assignee @me
done

# View your TODO list
gh issue list --assignee @me

# Quick check-in on progress
gh issue list --assignee @me --json number,title,state \
  | jq -r '.[] | "\(.state | ascii_upcase) #\(.number): \(.title)"'

# Close issue when done
gh issue close 123 --comment "Completed"

# Or close with commit message
git commit -m "fix: handle null values in parser

Closes #123"
```

### Issue templates for personal projects

```bash
# Create simple issue templates
mkdir -p .github/ISSUE_TEMPLATE

cat > .github/ISSUE_TEMPLATE/feature.md << 'EOF'
---
name: Feature
about: New feature to implement
title: ''
labels: enhancement
assignees: ''
---

## What
Brief description

## Why
Reason for adding this

## How
Implementation approach
EOF

cat > .github/ISSUE_TEMPLATE/bug.md << 'EOF'
---
name: Bug
about: Something isn't working
title: ''
labels: bug
assignees: ''
---

## Bug Description
What's broken

## Steps to Reproduce
1.
2.
3.

## Expected vs Actual
- Expected:
- Actual:
EOF
```

### Quick issue tracking

```bash
# Today's focus - issues I'm working on
gh issue list --assignee @me --label "in-progress"

# This week's completed issues
gh issue list --assignee @me --search "is:closed closed:>=$(date -d '7 days ago' +%Y-%m-%d)"

# Backlog - future work
gh issue list --assignee @me --label "backlog" --json number,title \
  | jq -r '.[] | "- [ ] #\(.number): \(.title)"'
```

## Fast PR Workflows

### Quick PR for solo projects

```bash
# Method 1: Direct to main (for solo projects without sensitive data)
git checkout -b feature/quick-feature
# ... make changes ...
git add .
git commit -m "feat: add quick feature"
git push -u origin feature/quick-feature
gh pr create --fill
gh pr merge --squash --delete-branch --auto

# Method 2: Review your own work
git checkout -b feature/needs-review
# ... make changes ...
git push -u origin feature/needs-review
gh pr create --fill --draft

# Come back later, review in browser
gh pr ready <pr-number>
gh pr merge <pr-number> --squash --delete-branch
```

### Using PR as checkpoint

```bash
# Create draft PR to save work-in-progress
git checkout -b wip/big-refactor
# ... start working ...
git add .
git commit -m "wip: refactoring data layer"
git push -u origin wip/big-refactor

gh pr create --draft \
  --title "WIP: Refactor data layer" \
  --body "Tracking progress on data layer refactoring. Not ready for merge."

# Continue working, push updates
# ... more work ...
git push

# When ready, mark as ready and merge
gh pr ready <pr-number>
gh pr merge <pr-number> --squash --delete-branch
```

### Skip PR for tiny changes

```bash
# For truly trivial changes (typos, comments, etc.)
# Just commit directly to main

git checkout main
git pull
# ... fix typo ...
git add .
git commit -m "docs: fix typo in README"
git push

# Reserve PRs for actual features/fixes that benefit from:
# - CI validation
# - Historical checkpoint
# - Detailed description
```

## Personal Project Organization

### Label system for solo projects

```bash
# Simple label scheme
gh label create "in-progress" --color "0e8a16" --description "Currently working on"
gh label create "backlog" --color "d4c5f9" --description "Future work"
gh label create "bug" --color "d73a4a" --description "Something broken"
gh label create "enhancement" --color "a2eeef" --description "New feature"
gh label create "docs" --color "0075ca" --description "Documentation"
gh label create "quick-win" --color "7057ff" --description "Easy task, quick to complete"

# Use labels for workflow
gh issue create --title "Task" --label "quick-win"  # Easy task
gh issue edit 123 --add-label "in-progress"         # Start working
gh issue close 123                                   # Complete
```

### Milestone for version planning

```bash
# Create milestone for next version
gh api repos/:owner/:repo/milestones -X POST \
  -f title="v1.1" \
  -f description="Next minor release" \
  -f due_on="2024-12-31T23:59:59Z"

# Assign issues to milestone
gh issue edit 101 --milestone "v1.1"
gh issue edit 102 --milestone "v1.1"

# Check progress
gh issue list --milestone "v1.1"

# When done, create release
gh release create v1.1.0 --generate-notes
```

### Project boards (optional)

```bash
# For visual project management
# Create project via web UI, then:

# Add issues to project
gh issue edit 123 --add-project "My Project"

# View project
gh project list
gh project view <project-number> --web
```

## Solo Release Management

### Semantic versioning workflow

```bash
# Patch release (bug fixes)
VERSION="v1.0.1"
git tag -a $VERSION -m "Bug fixes"
git push origin $VERSION
gh release create $VERSION --generate-notes

# Minor release (new features)
VERSION="v1.1.0"
git tag -a $VERSION -m "New features"
git push origin $VERSION
gh release create $VERSION --generate-notes --title "Version 1.1.0"

# Major release (breaking changes)
VERSION="v2.0.0"
git tag -a $VERSION -m "Major release"
git push origin $VERSION
gh release create $VERSION --generate-notes --title "Version 2.0.0 - Breaking Changes"
```

### Quick release script

```bash
#!/bin/bash
# quick-release.sh - Fast release for solo projects

VERSION="$1"
if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  echo "Example: $0 v1.2.0"
  exit 1
fi

echo "Creating release $VERSION..."

# Update version in code (customize for your project)
# sed -i "s/VERSION = .*/VERSION = \"${VERSION#v}\"/" version.py

# Run tests
if ! make test; then
  echo "❌ Tests failed! Fix tests before releasing."
  exit 1
fi

# Build if needed
# make build

# Create tag
git tag -a "$VERSION" -m "Release $VERSION"
git push origin "$VERSION"

# Create GitHub release
gh release create "$VERSION" \
  --generate-notes \
  --title "Release $VERSION"

echo "✅ Release $VERSION created!"
gh release view "$VERSION" --web
```

### Changelog management

```bash
# Manual changelog (simple)
cat > update-changelog.sh << 'EOF'
#!/bin/bash
VERSION="$1"

cat >> CHANGELOG.md << END

## [$VERSION] - $(date +%Y-%m-%d)

### Added
- New feature X

### Changed
- Updated behavior Y

### Fixed
- Bug Z

END

echo "Updated CHANGELOG.md for $VERSION"
EOF

# Or auto-generate from commits
git log --oneline --no-merges v1.0.0..HEAD | \
  grep -E "(feat|fix):" | \
  sed 's/^[a-f0-9]* /- /' > recent-changes.txt
```

## Automation for One

### Daily workflow automation

```bash
#!/bin/bash
# morning-routine.sh - Start your dev day

echo "🌅 Good morning! Here's your dev status:"
echo ""

# Repo status
cd ~/projects/my-project
echo "📁 Repository: $(basename $(pwd))"
git fetch
if [ -n "$(git status -s)" ]; then
  echo "⚠️  Uncommitted changes:"
  git status -s
fi
echo ""

# Today's issues
echo "📋 Your issues:"
gh issue list --assignee @me --limit 5
echo ""

# CI status
echo "🔄 Recent CI runs:"
gh run list --limit 3 --json conclusion,workflowName,createdAt \
  | jq -r '.[] | "  \(.conclusion | ascii_upcase): \(.workflowName) (\(.createdAt | split("T")[0]))"'
echo ""

# Open PRs
PR_COUNT=$(gh pr list --json number | jq 'length')
if [ "$PR_COUNT" -gt 0 ]; then
  echo "🔀 Open PRs: $PR_COUNT"
  gh pr list
fi
```

### Weekly summary automation

```bash
#!/bin/bash
# weekly-summary.sh - Your weekly dev summary

echo "# Weekly Dev Summary"
echo "Week ending: $(date +%Y-%m-%d)"
echo ""

# Commits this week
echo "## Commits This Week"
git log --oneline --since='7 days ago' --author="$(git config user.email)"
echo ""

# Issues closed
echo "## Issues Closed"
gh issue list --search "is:closed closed:>=$(date -d '7 days ago' +%Y-%m-%d)" \
  --json number,title --jq '.[] | "- #\(.number): \(.title)"'
echo ""

# PRs merged
echo "## PRs Merged"
gh pr list --search "is:merged merged:>=$(date -d '7 days ago' +%Y-%m-%d)" \
  --json number,title --jq '.[] | "- #\(.number): \(.title)"'
echo ""

# Releases
RELEASES=$(gh release list --limit 5 --json tagName,publishedAt \
  | jq -r ".[] | select(.publishedAt > \"$(date -d '7 days ago' --iso-8601)T00:00:00Z\") | \"- \(.tagName)\"")
if [ -n "$RELEASES" ]; then
  echo "## Releases"
  echo "$RELEASES"
fi
```

### Backup and sync

```bash
#!/bin/bash
# backup-repos.sh - Backup all your repos

BACKUP_DIR="$HOME/backups/github/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# List your repos
gh repo list --json name,url --limit 100 | jq -r '.[] | .url' | while read url; do
  repo_name=$(basename "$url" .git)
  echo "Backing up $repo_name..."

  if [ -d "$BACKUP_DIR/$repo_name" ]; then
    cd "$BACKUP_DIR/$repo_name" && git pull
  else
    git clone --mirror "$url" "$BACKUP_DIR/$repo_name"
  fi
done

echo "✅ Backup complete: $BACKUP_DIR"
```

## Common Solo Workflows

### Workflow 1: Feature development cycle

```bash
# 1. Create issue for tracking
gh issue create \
  --title "Add user profile page" \
  --body "Users should be able to view and edit their profile" \
  --label enhancement \
  --assignee @me

ISSUE=$(gh issue list --limit 1 --json number --jq '.[0].number')

# 2. Create feature branch
git checkout -b "feature/user-profile-$ISSUE"

# 3. Work on feature
# ... make changes ...

# 4. Commit with issue reference
git add .
git commit -m "feat: add user profile page

- Added profile view
- Added profile edit form
- Added validation

Related to #$ISSUE"

# 5. Push and create PR
git push -u origin "feature/user-profile-$ISSUE"
gh pr create --fill --web

# 6. Wait for CI, then merge
gh pr checks --watch
gh pr merge --squash --delete-branch

# 7. Issue auto-closes via PR reference
# Or manually close
gh issue close $ISSUE --comment "Implemented in latest merge"
```

### Workflow 2: Bug fix workflow

```bash
# 1. Create bug report
gh issue create \
  --title "Fix: Form validation not working" \
  --body "Form allows invalid email addresses" \
  --label bug

BUG=$(gh issue list --limit 1 --json number --jq '.[0].number')

# 2. Quick branch and fix
git checkout -b "fix/form-validation-$BUG"
# ... fix bug ...
git add .
git commit -m "fix: form validation for email addresses

Fixes #$BUG"

# 3. Push and merge quickly
git push -u origin "fix/form-validation-$BUG"
gh pr create --fill
gh pr merge --auto --squash --delete-branch

# Issue auto-closes via "Fixes #BUG" in commit message
```

### Workflow 3: Experimentation workflow

```bash
# 1. Create experiment branch
git checkout -b experiment/try-new-architecture

# 2. Create draft PR for tracking
gh pr create --draft \
  --title "Experiment: New architecture" \
  --body "Trying out new architecture. May not merge."

# 3. Work on experiment
# ... experiment ...
git add .
git commit -m "experiment: try new architecture"
git push

# 4a. If successful, convert to real PR
gh pr ready <pr-number>
gh pr edit <pr-number> --title "feat: Implement new architecture"
gh pr merge <pr-number> --squash

# 4b. If unsuccessful, close PR and delete branch
gh pr close <pr-number>
git checkout main
git branch -D experiment/try-new-architecture
git push origin --delete experiment/try-new-architecture
```

### Workflow 4: Documentation workflow

```bash
# Keep docs in sync with code changes
git checkout -b docs/update-api-docs

# Update docs
# ... edit docs ...

# Use conventional commit
git add docs/
git commit -m "docs: update API documentation for v2 endpoints"

# Quick merge - docs don't need extensive review for solo projects
git push -u origin docs/update-api-docs
gh pr create --fill
gh pr merge --auto --squash --delete-branch

# Or skip PR for doc-only changes
git checkout main
git pull
# ... edit docs ...
git add docs/
git commit -m "docs: fix typo in README"
git push
```

### Workflow 5: Maintenance workflow

```bash
#!/bin/bash
# monthly-maintenance.sh - Monthly repo maintenance

echo "🧹 Monthly Maintenance"
echo ""

# Close stale issues
echo "Closing stale issues..."
gh issue list --search "is:open updated:<$(date -d '90 days ago' +%Y-%m-%d)" --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue close {} --comment "Closing due to inactivity. Reopen if still relevant."

# Delete old branches
echo "Cleaning up merged branches..."
git fetch --prune
git branch --merged main | grep -v "^* main$" | xargs -r git branch -d

# Delete old workflow runs
echo "Cleaning up old workflow runs..."
gh run list --status completed --limit 100 --json databaseId,createdAt \
  | jq --arg date "$(date -u -d '30 days ago' +%Y-%m-%d)" \
    '.[] | select(.createdAt < $date) | .databaseId' \
  | xargs -I {} gh run delete {} --confirm

# Update dependencies (if using npm)
if [ -f "package.json" ]; then
  echo "Checking for dependency updates..."
  npm outdated
fi

echo ""
echo "✅ Maintenance complete!"
```

## Tips and Best Practices

1. **Keep it simple**: Don't over-engineer workflows for solo projects
2. **Use issues as TODO**: Personal task tracking with GitHub issues
3. **PR for checkpoints**: Use PRs for historical tracking, not just review
4. **Direct commits for tiny changes**: Skip PR process for trivial fixes
5. **Automate repetition**: Script common workflows
6. **Regular releases**: Release early and often
7. **Self-review**: Review your own PRs after a break
8. **Use drafts**: Draft PRs for work-in-progress tracking
9. **Label for context**: Quick labels for task type/status
10. **Backup regularly**: Keep local backups of important projects
11. **Document decisions**: Use issues/PRs to document "why"
12. **Celebrate wins**: Track completed issues to see progress

## Quick Reference

```bash
# Fast project init
gh repo create my-project --public --clone
cd my-project && gh issue create --title "First task"

# Issue as TODO
gh issue create --title "Task" --assignee @me
gh issue list --assignee @me
gh issue close 123

# Quick PR
git push -u origin feature
gh pr create --fill
gh pr merge --auto --squash --delete-branch

# Fast release
git tag v1.0.0 && git push origin v1.0.0
gh release create v1.0.0 --generate-notes

# Daily status
gh issue list --assignee @me
gh pr list
gh run list --limit 3

# Weekly summary
gh issue list --search "is:closed closed:>=7.days.ago"
gh pr list --search "is:merged merged:>=7.days.ago"

# Cleanup
gh issue list --search "is:open updated:<90.days.ago"
git branch --merged | xargs git branch -d
```
