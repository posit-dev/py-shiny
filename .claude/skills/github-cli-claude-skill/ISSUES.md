# Issue Management

Comprehensive guide for managing GitHub issues using the gh CLI.

## Table of Contents
- [Viewing Issues](#viewing-issues)
- [Creating Issues](#creating-issues)
- [Updating Issues](#updating-issues)
- [Closing and Reopening Issues](#closing-and-reopening-issues)
- [Labels](#labels)
- [Milestones](#milestones)
- [Projects](#projects)
- [Search and Filtering](#search-and-filtering)
- [Common Workflows](#common-workflows)

## Viewing Issues

### List issues
```bash
# List open issues in current repository
gh issue list

# List all issues (open and closed)
gh issue list --state all

# Limit number of results
gh issue list --limit 50

# Filter by label
gh issue list --label bug
gh issue list --label "help wanted,good first issue"

# Filter by assignee
gh issue list --assignee @me
gh issue list --assignee username

# Filter by milestone
gh issue list --milestone "v1.0"

# Get JSON output
gh issue list --json number,title,state,labels,assignees
```

### View specific issue
```bash
# View issue details
gh issue view 123

# View in browser
gh issue view 123 --web

# View issue comments
gh issue view 123 --comments

# Get JSON output
gh issue view 123 --json number,title,body,state,labels,assignees,comments
```

### Search issues
```bash
# Search issues by keyword
gh issue list --search "error handling"

# Search with GitHub search syntax
gh issue list --search "is:open label:bug sort:created-desc"
gh issue list --search "is:closed author:username"
gh issue list --search "in:title performance"

# Search in specific repository
gh issue list -R owner/repo --search "memory leak"
```

## Creating Issues

### Interactive creation
```bash
# Create issue with interactive prompts
gh issue create

# Follow prompts for:
# - Title
# - Body
# - Metadata (labels, assignees, milestones)
```

### Non-interactive creation
```bash
# Create issue with title only
gh issue create --title "Fix login bug"

# Create issue with title and body
gh issue create --title "Add dark mode" --body "Users have requested dark mode support"

# Create issue with metadata
gh issue create \
  --title "Performance optimization" \
  --body "Optimize database queries" \
  --label bug,performance \
  --assignee username \
  --milestone "v2.0"

# Create issue from template
gh issue create --template bug_report.md

# Create issue in browser
gh issue create --web
```

### Create from file
```bash
# Create issue with body from file
gh issue create --title "Documentation update" --body-file docs/todo.md

# Create issue from markdown file (first heading as title)
cat << 'EOF' > issue.md
# Memory leak in user service

## Description
The user service is experiencing memory leaks after prolonged use.

## Steps to reproduce
1. Start the service
2. Create 1000 users
3. Monitor memory usage

## Expected behavior
Memory should remain stable

## Actual behavior
Memory grows continuously
EOF

gh issue create --body-file issue.md
```

## Updating Issues

### Edit issue
```bash
# Edit issue interactively
gh issue edit 123

# Update title
gh issue edit 123 --title "New title"

# Update body
gh issue edit 123 --body "Updated description"

# Update body from file
gh issue edit 123 --body-file updated.md

# Add labels
gh issue edit 123 --add-label bug,priority-high

# Remove labels
gh issue edit 123 --remove-label wontfix

# Add assignees
gh issue edit 123 --add-assignee user1,user2

# Remove assignees
gh issue edit 123 --remove-assignee user1

# Set milestone
gh issue edit 123 --milestone "v1.5"

# Remove milestone
gh issue edit 123 --milestone ""

# Add to project
gh issue edit 123 --add-project "Backend Tasks"

# Remove from project
gh issue edit 123 --remove-project "Backend Tasks"
```

### Comment on issue
```bash
# Add comment
gh issue comment 123 --body "Working on this now"

# Add comment from file
gh issue comment 123 --body-file comment.md

# Edit comment (requires comment ID)
gh api repos/:owner/:repo/issues/comments/COMMENT_ID -X PATCH -f body="Updated comment"
```

## Closing and Reopening Issues

### Close issues
```bash
# Close issue
gh issue close 123

# Close with comment
gh issue close 123 --comment "Fixed in PR #456"

# Close as completed
gh issue close 123 --reason completed

# Close as not planned
gh issue close 123 --reason "not planned"

# Close multiple issues
for issue in 123 124 125; do
  gh issue close $issue --comment "Bulk closing"
done
```

### Reopen issues
```bash
# Reopen issue
gh issue reopen 123

# Reopen with comment
gh issue reopen 123 --comment "Need to revisit this"
```

### Delete issues
```bash
# Delete issue (via API - CAREFUL)
gh api repos/:owner/:repo/issues/123 -X DELETE
```

## Labels

### List labels
```bash
# List labels in repository
gh label list

# Get JSON output
gh label list --json name,description,color
```

### Create labels
```bash
# Create label
gh label create bug --description "Something isn't working" --color d73a4a

# Create multiple labels
gh label create enhancement --description "New feature or request" --color a2eeef
gh label create documentation --description "Improvements to documentation" --color 0075ca
gh label create "good first issue" --description "Good for newcomers" --color 7057ff
```

### Edit labels
```bash
# Edit label
gh label edit bug --description "Bug report" --color ff0000

# Rename label
gh label edit old-name --name new-name
```

### Delete labels
```bash
# Delete label
gh label delete wontfix
```

### Manage issue labels
```bash
# Add labels to issue
gh issue edit 123 --add-label bug,priority-high

# Remove labels from issue
gh issue edit 123 --remove-label wontfix

# Replace all labels
gh api repos/:owner/:repo/issues/123 -X PATCH -f labels='["bug","confirmed"]'
```

## Milestones

### List milestones
```bash
# List milestones (via API)
gh api repos/:owner/:repo/milestones --jq '.[] | {number: .number, title: .title, due_on: .due_on}'
```

### Create milestone
```bash
# Create milestone
gh api repos/:owner/:repo/milestones -X POST \
  -f title="v1.0" \
  -f description="First major release" \
  -f due_on="2024-12-31T23:59:59Z"
```

### Update milestone
```bash
# Update milestone
gh api repos/:owner/:repo/milestones/1 -X PATCH \
  -f title="v1.0.0" \
  -f state="closed"
```

### Delete milestone
```bash
# Delete milestone
gh api repos/:owner/:repo/milestones/1 -X DELETE
```

## Projects

### List projects
```bash
# List projects (via API)
gh api repos/:owner/:repo/projects --jq '.[] | {name: .name, number: .number}'

# List organization projects
gh api orgs/:org/projects --jq '.[] | {name: .name, number: .number}'
```

### Add issue to project
```bash
# Add issue to project (requires project ID)
gh issue edit 123 --add-project "Project Name"
```

## Search and Filtering

### Advanced search examples
```bash
# Find stale issues
gh issue list --search "is:open updated:<2024-01-01"

# Find issues by author
gh issue list --search "author:username is:open"

# Find issues with no assignee
gh issue list --search "is:open no:assignee"

# Find issues with multiple labels
gh issue list --search "is:open label:bug label:critical"

# Find issues in title
gh issue list --search "in:title authentication"

# Find issues by comment count
gh issue list --search "is:open comments:>10"

# Find recently updated issues
gh issue list --search "is:open sort:updated-desc"

# Combine filters
gh issue list --search "is:open label:bug assignee:@me sort:created-asc"
```

### Filter with JSON output
```bash
# Get open bugs assigned to you
gh issue list --json number,title,labels,assignees \
  | jq '.[] | select(.assignees[].login == "username") | select(.labels[].name == "bug")'

# Count issues by label
gh issue list --state all --json labels --jq '
  [.[] | .labels[].name] | group_by(.) | map({label: .[0], count: length})
'

# Find issues updated in last 7 days
gh issue list --json number,title,updatedAt --jq '
  .[] | select(.updatedAt | fromdateiso8601 > (now - 604800))
'
```

## Common Workflows

### Workflow 1: Bug report workflow

```bash
# Create bug report
gh issue create \
  --title "Login fails with 2FA enabled" \
  --body "$(cat <<EOF
## Bug Description
Users cannot log in when 2FA is enabled.

## Steps to Reproduce
1. Enable 2FA on account
2. Attempt to log in
3. Authentication fails

## Expected Behavior
Login should succeed with 2FA code

## Actual Behavior
Login fails with error message

## Environment
- Browser: Chrome 119
- OS: macOS 14.0
EOF
)" \
  --label bug,priority-high \
  --assignee security-team

# Get issue number
ISSUE=$(gh issue list --label bug --limit 1 --json number --jq '.[0].number')

# Add follow-up comment
gh issue comment $ISSUE --body "Investigating root cause"

# Link to PR when fixed
gh issue comment $ISSUE --body "Fixed in PR #789"

# Close issue
gh issue close $ISSUE --comment "Resolved in v2.1.0"
```

### Workflow 2: Feature request workflow

```bash
# Create feature request
gh issue create \
  --title "Add export to PDF feature" \
  --body "Users want to export reports as PDF" \
  --label enhancement,feature-request

# Team discusses and assigns
gh issue edit 123 --add-assignee developer1 --milestone "v2.0"

# Track progress with comments
gh issue comment 123 --body "Starting implementation"
gh issue comment 123 --body "UI mockups ready for review"
gh issue comment 123 --body "Backend API complete"

# Link to PR
gh issue comment 123 --body "Implementation complete, see PR #456"

# Close when merged
gh issue close 123 --comment "Feature released in v2.0"
```

### Workflow 3: Issue triage workflow

```bash
# List untriaged issues (no labels)
gh issue list --json number,title,labels \
  | jq '.[] | select(.labels | length == 0) | {number: .number, title: .title}'

# Triage each issue
gh issue edit 123 --add-label bug
gh issue edit 124 --add-label enhancement
gh issue edit 125 --add-label question,help-wanted

# Assign priority labels
gh issue edit 123 --add-label priority-high
gh issue edit 124 --add-label priority-medium

# Assign to milestones
gh issue edit 123 --milestone "v1.5"
gh issue edit 124 --milestone "v2.0"

# Assign to team members
gh issue edit 123 --add-assignee developer1
```

### Workflow 4: Sprint planning workflow

```bash
# List issues in milestone
gh issue list --milestone "Sprint 5" --json number,title,assignees

# Assign issues to team members
gh issue edit 101 --add-assignee alice
gh issue edit 102 --add-assignee bob
gh issue edit 103 --add-assignee charlie

# Add sprint label
for issue in 101 102 103; do
  gh issue edit $issue --add-label "sprint-5"
done

# Monitor progress during sprint
gh issue list --milestone "Sprint 5" --state all --json number,title,state

# Close completed issues
gh issue list --milestone "Sprint 5" --search "is:open label:done" \
  | jq -r '.[].number' \
  | xargs -I {} gh issue close {}
```

### Workflow 5: Bulk issue operations

```bash
# Create multiple issues from file
while IFS='|' read -r title body labels; do
  gh issue create --title "$title" --body "$body" --label "$labels"
done < issues.txt

# Bulk close stale issues
gh issue list --search "is:open updated:<2023-01-01" --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue close {} --comment "Closing due to inactivity"

# Bulk label update
gh issue list --label old-label --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue edit {} --remove-label old-label --add-label new-label

# Export issues to CSV
gh issue list --state all --json number,title,state,labels,assignees,createdAt --limit 1000 \
  | jq -r '.[] | [.number, .title, .state, (.labels | map(.name) | join(";")), (.assignees | map(.login) | join(";")), .createdAt] | @csv' \
  > issues.csv
```

## Advanced Techniques

### Using templates

```bash
# List issue templates
ls -la .github/ISSUE_TEMPLATE/

# Create issue from template
gh issue create --template bug_report.yml

# Create custom template
mkdir -p .github/ISSUE_TEMPLATE
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: Report a bug
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear description of what the bug is.

**Steps to reproduce**
1.
2.
3.

**Expected behavior**
What should happen.

**Actual behavior**
What actually happens.
EOF
```

### Issue forms (YAML)

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: File a bug report
title: "[Bug]: "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  - type: input
    id: contact
    attributes:
      label: Contact Details
      description: How can we get in touch with you if we need more info?
      placeholder: ex. email@example.com
    validations:
      required: false
  - type: textarea
    id: what-happened
    attributes:
      label: What happened?
      description: Also tell us, what did you expect to happen?
      placeholder: Tell us what you see!
    validations:
      required: true
```

### Automation with GitHub Actions

```yaml
# .github/workflows/issue-labeler.yml
name: Label Issues
on:
  issues:
    types: [opened]
jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - name: Label bug reports
        if: contains(github.event.issue.title, '[BUG]')
        run: gh issue edit ${{ github.event.issue.number }} --add-label bug
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Tips and Best Practices

1. **Use templates**: Create issue templates for consistency
2. **Label systematically**: Develop a consistent labeling scheme
3. **Triage regularly**: Review and label new issues promptly
4. **Link PRs**: Always reference issues in PR descriptions
5. **Close properly**: Use "Closes #123" in PR descriptions for auto-closing
6. **Use milestones**: Group related issues for release planning
7. **Assign clearly**: Assign issues to specific people
8. **Comment updates**: Keep stakeholders informed with comments
9. **Search effectively**: Use GitHub search syntax for complex queries
10. **Export data**: Use JSON output for reporting and analysis

## Quick Reference

```bash
# List
gh issue list                                  # List open issues
gh issue list --state all                      # List all issues
gh issue list --label bug                      # Filter by label
gh issue list --assignee @me                   # Your issues

# View
gh issue view 123                              # View issue details
gh issue view 123 --web                        # Open in browser
gh issue view 123 --comments                   # Include comments

# Create
gh issue create                                # Interactive creation
gh issue create --title "text" --body "text"   # Non-interactive
gh issue create --label bug --assignee user    # With metadata

# Update
gh issue edit 123 --title "new title"          # Change title
gh issue edit 123 --add-label bug              # Add label
gh issue edit 123 --add-assignee user          # Add assignee

# Comment
gh issue comment 123 --body "comment text"     # Add comment

# Close/Reopen
gh issue close 123                             # Close issue
gh issue close 123 --reason completed          # Close with reason
gh issue reopen 123                            # Reopen issue

# Search
gh issue list --search "query"                 # Search issues
gh issue list --search "is:open label:bug"     # Complex search

# Labels
gh label list                                  # List labels
gh label create name --color hex               # Create label
gh label edit name --name new-name             # Edit label
```
