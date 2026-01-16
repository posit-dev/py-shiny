#!/bin/bash
# create-feature-branch.sh - Create and push a feature branch with optional issue

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }

# Check if gh is installed
if ! command -v gh &> /dev/null; then
  print_error "GitHub CLI (gh) is not installed. Install from https://cli.github.com"
  exit 1
fi

# Parse arguments
FEATURE_NAME="$1"
ISSUE_NUMBER="$2"
BASE_BRANCH="${3:-main}"

if [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-name> [issue-number] [base-branch]"
  echo ""
  echo "Examples:"
  echo "  $0 user-authentication"
  echo "  $0 user-authentication 42"
  echo "  $0 user-authentication 42 develop"
  exit 1
fi

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  print_error "Not in a git repository"
  exit 1
fi

# Create branch name
if [ -n "$ISSUE_NUMBER" ]; then
  BRANCH_NAME="feature/${FEATURE_NAME}-${ISSUE_NUMBER}"
else
  BRANCH_NAME="feature/${FEATURE_NAME}"
fi

print_info "Creating feature branch: $BRANCH_NAME from $BASE_BRANCH"

# Make sure we have latest base branch
print_info "Fetching latest changes..."
git fetch origin

# Check if base branch exists
if ! git show-ref --verify --quiet "refs/remotes/origin/$BASE_BRANCH"; then
  print_error "Base branch '$BASE_BRANCH' does not exist on remote"
  exit 1
fi

# Create and checkout branch
print_info "Creating branch..."
git checkout -b "$BRANCH_NAME" "origin/$BASE_BRANCH"

# Push branch to remote
print_info "Pushing branch to remote..."
git push -u origin "$BRANCH_NAME"

print_success "Feature branch created and pushed: $BRANCH_NAME"

# If issue number provided, add comment
if [ -n "$ISSUE_NUMBER" ]; then
  print_info "Adding comment to issue #$ISSUE_NUMBER..."
  if gh issue comment "$ISSUE_NUMBER" --body "Started work on this in branch \`$BRANCH_NAME\`" 2>/dev/null; then
    print_success "Added comment to issue #$ISSUE_NUMBER"
  else
    print_error "Could not add comment to issue #$ISSUE_NUMBER (issue may not exist)"
  fi
fi

echo ""
print_info "Next steps:"
echo "  1. Make your changes"
echo "  2. git add . && git commit -m 'feat: description'"
echo "  3. git push"
echo "  4. gh pr create --fill"
