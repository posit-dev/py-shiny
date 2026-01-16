#!/bin/bash
# pr-workflow.sh - Complete PR creation workflow with validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }
print_step() { echo -e "${BLUE}▶${NC} $1"; }

# Check if gh is installed
if ! command -v gh &> /dev/null; then
  print_error "GitHub CLI (gh) is not installed. Install from https://cli.github.com"
  exit 1
fi

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  print_error "Not in a git repository"
  exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
  print_error "You're on the main branch. Create a feature branch first."
  echo "  git checkout -b feature/your-feature"
  exit 1
fi

print_step "PR Workflow for branch: $CURRENT_BRANCH"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  print_error "You have uncommitted changes. Commit them first."
  git status --short
  exit 1
fi

# Push current branch
print_step "Step 1: Pushing branch to remote..."
git push -u origin "$CURRENT_BRANCH" 2>&1 || {
  print_error "Failed to push branch"
  exit 1
}
print_success "Branch pushed"
echo ""

# Check if PR already exists
print_step "Step 2: Checking for existing PR..."
EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null || echo "")

if [ -n "$EXISTING_PR" ]; then
  print_info "PR already exists: #$EXISTING_PR"
  gh pr view "$EXISTING_PR"
  echo ""
  read -p "Open PR in browser? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    gh pr view "$EXISTING_PR" --web
  fi
  exit 0
fi

# Get PR options
echo ""
print_step "Step 3: Configure PR options..."
echo ""

# Base branch
echo "Base branch (default: main):"
read -r BASE_BRANCH
BASE_BRANCH="${BASE_BRANCH:-main}"

# Draft PR?
echo ""
echo "Create as draft? (y/n, default: n):"
read -r -n 1 DRAFT_REPLY
echo
DRAFT_FLAG=""
if [[ $DRAFT_REPLY =~ ^[Yy]$ ]]; then
  DRAFT_FLAG="--draft"
  print_info "Will create draft PR"
fi

# Reviewers
echo ""
echo "Reviewers (comma-separated, optional):"
read -r REVIEWERS
REVIEWER_FLAGS=""
if [ -n "$REVIEWERS" ]; then
  IFS=',' read -ra REVIEWER_ARRAY <<< "$REVIEWERS"
  for reviewer in "${REVIEWER_ARRAY[@]}"; do
    reviewer=$(echo "$reviewer" | xargs) # trim whitespace
    REVIEWER_FLAGS="$REVIEWER_FLAGS --reviewer $reviewer"
  done
fi

# Labels
echo ""
echo "Labels (comma-separated, optional):"
read -r LABELS
LABEL_FLAGS=""
if [ -n "$LABELS" ]; then
  IFS=',' read -ra LABEL_ARRAY <<< "$LABELS"
  for label in "${LABEL_ARRAY[@]}"; do
    label=$(echo "$label" | xargs) # trim whitespace
    LABEL_FLAGS="$LABEL_FLAGS --label $label"
  done
fi

# Create PR
echo ""
print_step "Step 4: Creating pull request..."

# Use --fill to auto-populate title and body from commits
PR_CMD="gh pr create --base $BASE_BRANCH --fill $DRAFT_FLAG $REVIEWER_FLAGS $LABEL_FLAGS"

print_info "Running: $PR_CMD"
eval $PR_CMD

PR_NUMBER=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number')

print_success "Pull request created: #$PR_NUMBER"
echo ""

# Check CI status
print_step "Step 5: Checking CI status..."
sleep 3 # Wait a moment for CI to start

gh pr checks "$PR_NUMBER" || true
echo ""

# Open in browser?
read -p "Open PR in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  gh pr view "$PR_NUMBER" --web
fi

echo ""
print_success "PR workflow complete!"
print_info "Next steps:"
echo "  - Wait for CI checks to pass"
echo "  - Request reviews if needed: gh pr edit $PR_NUMBER --add-reviewer user"
echo "  - Merge when ready: gh pr merge $PR_NUMBER"
