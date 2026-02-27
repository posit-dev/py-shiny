---
name: pr-threads-resolve
description: Bulk resolve unresolved PR review threads. Useful after manually addressing threads or after using /pr-threads-address.
---

# /pr-threads-resolve

**Usage:** `/pr-threads-resolve [PR_NUMBER]`

**Description:** Bulk resolve unresolved PR review threads. Useful after manually addressing threads or after using `/pr-threads-address`.

**Note:** If `PR_NUMBER` is omitted, the command will automatically detect and use the PR associated with the current branch.

## Workflow

1. Fetch and display all unresolved PR review threads
2. Show thread details (file, line, comment text)
3. Ask for confirmation or allow selective resolution
4. Resolve the confirmed threads
5. Report back with a summary of resolved threads

## When to use

Use this command when you have already addressed PR review threads and want to bulk resolve them, or when you need to clean up threads that are no longer relevant.

## Example

```
/pr-threads-resolve 42
```

This will:
- List all unresolved threads on PR #42
- Show what each thread is about
- Ask which threads to resolve (all or specific ones)
- Resolve the selected threads
- Provide a summary of resolved items

## Prerequisites

Before using this command, check if the gh pr-review extension is installed:

```bash
gh extension list | grep -q pr-review || gh extension install agynio/gh-pr-review
```

## Key Commands Used

### List Unresolved Threads
```bash
gh pr-review threads list --pr <number> --unresolved --repo <owner/repo>
```

### View Unresolved Comments with Details
```bash
gh pr-review review view --pr <number> --unresolved --not_outdated --repo <owner/repo>
```

### Resolve a Thread
```bash
gh pr-review threads resolve --thread-id <PRRT_...> --repo <owner/repo>
```

### Bulk Resolve Example
```bash
# Get all unresolved thread IDs and resolve them
gh pr-review threads list --pr 42 --unresolved --repo owner/repo | \
  jq -r '.threads[].id' | \
  xargs -I {} gh pr-review threads resolve --thread-id {} --repo owner/repo
```
