#!/bin/bash
# Quick installer for GitHub CLI Claude Skill

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }

echo "GitHub CLI Claude Skill Installer"
echo "=================================="
echo ""

# Determine installation location
if [ "$1" = "--project" ]; then
  INSTALL_DIR=".claude/skills"
  SCOPE="project-specific"
else
  INSTALL_DIR="$HOME/.claude/skills"
  SCOPE="user-level"
fi

print_info "Installing $SCOPE..."
print_info "Installation directory: $INSTALL_DIR"
echo ""

# Create skills directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Clone or update
SKILL_DIR="$INSTALL_DIR/github-cli-claude-skill"

if [ -d "$SKILL_DIR" ]; then
  print_info "Skill already exists. Updating..."
  cd "$SKILL_DIR"
  git pull
else
  print_info "Cloning skill..."
  cd "$INSTALL_DIR"
  git clone https://github.com/doug-skinner/github-cli-claude-skill.git
fi

echo ""
print_success "Installation complete!"
echo ""
print_info "Next steps:"
echo "  1. Ensure 'gh' CLI is installed and authenticated:"
echo "     gh auth login"
echo ""
echo "  2. Restart Claude Code"
echo ""
echo "  3. Verify installation by asking Claude:"
echo "     \"List my open GitHub issues\""
echo ""

if [ "$SCOPE" = "user-level" ]; then
  print_info "This skill is now available in all your projects!"
else
  print_info "This skill is available in this project only."
fi
