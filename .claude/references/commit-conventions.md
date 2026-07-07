# Git Commit and PR Conventions

This project uses **conventional commits** for commit messages and PR titles.

## Commit Message Format

```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
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
- Always include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` when
  Claude writes the code

## PR Titles

PR titles should follow the same conventional commit format (PRs are squash
merged, so the PR title becomes the commit message on `main`):

- `feat: Add Toolbar component`
- `fix: Pin griffe to <2.0.0 for quartodoc compatibility`
- `refactor: Simplify reactive graph invalidation logic`

## Related

- Update `CHANGELOG.md` for user-facing changes
- Always run `make format` before committing
