---
name: gh-pr-review
description: Manage GitHub pull request review comments using the gh-pr-review extension. Use when the user asks to view, reply to, resolve, or manage PR review threads and inline comments from the terminal.
---

# GitHub PR Review Comment Management

Manage GitHub pull request review comments and threads using the `gh pr-review` extension. This extension enables viewing, navigating, replying to, and resolving review threads directly from the terminal.

## Prerequisites

Before using any pr-review commands, check if the extension is installed:

```bash
gh extension list | grep -q pr-review || gh extension install agynio/gh-pr-review
```

This will install the extension if it's not already present.

## Commands

### View PR Reviews and Comments

Display all reviews, inline comments, and replies for a pull request:

```bash
gh pr-review review view --pr <number> --repo <owner/repo>
```

**Common filters:**
- `--reviewer <login>` — Filter by specific reviewer
- `--states <list>` — Filter by review state (APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED)
- `--unresolved` — Show only unresolved threads
- `--not_outdated` — Exclude outdated threads
- `--tail <n>` — Show only the last n replies per thread
- `--include-comment-node-id` — Include GraphQL node IDs for replies

**Examples:**
```bash
# View all unresolved comments
gh pr-review review view --pr 42 --unresolved --repo owner/repo

# View comments from a specific reviewer
gh pr-review review view --pr 42 --reviewer username --repo owner/repo

# View only change requests, excluding outdated threads
gh pr-review review view --pr 42 --states CHANGES_REQUESTED --not_outdated --repo owner/repo
```

### Start a Pending Review

Create a new pending review to add comments before submission:

```bash
gh pr-review review --start --pr <number> --repo <owner/repo>
```

This returns a review ID (format: `PRR_...`) needed for adding comments.

### Add Review Comments

Add inline comments to a pending review:

```bash
gh pr-review review --add-comment --review-id <PRR_...> --path <file-path> --line <number> --body "<comment-text>" --repo <owner/repo>
```

**Flags:**
- `--review-id` — Review ID from `--start` command (required)
- `--path` — File path in the repository (required)
- `--line` — Line number for the comment (required)
- `--body` — Comment text (required)

### Submit a Review

Finalize and submit a pending review:

```bash
gh pr-review review --submit --review-id <PRR_...> --event <EVENT_TYPE> --body "<summary>" --repo <owner/repo>
```

**Event types:**
- `APPROVE` — Approve the changes
- `REQUEST_CHANGES` — Request changes before merging
- `COMMENT` — Submit general feedback without explicit approval

**Example:**
```bash
gh pr-review review --submit --review-id PRR_abc123 --event REQUEST_CHANGES --body "Please address the comments before merging" --repo owner/repo
```

### Reply to Review Threads

Respond to specific review comment threads:

```bash
gh pr-review comments reply --thread-id <PRRT_...> --body "<reply-text>" --repo <owner/repo>
```

**Example:**
```bash
gh pr-review comments reply --thread-id PRRT_xyz789 --body "Fixed in the latest commit" --repo owner/repo
```

### List Review Threads

Enumerate all review threads with filtering:

```bash
gh pr-review threads list --pr <number> --repo <owner/repo>
```

**Common filters:**
- `--unresolved` — Show only unresolved threads
- `--resolved` — Show only resolved threads

### Resolve/Unresolve Threads

Toggle thread resolution status:

```bash
# Resolve a thread
gh pr-review threads resolve --thread-id <PRRT_...> --repo <owner/repo>

# Unresolve a thread
gh pr-review threads unresolve --thread-id <PRRT_...> --repo <owner/repo>
```

## Complete Workflow Example

Here's a typical workflow for conducting a PR review:

```bash
# 1. View unresolved comments to understand what needs attention
gh pr-review review view --pr 42 --unresolved --repo owner/repo

# 2. Start a new pending review
REVIEW_ID=$(gh pr-review review --start --pr 42 --repo owner/repo)

# 3. Add inline comments
gh pr-review review --add-comment \
  --review-id "$REVIEW_ID" \
  --path "src/main.py" \
  --line 42 \
  --body "Consider using a context manager here" \
  --repo owner/repo

# 4. Submit the review with changes requested
gh pr-review review --submit \
  --review-id "$REVIEW_ID" \
  --event REQUEST_CHANGES \
  --body "Please address the inline comments" \
  --repo owner/repo

# 5. Later, reply to author's response
gh pr-review comments reply \
  --thread-id PRRT_xyz789 \
  --body "Thanks for the update, looks good now" \
  --repo owner/repo

# 6. Resolve the thread
gh pr-review threads resolve --thread-id PRRT_xyz789 --repo owner/repo
```

## Usage Notes

1. **Repository Context**: Always include `--repo owner/repo` to ensure correct repository context, or run commands from within a local clone of the repository.

2. **Thread IDs**: Thread IDs (format `PRRT_...`) can be obtained from `review view --include-comment-node-id` or `threads list` commands.

3. **Review IDs**: Review IDs (format `PRR_...`) are returned by the `review --start` command and must be used for adding comments to that review.

4. **Multi-line Comments**: Use heredoc syntax for multi-line comment bodies:
   ```bash
   gh pr-review comments reply --thread-id PRRT_xyz789 --body "$(cat <<'EOF'
   Good point. Here's my reasoning:

   1. Performance consideration
   2. Backwards compatibility
   3. Code maintainability
   EOF
   )" --repo owner/repo
   ```

5. **JSON Output**: Most commands support JSON output for programmatic processing and LLM integration. The tool is designed to provide "deterministic, stable output" with "compact, meaningful JSON."

6. **State Filters**: When using `--states`, provide a comma-separated list: `--states APPROVED,CHANGES_REQUESTED`

7. **Unresolved Focus**: Use `--unresolved --not_outdated` together to focus on actionable comments that need attention.
