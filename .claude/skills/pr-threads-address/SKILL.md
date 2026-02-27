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

## Key Commands Used

### View Unresolved Threads
```bash
gh pr-review review view --pr <number> --unresolved --not_outdated --repo <owner/repo>
```

### Reply to Review Thread
```bash
gh pr-review comments reply --thread-id <PRRT_...> --body "<reply-text>" --repo <owner/repo>
```

### Multi-line Reply Example
```bash
gh pr-review comments reply --thread-id PRRT_xyz789 --body "$(cat <<'EOF'
Fixed in commit abc123.

The changes include:
- Updated function signature
- Added error handling
- Updated tests
EOF
)" --repo owner/repo
```
