# Git Commit and PR Conventions

This project uses **conventional commits** for commit messages and PR titles.

## Commit Message Format

```
<type>: <description>

[optional body]
```

An optional scope may be added when it clarifies the affected area, e.g.
`fix(tests): Read UserInput.text in chat module test app`.

## Types

- **feat**: New feature (e.g., `feat: Add input_submit_textarea component`)
- **fix**: Bug fix (e.g., `fix: Resolve session context error in modules`)
- **docs**: Documentation changes (e.g., `docs: Update reactive programming guide`)
- **refactor**: Code refactoring without behavior change
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **perf**: Performance improvements
- **style**: Code style/formatting changes (not user-facing style)

## Guidelines

- Use present tense: "Add feature" not "Added feature"
- Keep the description concise (under 72 characters for the first line)
- Use sentence case: "Add feature" not "add feature"
- No period at the end of the subject line
- Body is optional but useful for explaining "why" not "what"
- Do not add `Co-Authored-By: Claude ...` trailers

## PR Titles

PR titles should follow the same conventional commit format (PRs are squash
merged, so the PR title becomes the commit message on `main`):

- `feat: Add Toolbar component`
- `fix: Pin griffe to <2.0.0 for quartodoc compatibility`
- `refactor: Simplify reactive graph invalidation logic`

## Merging PRs

- When instructed to merge a PR, **squash merge** (`gh pr merge <number> --squash`)
  only after the **full test suite (150+ GHA jobs) has succeeded** (`gh pr checks`).
- **Never use `gh pr merge --auto`**: this repo has no required checks, so
  `--auto` merges instantly instead of waiting for CI. Watch CI to completion,
  then merge.

## Handling flaky test failures

- If tests unrelated to the PR fail, restart the failed jobs:
  `gh run rerun <run-id> --failed`.
- For each broken test that **passes within the restarted job**, submit a
  GitHub Issue (`gh issue create`) containing a github.com URL link to the
  broken job and the error output when possible. Search existing issues for
  the test name first; if one exists, comment with the new occurrence instead
  of filing a duplicate.
- Individual tests are already retried in-job (pytest-rerunfailures); a
  `1 rerun` note in the log means a flake was absorbed and needs no action.
- A test that fails the **same way twice in a row** is not flaky — treat it as
  real breakage and investigate.
- Before chasing a failure, check whether `main` fails the same way
  (`gh run list --workflow "Run tests" --branch main`). If it does, the
  breakage is pre-existing — report it, don't fix it in the unrelated PR.
- Never change tests or snapshots just to quiet an unrelated failure (e.g., do
  not run `--snapshot-update` to silence syrupy's "unused snapshots" error —
  a job can fail from that even when every test passed).

## Related

- Update `CHANGELOG.md` for user-facing changes
- Always run `make format` before committing
