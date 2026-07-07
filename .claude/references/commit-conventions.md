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

## Handling flaky test failures in CI

This section is about GitHub Actions jobs failing on a PR's CI run. (A test
that fails locally on your machine is not "flaky" for this purpose — reproduce
and fix it.)

- If a CI job fails on tests unrelated to the PR's changes, restart that job:
  `gh run rerun <run-id> --failed`.
- For each test that failed in the original CI job but **passes in the
  restarted job**, submit a GitHub Issue (`gh issue create`) containing a
  github.com URL link to the failed job and the error output when possible.
  Search existing issues for the test name first; if one exists, comment with
  the new occurrence instead of filing a duplicate.
- Label flake issues with **`flaky test`** (groups them for the staleness
  sweep), **`ai-generated-issue`** (marks the body as AI-written), and
  **`needs-triage`** (flags it for human attention):
  `gh issue create --label "flaky test,ai-generated-issue,needs-triage" ...`
- **Staleness rule**: when a flake issue has had no new occurrences reported
  for **30 days** (check the last occurrence comment's date), close it with a
  note that it can be reopened if the flake returns. Find candidates with
  `gh issue list --label "flaky test"`.
- Within a CI job, individual tests are already retried
  (pytest-rerunfailures); a `1 rerun` note in the job log means a flake was
  absorbed and the job passed — no action needed.
- A CI job that fails the **same way twice in a row** (original run + restart)
  is not flaky — treat it as real breakage and investigate, starting by
  reproducing the failing test locally.
- Before chasing a CI failure, check whether the same workflow also fails on
  `main` (`gh run list --workflow "Run tests" --branch main`). If it does, the
  breakage is pre-existing — report it (or file an issue), don't fix it in the
  unrelated PR.
- Never change tests or snapshots just to make an unrelated CI failure go
  away (e.g., do not run `--snapshot-update` to silence syrupy's "unused
  snapshots" error — that error can fail a CI job even when every test
  passed).

## Related

- Update `CHANGELOG.md` for user-facing changes
- Always run `make format` before committing
