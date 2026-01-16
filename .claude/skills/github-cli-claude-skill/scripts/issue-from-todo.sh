#!/bin/bash
# issue-from-todo.sh - Create GitHub issues from TODO comments in code

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
AUTO_CREATE="${1:-false}"
LABEL="${2:-todo}"

print_step "Scanning for TODO comments..."
echo ""

# Find all TODO comments in tracked files
# Patterns: TODO:, TODO(name):, FIXME:, HACK:
TODO_PATTERN="(TODO|FIXME|HACK)(\([^)]*\))?:"

# Use git grep to only search tracked files
TODOS=$(git grep -n -i -E "$TODO_PATTERN" -- ':!*.md' ':!*.txt' 2>/dev/null || echo "")

if [ -z "$TODOS" ]; then
  print_info "No TODO comments found in tracked files"
  exit 0
fi

# Parse and display TODOs
echo "$TODOS" | while IFS= read -r line; do
  # Extract file:line:content
  FILE=$(echo "$line" | cut -d: -f1)
  LINE_NUM=$(echo "$line" | cut -d: -f2)
  CONTENT=$(echo "$line" | cut -d: -f3-)

  # Extract TODO text
  TODO_TEXT=$(echo "$CONTENT" | sed -E "s/.*$TODO_PATTERN\s*//" | xargs)

  echo "────────────────────────────────────────"
  echo "File:    $FILE:$LINE_NUM"
  echo "Content: $TODO_TEXT"
  echo ""

  # If auto-create is enabled, create issue
  if [ "$AUTO_CREATE" = "true" ] || [ "$AUTO_CREATE" = "--create" ]; then
    # Create issue title
    TITLE="TODO: $TODO_TEXT"

    # Create issue body with file reference
    BODY="Found in \`$FILE\` at line $LINE_NUM:

\`\`\`
$CONTENT
\`\`\`

File: $FILE:$LINE_NUM"

    # Create issue
    print_info "Creating issue..."
    ISSUE_NUM=$(gh issue create \
      --title "$TITLE" \
      --body "$BODY" \
      --label "$LABEL" \
      --json number --jq .number)

    print_success "Created issue #$ISSUE_NUM"
    echo ""
  else
    # Ask if user wants to create issue
    read -p "Create issue for this TODO? (y/n/q) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Qq]$ ]]; then
      print_info "Quitting"
      exit 0
    fi

    if [[ $REPLY =~ ^[Yy]$ ]]; then
      # Allow editing title
      echo "Issue title (default: TODO: $TODO_TEXT):"
      read -r CUSTOM_TITLE
      TITLE="${CUSTOM_TITLE:-TODO: $TODO_TEXT}"

      # Create issue body
      BODY="Found in \`$FILE\` at line $LINE_NUM:

\`\`\`
$CONTENT
\`\`\`

File: $FILE:$LINE_NUM"

      # Ask for additional context
      echo "Additional context (optional, press Enter to skip):"
      read -r ADDITIONAL_CONTEXT
      if [ -n "$ADDITIONAL_CONTEXT" ]; then
        BODY="$BODY

## Additional Context
$ADDITIONAL_CONTEXT"
      fi

      # Create issue
      print_info "Creating issue..."
      ISSUE_NUM=$(gh issue create \
        --title "$TITLE" \
        --body "$BODY" \
        --label "$LABEL" \
        --json number --jq .number)

      print_success "Created issue #$ISSUE_NUM"
    fi
    echo ""
  fi
done

echo "────────────────────────────────────────"
print_success "TODO scan complete!"

# Summary
TODO_COUNT=$(echo "$TODOS" | wc -l | xargs)
print_info "Found $TODO_COUNT TODO comments"

if [ "$AUTO_CREATE" != "true" ] && [ "$AUTO_CREATE" != "--create" ]; then
  echo ""
  print_info "Tip: Run with --create flag to automatically create issues for all TODOs"
  echo "  $0 --create [label]"
fi
