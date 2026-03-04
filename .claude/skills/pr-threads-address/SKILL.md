---
name: pr-threads-address
description: Review all unresolved PR review threads, address them by making necessary code changes, and commit the changes appropriately.
---

# /pr-threads-address

**Usage:** `/pr-threads-address [PR_NUMBER]`

**Description:** Review all unresolved PR review threads, address them by making necessary code changes, and commit the changes appropriately.

**Note:** If `PR_NUMBER` is omitted, the command will automatically detect and use the PR associated with the current branch.

## Workflow

1. Fetch and display all unresolved PR review threads
2. Analyze each thread to understand the requested changes
3. For each thread:
  1. Make the necessary code modifications
  2. (When possible) Add unit tests to verify the change
  3. Commit the changes with descriptive commit messages using conventional commit specification
4. Report back with a summary of addressed threads
5. Ask if the user wants to resolve the threads. If so, reply to each thread indicating what was done and then resolve the thread.

## When to use

Use this command when you have received PR review feedback and need to systematically address all unresolved threads before the PR can be merged.

## Example

```
/pr-threads-address 42
```

This will:
- View unresolved threads on PR #42
- Make code changes to address each thread
- Create commits for the changes
- Reply to reviewers with explanations
- Provide a summary of all addressed items
- Ask if you want to resolve the threads

## Prerequisites

Before using this command, check if the gh pr-review extension is installed:

```bash
gh extension list | grep -q pr-review || gh extension install agynio/gh-pr-review
```

## CLI Reference

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

### Reply to Review Threads

Respond to specific review comment threads:

```bash
gh pr-review comments reply --thread-id <PRRT_...> --body "<reply-text>" --repo <owner/repo> --pr <number>
```

**Multi-line replies** use heredoc syntax:

```bash
gh pr-review comments reply --thread-id PRRT_xyz789 --body "$(cat <<'EOF'
Fixed in commit abc123.

The changes include:
- Updated function signature
- Added error handling
- Updated tests
EOF
)" --repo owner/repo --pr 42
```

### Resolve a Thread

```bash
gh pr-review threads resolve --thread-id <PRRT_...> --repo <owner/repo>
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

## Usage Notes

1. **Repository Context**: Always include `--repo owner/repo` to ensure correct repository context, or run commands from within a local clone of the repository.

2. **Thread IDs**: Thread IDs (format `PRRT_...`) can be obtained from `review view --include-comment-node-id` or `threads list` commands.

3. **Review IDs**: Review IDs (format `PRR_...`) are returned by the `review --start` command and must be used for adding comments to that review.

4. **State Filters**: When using `--states`, provide a comma-separated list: `--states APPROVED,CHANGES_REQUESTED`

5. **Unresolved Focus**: Use `--unresolved --not_outdated` together to focus on actionable comments that need attention.
