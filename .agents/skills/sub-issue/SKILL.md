---
# Source: https://github.com/posit-dev/connect/blob/5581fe8d1b7d1e78ba6b78ecfd1963122eb63049/.claude/skills/sub-issue/SKILL.md
name: sub-issue
description: Manage GitHub sub-issues using the gh CLI (v2.94.0+). Use when the user asks to create, list, add, or remove sub-issues (child issues) from a parent issue.
---

# GitHub Sub-Issue Management

Manage GitHub sub-issues (child issues) using native `gh` CLI commands (v2.94.0+).

## Prerequisites

Before using any sub-issue commands, verify the `gh` CLI is v2.94.0 or newer:

```bash
gh --version
```

If the version is older than 2.94.0, the native sub-issue flags (`--parent`, `--add-sub-issue`, `--remove-sub-issue`, `--remove-parent`) will not be available. In that case, advise the user to upgrade `gh` before proceeding.

## Commands

### Create a new sub-issue

Create a new issue directly linked as a child of a parent issue:

```bash
gh issue create --parent <parent-issue> --title "<title>" --body "<body>" --repo posit-dev/py-shiny
```

**Flags:**
- `--parent` — Parent issue number or URL (required for sub-issue linking)
- `--title` — Title for new sub-issue (required)
- `--body` — Body text for the sub-issue
- `--label` — Comma-separated labels
- `--assignee` — Comma-separated usernames
- `--milestone` — Milestone name or number
- `--project` — Project to add the issue to

### Add an existing issue as a sub-issue

```bash
gh issue edit <parent-issue> --add-sub-issue <child-issue> --repo posit-dev/py-shiny
```

### Set or change the parent of an issue

```bash
gh issue edit <child-issue> --parent <parent-issue> --repo posit-dev/py-shiny
```

### List sub-issues of a parent

```bash
gh issue view <parent-issue> --json subIssues,subIssuesSummary --repo posit-dev/py-shiny
```

### Remove a sub-issue link

```bash
gh issue edit <parent-issue> --remove-sub-issue <child-issue> --repo posit-dev/py-shiny
```

### Remove parent from an issue

```bash
gh issue edit <child-issue> --remove-parent --repo posit-dev/py-shiny
```

## Usage Notes

1. Always include `--repo posit-dev/py-shiny` to ensure correct repository context
2. When creating multiple sub-issues, create them sequentially to avoid rate limiting
3. Use `--body` with heredoc for multi-line descriptions:

```bash
gh issue create --parent 123 --title "My issue" --body "$(cat <<'EOF'
Description here.

**Acceptance criteria:**
1. First item
2. Second item
EOF
)" --repo posit-dev/py-shiny
```

4. Reference the parent issue in the body for context (e.g., "Part of #123")
