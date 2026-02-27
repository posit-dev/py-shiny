---
# https://raw.githubusercontent.com/posit-dev/connect/refs/heads/main/.claude/skills/sub-issue/SKILL.md?token=GHSAT0AAAAAAC7BSG2IOYC77SLM7CEB3I3C2LKMOXQ
name: sub-issue
description: Manage GitHub sub-issues using the gh-sub-issue extension. Use when the user asks to create, list, add, or remove sub-issues (child issues) from a parent issue.
---

# GitHub Sub-Issue Management

Manage GitHub sub-issues (child issues) using the `gh sub-issue` extension.

## Prerequisites

Before using any sub-issue commands, check if the extension is installed:

```bash
gh extension list | grep -q sub-issue || gh extension install yahsan2/gh-sub-issue
```

This will install the extension if it's not already present.

## Commands

### Create a new sub-issue

Create a new issue directly linked as a child of a parent issue:

```bash
gh sub-issue create --parent <parent-issue> --title "<title>" --body "<body>" --repo posit-dev/connect
```

**Flags:**
- `-p, --parent` — Parent issue number or URL (required)
- `-t, --title` — Title for new sub-issue (required)
- `-b, --body` — Body text for the sub-issue
- `-l, --label` — Comma-separated labels
- `-a, --assignee` — Comma-separated usernames
- `-m, --milestone` — Milestone name or number
- `--project` — Projects (can specify multiple times)

### Link an existing issue as a sub-issue

```bash
gh sub-issue add <parent-issue> <sub-issue> --repo posit-dev/connect
```

### List sub-issues of a parent

```bash
gh sub-issue list <parent-issue> --repo posit-dev/connect
gh sub-issue list <parent-issue> --state all --repo posit-dev/connect
```

### Remove a sub-issue link

```bash
gh sub-issue remove <parent-issue> <sub-issue> --repo posit-dev/connect
```

## Usage Notes

1. Always include `--repo posit-dev/connect` to ensure correct repository context
2. When creating multiple sub-issues, create them sequentially to avoid rate limiting
3. Use `--body` with heredoc for multi-line descriptions:

```bash
gh sub-issue create --parent 123 --title "My issue" --body "$(cat <<'EOF'
Description here.

**Acceptance criteria:**
1. First item
2. Second item
EOF
)" --repo posit-dev/connect
```

4. Reference the parent issue in the body for context (e.g., "Part of #123")
