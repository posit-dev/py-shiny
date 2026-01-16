# Team Collaboration Workflows

Comprehensive guide for team collaboration patterns and workflows using the gh CLI.

## Table of Contents
- [Branch Strategies](#branch-strategies)
- [Code Review Process](#code-review-process)
- [Issue Triage and Assignment](#issue-triage-and-assignment)
- [Sprint Planning](#sprint-planning)
- [Release Coordination](#release-coordination)
- [Team Communication](#team-communication)
- [Onboarding New Team Members](#onboarding-new-team-members)
- [Common Team Workflows](#common-team-workflows)

## Branch Strategies

### Git Flow with gh CLI

```bash
# 1. Feature development
# Developer creates feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication
# ... work on feature ...
git push -u origin feature/user-authentication

# 2. Create PR to develop
gh pr create \
  --base develop \
  --title "feat: add user authentication" \
  --body "Implements user authentication with JWT tokens" \
  --label feature \
  --reviewer team-leads

# 3. Code review process
gh pr list --author @me --json number,reviewDecision
gh pr checks <pr-number> --watch

# 4. Merge to develop after approval
gh pr merge <pr-number> --squash --delete-branch

# 5. Release process (team lead)
git checkout main
git pull origin main
git merge develop
git push origin main

# 6. Create release
gh release create v1.0.0 --generate-notes --target main
```

### Trunk-Based Development

```bash
# 1. Create short-lived feature branch from main
git checkout main
git pull origin main
git checkout -b username/quick-fix

# 2. Make changes and push quickly (within hours/days)
# ... work ...
git push -u origin username/quick-fix

# 3. Create PR immediately
gh pr create --fill --base main --label quick-fix

# 4. Request fast review
gh pr edit <pr-number> --add-reviewer @team

# 5. Merge quickly after approval
gh pr merge <pr-number> --squash --delete-branch

# 6. Delete branch immediately
git checkout main
git pull origin main
```

### Release Branch Strategy

```bash
# 1. Create release branch from main
git checkout main
git pull origin main
git checkout -b release/v2.0
git push -u origin release/v2.0

# 2. Configure branch protection
gh api repos/:owner/:repo/branches/release/v2.0/protection -X PUT \
  -f required_pull_request_reviews='{"required_approving_review_count":2}' \
  -f enforce_admins=false

# 3. Cherry-pick bug fixes to release branch
git checkout release/v2.0
git cherry-pick <commit-hash>
git push

# 4. Create release from release branch
gh release create v2.0.0 --target release/v2.0 --generate-notes

# 5. Merge release branch back to main
gh pr create \
  --base main \
  --head release/v2.0 \
  --title "Release v2.0" \
  --body "Merging release branch back to main"
```

## Code Review Process

### Team Review Workflow

```bash
# 1. List PRs awaiting your review
gh pr list --search "is:open review-requested:@me"

# 2. Check out PR locally for testing
gh pr checkout <pr-number>

# 3. Run tests locally
npm test
# or
pytest

# 4. Review code in browser
gh pr view <pr-number> --web

# 5. Add review comments
gh pr review <pr-number> --comment --body "Consider adding error handling for edge case X"

# 6. Request changes if needed
gh pr review <pr-number> --request-changes --body "Please address the following issues..."

# 7. Approve when satisfied
gh pr review <pr-number> --approve --body "LGTM! Great work on the error handling."
```

### Team Review Best Practices

```bash
# Set review assignment rules in .github/CODEOWNERS
cat > .github/CODEOWNERS << 'EOF'
# Backend team reviews backend code
/backend/**         @org/backend-team

# Frontend team reviews frontend code
/frontend/**        @org/frontend-team

# DevOps reviews infrastructure
/.github/**         @org/devops-team
/infra/**           @org/devops-team

# Security team reviews auth code
/auth/**            @org/security-team
EOF

# PRs automatically request reviews from code owners
gh pr create --fill  # Automatically adds reviewers based on CODEOWNERS
```

### Review Metrics and Reporting

```bash
# Track team review velocity
gh pr list --search "is:closed merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number,reviews,mergedAt \
  | jq 'map({
      pr: .number,
      reviewers: [.reviews[].author.login] | unique,
      review_time: (.mergedAt | fromdateiso8601)
    })'

# Find PRs needing review
gh pr list --search "is:open review:required" --json number,title,author

# Find stale reviews
gh pr list --search "is:open review-requested:@me updated:<$(date -d '3 days ago' +%Y-%m-%d)"
```

## Issue Triage and Assignment

### Daily Triage Workflow

```bash
# 1. List new untriaged issues (no labels)
gh issue list --json number,title,labels,createdAt \
  | jq '.[] | select(.labels | length == 0) | {number, title, createdAt}'

# 2. Triage each issue
ISSUE=123
# Classify
gh issue edit $ISSUE --add-label bug
# Set priority
gh issue edit $ISSUE --add-label priority-high
# Assign milestone
gh issue edit $ISSUE --milestone "Sprint 5"
# Assign to team member
gh issue edit $ISSUE --add-assignee alice

# 3. Create triage report
cat > triage-report.md << EOF
# Daily Triage Report - $(date +%Y-%m-%d)

## New Issues Triaged
$(gh issue list --search "created:$(date +%Y-%m-%d)" --json number,title,labels \
  | jq -r '.[] | "- #\(.number): \(.title) [\(.labels | map(.name) | join(", "))]"')

## High Priority Issues
$(gh issue list --label priority-high --json number,title,assignees \
  | jq -r '.[] | "- #\(.number): \(.title) (assigned to: \(.assignees | map(.login) | join(", ")))"')
EOF

cat triage-report.md
```

### Automated Issue Assignment

```bash
# Round-robin assignment script
TEAM_MEMBERS=("alice" "bob" "charlie" "diana")
COUNTER=0

gh issue list --label "needs-assignment" --json number | jq -r '.[].number' | while read issue; do
  assignee=${TEAM_MEMBERS[$COUNTER]}
  gh issue edit $issue --add-assignee "$assignee" --remove-label "needs-assignment"
  echo "Assigned #$issue to $assignee"
  COUNTER=$(( (COUNTER + 1) % ${#TEAM_MEMBERS[@]} ))
done
```

### Workload Balancing

```bash
# Check team member workload
TEAM=("alice" "bob" "charlie")

for member in "${TEAM[@]}"; do
  open_count=$(gh issue list --assignee "$member" --json number | jq 'length')
  in_progress=$(gh issue list --assignee "$member" --search "is:open label:in-progress" --json number | jq 'length')
  echo "$member: $open_count total, $in_progress in progress"
done

# Reassign if overloaded
# If alice has too many issues, reassign some
gh issue list --assignee alice --search "is:open label:low-priority" --limit 5 --json number \
  | jq -r '.[].number' \
  | xargs -I {} gh issue edit {} --remove-assignee alice --add-assignee bob
```

## Sprint Planning

### Sprint Setup

```bash
# 1. Create sprint milestone
gh api repos/:owner/:repo/milestones -X POST \
  -f title="Sprint 5" \
  -f description="Two-week sprint from 2024-03-01 to 2024-03-14" \
  -f due_on="2024-03-14T23:59:59Z"

# 2. Identify sprint candidates
gh issue list --label "ready-for-sprint" --json number,title,labels

# 3. Assign issues to sprint
for issue in 101 102 103 104 105; do
  gh issue edit $issue --milestone "Sprint 5"
done

# 4. Assign to team members
gh issue edit 101 --add-assignee alice
gh issue edit 102 --add-assignee bob
gh issue edit 103 --add-assignee charlie

# 5. Add sprint label
for issue in 101 102 103 104 105; do
  gh issue edit $issue --add-label "sprint-5"
done
```

### Sprint Tracking

```bash
# Daily standup report
cat > standup-report.sh << 'EOF'
#!/bin/bash
SPRINT="Sprint 5"

echo "# Daily Standup Report - $(date +%Y-%m-%d)"
echo ""
echo "## Sprint: $SPRINT"
echo ""

# Sprint progress
total=$(gh issue list --milestone "$SPRINT" --json number | jq 'length')
completed=$(gh issue list --milestone "$SPRINT" --state closed --json number | jq 'length')
in_progress=$(gh issue list --milestone "$SPRINT" --search "is:open label:in-progress" --json number | jq 'length')
blocked=$(gh issue list --milestone "$SPRINT" --search "is:open label:blocked" --json number | jq 'length')

echo "Progress: $completed/$total completed ($in_progress in progress, $blocked blocked)"
echo ""

# Per team member
echo "## Team Member Status"
TEAM=("alice" "bob" "charlie")
for member in "${TEAM[@]}"; do
  echo ""
  echo "### $member"
  gh issue list --milestone "$SPRINT" --assignee "$member" --json number,title,labels \
    | jq -r '.[] | "- #\(.number): \(.title) [\(.labels | map(.name) | join(", "))]"'
done
EOF

chmod +x standup-report.sh
./standup-report.sh
```

### Sprint Retrospective

```bash
# Generate sprint retrospective data
cat > sprint-retro.sh << 'EOF'
#!/bin/bash
SPRINT="Sprint 5"

echo "# Sprint Retrospective - $SPRINT"
echo ""

# Velocity
completed=$(gh issue list --milestone "$SPRINT" --state closed --json number | jq 'length')
echo "Velocity: $completed issues completed"
echo ""

# Completed issues
echo "## Completed Issues"
gh issue list --milestone "$SPRINT" --state closed --json number,title,closedAt \
  | jq -r '.[] | "- #\(.number): \(.title) (closed: \(.closedAt | split("T")[0]))"'
echo ""

# Issues carried over
echo "## Carried Over to Next Sprint"
gh issue list --milestone "$SPRINT" --state open --json number,title \
  | jq -r '.[] | "- #\(.number): \(.title)"'
echo ""

# PRs merged
echo "## Pull Requests Merged"
gh pr list --search "is:merged merged:>=$(date -d '14 days ago' +%Y-%m-%d)" --json number,title,author \
  | jq -r '.[] | "- #\(.number): \(.title) by @\(.author.login)"'
EOF

chmod +x sprint-retro.sh
./sprint-retro.sh
```

## Release Coordination

### Team Release Process

```bash
# 1. Feature freeze (team lead)
echo "🎯 Feature freeze for v2.0 release"

# Lock main branch to prevent new features
gh api repos/:owner/:repo/branches/main/protection -X PUT \
  -f required_pull_request_reviews='{"required_approving_review_count":2}'

# 2. Create release branch
git checkout -b release/v2.0 main
git push -u origin release/v2.0

# 3. Notify team via issue
gh issue create \
  --title "Release v2.0 - Feature Freeze" \
  --body "Feature freeze for v2.0 release. Only bug fixes allowed on release/v2.0 branch." \
  --label release \
  --assignee team-leads

# 4. Team tests release branch
# Each team member checks out and tests
gh pr checkout release-pr-number
make test

# 5. Bug fixes during release
git checkout -b bugfix/release-issue release/v2.0
# Fix bug
git push -u origin bugfix/release-issue
gh pr create --base release/v2.0 --fill

# 6. Create release (after all fixes)
gh release create v2.0.0 --target release/v2.0 --generate-notes

# 7. Merge release branch back to main
gh pr create --base main --head release/v2.0 --title "Merge release v2.0"
```

### Release Checklist Automation

```bash
# Create release checklist
cat > .github/ISSUE_TEMPLATE/release-checklist.md << 'EOF'
---
name: Release Checklist
about: Track release preparation
title: 'Release v[VERSION] Checklist'
labels: release
---

## Pre-Release Checklist

- [ ] All milestone issues completed
- [ ] All PRs merged and reviewed
- [ ] Version numbers updated in code
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Database migrations tested
- [ ] Security audit completed

## Testing Checklist

- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance tests passing
- [ ] Manual QA completed
- [ ] Staging environment validated

## Release Checklist

- [ ] Release notes reviewed
- [ ] Release artifacts built
- [ ] Release branch created
- [ ] Tags created
- [ ] GitHub release published
- [ ] Artifacts uploaded

## Post-Release Checklist

- [ ] Production deployment successful
- [ ] Monitoring alerts configured
- [ ] Team notified
- [ ] Customers notified
- [ ] Blog post published
- [ ] Social media announcements
EOF

# Create release tracking issue
gh issue create --template release-checklist.md
```

## Team Communication

### PR-Based Communication

```bash
# Create discussion PR for architectural decisions
gh pr create \
  --draft \
  --title "[RFC] New API architecture" \
  --body "$(cat << EOF
# RFC: New API Architecture

## Problem
Current API architecture has scalability issues.

## Proposed Solution
Migrate to microservices architecture.

## Discussion Points
- Service boundaries
- Data consistency
- Migration strategy

cc @team
EOF
)" \
  --label rfc,discussion

# Team discusses in PR comments
gh pr view <pr-number> --web
```

### Status Updates via Issues

```bash
# Weekly status update
gh issue create \
  --title "Weekly Status - Week of $(date +%Y-%m-%d)" \
  --body "$(cat << EOF
# Team Status Update

## Completed This Week
$(gh pr list --search "is:merged merged:>=$(date -d '7 days ago' +%Y-%m-%d)" --json number,title | jq -r '.[] | "- #\(.number): \(.title)"')

## In Progress
$(gh pr list --search "is:open label:in-progress" --json number,title,author | jq -r '.[] | "- #\(.number): \(.title) (@\(.author.login))"')

## Blockers
$(gh issue list --search "is:open label:blocked" --json number,title | jq -r '.[] | "- #\(.number): \(.title)"')

## Next Week Goals
- Complete feature X
- Deploy to staging
- Start sprint 6 planning
EOF
)" \
  --label status-update
```

### Team Notifications

```bash
# Notify team of important PRs
IMPORTANT_PR=123
gh pr comment $IMPORTANT_PR --body "🚨 @team Important PR that affects all services. Please review by EOD."

# Notify on release
gh release create v1.0.0 --generate-notes
gh issue create \
  --title "📢 Version 1.0.0 Released" \
  --body "Version 1.0.0 has been released! $(gh release view v1.0.0 --json url --jq .url)" \
  --label announcement
```

## Onboarding New Team Members

### Onboarding Checklist

```bash
# Create onboarding issue for new team member
NEW_MEMBER="alice"

gh issue create \
  --title "Onboarding: $NEW_MEMBER" \
  --body "$(cat << EOF
# Onboarding Checklist for $NEW_MEMBER

## Access Setup
- [ ] GitHub org member added
- [ ] Repository access granted
- [ ] Team added (@org/backend-team)
- [ ] CODEOWNERS updated if needed

## Development Environment
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Local environment running
- [ ] Tests passing locally

## First Tasks
- [ ] Read CONTRIBUTING.md
- [ ] Review recent PRs: #101, #102, #103
- [ ] Complete starter issue: #104
- [ ] Submit first PR

## Team Introduction
- [ ] Team meeting introduction
- [ ] 1:1 with manager
- [ ] Pair programming session scheduled

cc @$NEW_MEMBER @team-lead
EOF
)" \
  --label onboarding \
  --assignee "$NEW_MEMBER"

# Create "good first issue" for new member
gh issue create \
  --title "Good First Issue: Update README" \
  --body "Welcome! This is a great first issue to get familiar with our codebase." \
  --label "good first issue" \
  --assignee "$NEW_MEMBER"
```

## Common Team Workflows

### Workflow 1: Morning Team Sync

```bash
#!/bin/bash
# morning-sync.sh - Run each morning to get team status

echo "=== Morning Team Sync ==="
echo ""

# PRs needing review
echo "📋 PRs Awaiting Review:"
gh pr list --search "is:open review:required" --json number,title,author \
  | jq -r '.[] | "  #\(.number): \(.title) by @\(.author.login)"'
echo ""

# Blocked issues
echo "🚫 Blocked Issues:"
gh issue list --label blocked --json number,title,assignees \
  | jq -r '.[] | "  #\(.number): \(.title) (blocked - assigned to: \(.assignees | map(.login) | join(", ")))"'
echo ""

# Failed CI runs
echo "❌ Failed CI Runs (last 24h):"
gh run list --status failure --created ">=$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)" --json workflowName,headBranch \
  | jq -r '.[] | "  \(.workflowName) on \(.headBranch)"'
echo ""

# Today's milestones
echo "🎯 Due Today:"
gh issue list --search "is:open due:$(date +%Y-%m-%d)" --json number,title \
  | jq -r '.[] | "  #\(.number): \(.title)"'
```

### Workflow 2: PR Review Session

```bash
#!/bin/bash
# team-review-session.sh - Batch review session

echo "=== Team Review Session ==="
echo ""

# List all open PRs sorted by age
gh pr list --json number,title,createdAt,author \
  | jq -r 'sort_by(.createdAt) | .[] | "PR #\(.number): \(.title) by @\(.author.login) (created: \(.createdAt | split("T")[0]))"' \
  | nl

echo ""
echo "Select PR number to review (or 'q' to quit):"

while read -r selection; do
  if [ "$selection" = "q" ]; then
    break
  fi

  # Get PR number from selection
  pr_number=$(gh pr list --json number --jq ".[$((selection-1))].number")

  # Open PR in browser
  gh pr view "$pr_number" --web

  # Checkout locally
  echo "Checkout locally? (y/n)"
  read -r checkout
  if [ "$checkout" = "y" ]; then
    gh pr checkout "$pr_number"
    echo "PR checked out. Review locally, then press Enter to continue..."
    read -r
  fi

  echo "Next PR? (number or 'q'):"
done
```

### Workflow 3: Release Day Coordination

```bash
#!/bin/bash
# release-day.sh - Coordinate team release activities

VERSION="$1"
if [ -z "$VERSION" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

echo "🚀 Release Day Coordination for $VERSION"
echo ""

# 1. Pre-release checks
echo "✅ Running pre-release checks..."
if ! make test; then
  echo "❌ Tests failed! Aborting release."
  exit 1
fi

# 2. Create release issue
RELEASE_ISSUE=$(gh issue create \
  --title "Release $VERSION - $(date +%Y-%m-%d)" \
  --body "Tracking release $VERSION deployment" \
  --label release \
  --json number --jq .number)

echo "📝 Created release tracking issue: #$RELEASE_ISSUE"

# 3. Build artifacts
echo "🔨 Building release artifacts..."
make build

# 4. Create release
echo "📦 Creating GitHub release..."
gh release create "$VERSION" \
  --generate-notes \
  --title "Release $VERSION" \
  dist/*

# 5. Notify team
gh issue comment "$RELEASE_ISSUE" --body "✅ Release $VERSION created and artifacts uploaded."

# 6. Deployment checklist
echo ""
echo "Next steps:"
echo "  1. Deploy to staging"
echo "  2. Run smoke tests"
echo "  3. Deploy to production"
echo "  4. Monitor for issues"
echo "  5. Close release issue #$RELEASE_ISSUE"
```

### Workflow 4: Incident Response

```bash
#!/bin/bash
# incident-response.sh - Quick incident response workflow

TITLE="$1"
if [ -z "$TITLE" ]; then
  echo "Usage: $0 \"Incident description\""
  exit 1
fi

# 1. Create incident issue
INCIDENT=$(gh issue create \
  --title "🚨 INCIDENT: $TITLE" \
  --body "$(cat << EOF
# Incident Report

## Impact
[Describe user impact]

## Timeline
- $(date +"%Y-%m-%d %H:%M:%S") - Incident detected

## Investigation
[Document investigation steps]

## Resolution
[Document resolution steps]

## Post-Incident
- [ ] Root cause analysis
- [ ] Post-mortem document
- [ ] Preventive measures implemented

cc @team @oncall
EOF
)" \
  --label incident,priority-critical \
  --json number --jq .number)

echo "Created incident issue: #$INCIDENT"

# 2. Create hotfix branch
git checkout -b "hotfix/incident-$INCIDENT" main

echo "Hotfix branch created. Fix the issue, then run:"
echo "  git push -u origin hotfix/incident-$INCIDENT"
echo "  gh pr create --title \"Hotfix: $TITLE\" --body \"Fixes #$INCIDENT\""
```

## Tips and Best Practices

1. **Clear communication**: Use issue and PR comments for async communication
2. **Code owners**: Define clear ownership with CODEOWNERS file
3. **Review culture**: Encourage constructive, timely code reviews
4. **Automation**: Automate repetitive tasks (triage, assignments, reports)
5. **Branch protection**: Enforce code review and CI checks
6. **Consistent labeling**: Maintain consistent label taxonomy
7. **Sprint ceremonies**: Use gh CLI to prepare standup and retro data
8. **Documentation**: Keep team workflows documented
9. **Onboarding**: Standardize onboarding process
10. **Metrics**: Track team velocity and review times
11. **Status updates**: Regular async status updates via issues
12. **Incident response**: Have documented incident response process

## Quick Reference

```bash
# Review management
gh pr list --search "review-requested:@me"    # PRs awaiting my review
gh pr list --search "reviewed-by:@me"         # PRs I've reviewed
gh pr review <pr> --approve                   # Approve PR

# Issue assignment
gh issue list --assignee @me                  # My assigned issues
gh issue edit <issue> --add-assignee user     # Assign issue
gh issue list --label "needs-assignment"      # Unassigned issues

# Sprint management
gh issue list --milestone "Sprint 5"          # Sprint issues
gh issue edit <issue> --milestone "Sprint 5"  # Add to sprint

# Team reporting
gh pr list --search "is:merged merged:>=2024-01-01" # Merged PRs
gh issue list --search "is:closed closed:>=2024-01-01" # Closed issues

# Release coordination
gh release create v1.0.0 --generate-notes     # Create release
gh issue create --label release               # Release tracking issue
```
