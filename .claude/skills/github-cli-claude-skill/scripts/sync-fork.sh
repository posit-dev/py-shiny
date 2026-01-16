#!/bin/bash
# sync-fork.sh - Sync a forked repository with upstream

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

# Parse arguments
BRANCH="${1:-main}"
FORCE="${2:-false}"

print_step "Syncing fork with upstream..."
echo ""

# Check if this is a fork
REPO_INFO=$(gh repo view --json isFork,parent)
IS_FORK=$(echo "$REPO_INFO" | jq -r .isFork)

if [ "$IS_FORK" != "true" ]; then
  print_error "This repository is not a fork"
  echo ""
  print_info "If you want to sync with a specific remote, use:"
  echo "  git fetch <remote>"
  echo "  git merge <remote>/<branch>"
  exit 1
fi

PARENT_REPO=$(echo "$REPO_INFO" | jq -r .parent.owner.login + "/" + .parent.name)
print_info "Fork of: $PARENT_REPO"
echo ""

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ] && [ "$FORCE" != "--force" ]; then
  print_error "You have uncommitted changes. Commit or stash them first."
  git status --short
  echo ""
  print_info "Or use --force to sync anyway (this will reset local changes)"
  exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_info "Current branch: $CURRENT_BRANCH"
print_info "Syncing branch: $BRANCH"
echo ""

# Warn if syncing a different branch than current
if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  print_info "You're on '$CURRENT_BRANCH' but syncing '$BRANCH'"
  read -p "Continue? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Cancelled"
    exit 0
  fi
fi

# Method 1: Use gh repo sync (simpler, recommended)
print_step "Step 1: Syncing with upstream using gh repo sync..."

if [ "$FORCE" = "--force" ]; then
  print_info "Force syncing (will overwrite local changes)"
  gh repo sync --branch "$BRANCH" --force
else
  gh repo sync --branch "$BRANCH"
fi

print_success "Sync complete!"
echo ""

# If we're on the synced branch, pull the changes
if [ "$CURRENT_BRANCH" = "$BRANCH" ]; then
  print_step "Step 2: Pulling synced changes to local branch..."
  git pull origin "$BRANCH"
  print_success "Local branch updated"
else
  print_info "Note: You're on '$CURRENT_BRANCH'. To update your local '$BRANCH' branch:"
  echo "  git checkout $BRANCH"
  echo "  git pull origin $BRANCH"
fi

echo ""
print_success "Fork synced with upstream!"

# Show sync status
echo ""
print_info "Checking sync status..."
git fetch origin "$BRANCH" &>/dev/null

if git rev-parse "$BRANCH" &>/dev/null; then
  AHEAD=$(git rev-list --count origin/$BRANCH..$BRANCH 2>/dev/null || echo "0")
  BEHIND=$(git rev-list --count $BRANCH..origin/$BRANCH 2>/dev/null || echo "0")

  if [ "$AHEAD" = "0" ] && [ "$BEHIND" = "0" ]; then
    print_success "Local and remote are in sync"
  else
    if [ "$AHEAD" != "0" ]; then
      print_info "Local is $AHEAD commit(s) ahead"
    fi
    if [ "$BEHIND" != "0" ]; then
      print_info "Local is $BEHIND commit(s) behind"
    fi
  fi
fi

echo ""
print_info "To sync other branches:"
echo "  $0 <branch-name>"
echo ""
print_info "To force sync (overwrite local changes):"
echo "  $0 <branch-name> --force"
