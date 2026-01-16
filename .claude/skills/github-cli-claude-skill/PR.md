# Pull Request Workflows

Comprehensive guide for managing GitHub pull requests using the gh CLI.

## Table of Contents
- [Viewing Pull Requests](#viewing-pull-requests)
- [Creating Pull Requests](#creating-pull-requests)
- [Reviewing Pull Requests](#reviewing-pull-requests)
- [Updating Pull Requests](#updating-pull-requests)
- [Merging Pull Requests](#merging-pull-requests)
- [Working with PR Locally](#working-with-pr-locally)
- [PR Checks and Status](#pr-checks-and-status)
- [Common Workflows](#common-workflows)

## Viewing Pull Requests

### List pull requests
```bash
# List open pull requests
gh pr list

# List all pull requests
gh pr list --state all

# Filter by author
gh pr list --author username
gh pr list --author @me

# Filter by label
gh pr list --label bug
gh pr list --label "needs review,priority-high"

# Filter by assignee
gh pr list --assignee @me

# Filter by base branch
gh pr list --base main
gh pr list --base develop

# Filter by head branch
gh pr list --head feature/new-feature

# Search pull requests
gh pr list --search "is:open review:required"
gh pr list --search "is:merged author:username"

# Limit results
gh pr list --limit 50

# Get JSON output
gh pr list --json number,title,state,headRefName,baseRefName,author
```

### View specific pull request
```bash
# View PR details
gh pr view 123

# View in browser
gh pr view 123 --web

# View PR comments
gh pr view 123 --comments

# View PR diff
gh pr diff 123

# Get JSON output
gh pr view 123 --json number,title,body,state,mergeable,reviews,checks
```

### Check PR status
```bash
# View PR checks
gh pr checks 123

# Wait for checks to complete
gh pr checks 123 --watch

# View specific check logs
gh run view <run-id> --log

# Get checks as JSON
gh pr view 123 --json statusCheckRollup
```

## Creating Pull Requests

### Interactive creation
```bash
# Create PR interactively
gh pr create

# Follow prompts for:
# - Title
# - Body
# - Base branch
# - Reviewers
# - Labels
# - Projects
```

### Non-interactive creation
```bash
# Create PR with current branch
gh pr create --title "Add new feature" --body "Description of changes"

# Create PR with auto-filled title and body from commits
gh pr create --fill

# Create PR with auto-filled title only
gh pr create --fill-first

# Create PR to specific base branch
gh pr create --base develop --fill

# Create PR with reviewers
gh pr create --fill --reviewer user1,user2
gh pr create --fill --reviewer team-name

# Create PR with labels
gh pr create --fill --label bug,priority-high

# Create PR with assignees
gh pr create --fill --assignee @me

# Create PR with milestone
gh pr create --fill --milestone "v2.0"

# Create PR in draft mode
gh pr create --fill --draft

# Create PR from specific branch
git checkout feature/branch
gh pr create --fill
```

### Create from template
```bash
# Create PR with body from file
gh pr create --title "Fix bug" --body-file pr-template.md

# Use template file
cat > pr-template.md << 'EOF'
## What
Brief description of changes

## Why
Reasoning for changes

## How
Technical approach

## Testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] Manual testing complete

Closes #123
EOF

gh pr create --body-file pr-template.md --fill-first
```

### Create PR in browser
```bash
# Open PR creation in browser
gh pr create --web
```

## Reviewing Pull Requests

### Request reviews
```bash
# Request review from users
gh pr edit 123 --add-reviewer user1,user2

# Request review from team
gh pr edit 123 --add-reviewer org/team-name

# Remove reviewer
gh pr edit 123 --remove-reviewer user1
```

### Submit reviews
```bash
# Approve PR
gh pr review 123 --approve

# Approve with comment
gh pr review 123 --approve --body "LGTM! Great work."

# Request changes
gh pr review 123 --request-changes --body "Please address the following issues..."

# Comment without approval
gh pr review 123 --comment --body "Some thoughts on this approach..."

# Review with body from file
gh pr review 123 --approve --body-file review.md
```

### Add review comments
```bash
# Add inline comments (requires checking out PR first)
gh pr checkout 123
# Make edits or add comments in review interface

# Add comment to PR conversation
gh pr comment 123 --body "Please update the documentation"

# Add comment from file
gh pr comment 123 --body-file comment.md
```

### View reviews
```bash
# View reviews on PR
gh pr view 123 --json reviews

# List reviews
gh api repos/:owner/:repo/pulls/123/reviews --jq '.[] | {user: .user.login, state: .state, body: .body}'

# View specific review
gh api repos/:owner/:repo/pulls/123/reviews/REVIEW_ID
```

## Updating Pull Requests

### Edit PR metadata
```bash
# Edit PR interactively
gh pr edit 123

# Update title
gh pr edit 123 --title "New title"

# Update body
gh pr edit 123 --body "Updated description"

# Update body from file
gh pr edit 123 --body-file updated.md

# Add labels
gh pr edit 123 --add-label bug,priority-high

# Remove labels
gh pr edit 123 --remove-label wontfix

# Add assignees
gh pr edit 123 --add-assignee user1,user2

# Remove assignees
gh pr edit 123 --remove-assignee user1

# Change base branch
gh pr edit 123 --base develop

# Add to milestone
gh pr edit 123 --milestone "v1.5"

# Remove from milestone
gh pr edit 123 --milestone ""

# Add to project
gh pr edit 123 --add-project "Backend"

# Remove from project
gh pr edit 123 --remove-project "Backend"
```

### Convert draft to ready
```bash
# Mark PR as ready for review
gh pr ready 123
```

### Convert to draft
```bash
# Convert PR to draft
gh pr edit 123 --draft
```

### Update PR branch
```bash
# Update PR branch with latest from base
gh pr checkout 123
git merge origin/main
git push

# Or use rebase
gh pr checkout 123
git rebase origin/main
git push --force-with-lease
```

## Merging Pull Requests

### Merge strategies
```bash
# Merge PR (default: merge commit)
gh pr merge 123

# Squash and merge
gh pr merge 123 --squash

# Rebase and merge
gh pr merge 123 --rebase

# Merge with auto-delete branch
gh pr merge 123 --delete-branch

# Merge with auto-rebase
gh pr merge 123 --auto --rebase
```

### Merge with options
```bash
# Merge when checks pass
gh pr merge 123 --auto

# Merge with custom commit message
gh pr merge 123 --squash --subject "feat: add new feature" --body "Detailed description"

# Merge using admin privileges
gh pr merge 123 --admin

# Merge and delete branch
gh pr merge 123 --delete-branch --squash
```

### Disable auto-merge
```bash
# Disable auto-merge
gh pr merge 123 --disable-auto
```

## Working with PR Locally

### Checkout PR
```bash
# Checkout PR branch
gh pr checkout 123

# Checkout PR from fork
gh pr checkout 123 --force

# Checkout by branch name
gh pr checkout feature/branch-name
```

### Update local PR branch
```bash
# Fetch latest changes
gh pr checkout 123
git pull

# Sync with base branch
git fetch origin
git merge origin/main
```

### Push changes to PR
```bash
# Make changes
git add .
git commit -m "Address review comments"
git push
```

### Create PR from current branch
```bash
# Push branch and create PR
git push -u origin feature/branch
gh pr create --fill
```

## PR Checks and Status

### View checks
```bash
# View all checks
gh pr checks 123

# Watch checks in real-time
gh pr checks 123 --watch

# View specific check
gh pr checks 123 --check "CI / test"

# Get required checks
gh api repos/:owner/:repo/branches/main/protection/required_status_checks
```

### Re-run checks
```bash
# Re-run failed checks (via workflow)
gh run list --branch feature/branch --limit 1 --json databaseId --jq '.[0].databaseId' \
  | xargs -I {} gh run rerun {}

# Re-run specific check
gh run rerun <run-id>

# Re-run only failed jobs
gh run rerun <run-id> --failed
```

### View CI logs
```bash
# View workflow run logs
gh run view <run-id> --log

# View specific job logs
gh run view <run-id> --job <job-id> --log

# Download logs
gh run download <run-id>
```

## Common Workflows

### Workflow 1: Feature development PR

```bash
# Create feature branch
git checkout -b feature/new-feature main

# Make changes
echo "new feature code" > feature.js
git add feature.js
git commit -m "Add new feature"

# Push and create PR
git push -u origin feature/new-feature
gh pr create --fill --reviewer team-name --label enhancement

# Get PR number
PR=$(gh pr list --head feature/new-feature --json number --jq '.[0].number')

# Address review comments
git add .
git commit -m "Address review feedback"
git push

# Merge when approved
gh pr merge $PR --squash --delete-branch
```

### Workflow 2: Bug fix PR

```bash
# Create bug fix branch
git checkout -b fix/bug-description main

# Make fix
# ... edit files ...
git add .
git commit -m "Fix: description of bug fix"
git push -u origin fix/bug-description

# Create PR that closes issue
gh pr create \
  --title "Fix: description of bug fix" \
  --body "Fixes #456$(printf '\n\n')## Changes$(printf '\n')- Fixed bug by..." \
  --label bug \
  --reviewer maintainer

# Wait for CI
PR=$(gh pr list --head fix/bug-description --json number --jq '.[0].number')
gh pr checks $PR --watch

# Merge when green
gh pr merge $PR --squash --delete-branch
```

### Workflow 3: Review workflow

```bash
# List PRs needing review
gh pr list --search "is:open review-requested:@me"

# Check out PR to test locally
gh pr checkout 123

# Run tests locally
npm test

# Review and approve
gh pr review 123 --approve --body "Tested locally, works great!"

# Or request changes
gh pr review 123 --request-changes --body "Please add error handling for edge case"

# After changes, approve
gh pr review 123 --approve --body "Changes look good!"
```

### Workflow 4: Update PR with base branch

```bash
# Checkout PR
gh pr checkout 123

# Update with latest main
git fetch origin
git merge origin/main

# Resolve conflicts if any
# ... fix conflicts ...
git add .
git commit -m "Merge main into feature branch"

# Push updates
git push

# Or use rebase for cleaner history
git fetch origin
git rebase origin/main
git push --force-with-lease
```

### Workflow 5: Draft PR for early feedback

```bash
# Create draft PR
git checkout -b wip/feature main
# ... make initial changes ...
git add .
git commit -m "WIP: Initial implementation"
git push -u origin wip/feature

gh pr create --draft --fill --body "Early draft for feedback on approach"

# Continue development
# ... more commits ...
git push

# Mark ready when done
PR=$(gh pr list --head wip/feature --json number --jq '.[0].number')
gh pr ready $PR
gh pr edit $PR --add-reviewer team-name
```

### Workflow 6: Batch PR operations

```bash
# List all open PRs by author
gh pr list --author @me --json number,title

# Approve multiple PRs
for pr in 101 102 103; do
  gh pr review $pr --approve --body "LGTM"
done

# Update labels on multiple PRs
gh pr list --label old-label --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh pr edit {} --remove-label old-label --add-label new-label

# Close stale PRs
gh pr list --search "is:open updated:<2023-01-01" --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh pr close {} --comment "Closing due to inactivity"
```

## Advanced Techniques

### Auto-merge configuration
```bash
# Enable auto-merge when checks pass
gh pr merge 123 --auto --squash

# Check auto-merge status
gh pr view 123 --json autoMergeRequest

# Disable auto-merge
gh pr merge 123 --disable-auto
```

### PR templates
```bash
# Create PR template
mkdir -p .github
cat > .github/pull_request_template.md << 'EOF'
## Description
Brief description of changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Dependent changes merged

## Related Issues
Closes #
EOF

# Template will be used automatically for new PRs
gh pr create --web
```

### Multiple PR templates
```bash
# Create template directory
mkdir -p .github/PULL_REQUEST_TEMPLATE

# Create feature template
cat > .github/PULL_REQUEST_TEMPLATE/feature.md << 'EOF'
## Feature Description
...
EOF

# Create bugfix template
cat > .github/PULL_REQUEST_TEMPLATE/bugfix.md << 'EOF'
## Bug Description
...
EOF

# Use specific template
gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/feature.md
```

### Link PRs to issues
```bash
# Link PR to issue (auto-close on merge)
gh pr create --fill --body "Closes #123"

# Link multiple issues
gh pr create --fill --body "Closes #123, closes #124, fixes #125"

# Link without auto-closing
gh pr create --fill --body "Related to #123"
gh pr create --fill --body "Part of #123"
```

### PR diff filtering
```bash
# View diff for specific files
gh pr diff 123 -- path/to/file.js

# View diff with context
gh pr diff 123 --patch

# View diff in external tool
gh pr diff 123 | code -
```

### Export PR data
```bash
# Export PRs to CSV
gh pr list --state all --json number,title,state,author,createdAt,mergedAt --limit 1000 \
  | jq -r '.[] | [.number, .title, .state, .author.login, .createdAt, .mergedAt] | @csv' \
  > prs.csv

# Generate PR report
gh pr list --search "is:merged merged:>2024-01-01" --json number,title,author \
  | jq -r '.[] | "PR #\(.number): \(.title) by @\(.author.login)"'
```

## Tips and Best Practices

1. **Use --fill flag**: Auto-populate title and body from commits
2. **Draft PRs**: Use for work-in-progress to get early feedback
3. **Link issues**: Always reference related issues in PR description
4. **Small PRs**: Keep PRs focused and reviewable
5. **Clear titles**: Use descriptive, concise titles
6. **Good descriptions**: Explain what, why, and how
7. **Request reviews**: Explicitly request reviews from appropriate people
8. **Respond to feedback**: Address all review comments promptly
9. **Keep updated**: Sync with base branch regularly
10. **Clean history**: Use squash or rebase for clean commit history
11. **CI/CD**: Ensure all checks pass before requesting review
12. **Delete branches**: Clean up after merge

## Quick Reference

```bash
# List
gh pr list                                     # List open PRs
gh pr list --author @me                        # Your PRs
gh pr list --search "query"                    # Search PRs

# View
gh pr view 123                                 # View PR details
gh pr view 123 --web                           # Open in browser
gh pr diff 123                                 # View diff
gh pr checks 123                               # View checks

# Create
gh pr create                                   # Interactive creation
gh pr create --fill                            # Auto-fill from commits
gh pr create --draft                           # Create as draft

# Review
gh pr review 123 --approve                     # Approve PR
gh pr review 123 --request-changes             # Request changes
gh pr review 123 --comment                     # Comment only
gh pr comment 123 --body "text"                # Add comment

# Update
gh pr edit 123 --title "new title"             # Change title
gh pr edit 123 --add-reviewer user             # Add reviewer
gh pr edit 123 --add-label label               # Add label
gh pr ready 123                                # Mark ready for review

# Merge
gh pr merge 123                                # Merge PR
gh pr merge 123 --squash                       # Squash and merge
gh pr merge 123 --rebase                       # Rebase and merge
gh pr merge 123 --auto                         # Auto-merge when ready

# Local
gh pr checkout 123                             # Checkout PR locally
gh pr checkout 123 && git pull                 # Update local PR branch

# Close
gh pr close 123                                # Close PR
gh pr reopen 123                               # Reopen PR
```
