# Bundled Agent Skills

The shiny package ships [Agent Skills](https://agentskills.io) under
`shiny/.agents/skills/` — one directory per skill, each with a `SKILL.md`.
They are **package data**: they ship in the wheel and are discovered by
installers such as [library-skills](https://library-skills.io) (which symlinks
them into a project's `.agents/skills/` or `.claude/skills/`). A `shiny skills
list|get` CLI subcommand is planned as a zero-dependency way to read them.

**Audience:** coding agents *using* shiny to build, test, and debug apps — not
contributors to shiny itself. Contributor-facing guidance belongs in
`.claude/references/`, not here. If a topic serves both audiences, the bundled
skill documents the public API and the reference file documents the internals.

## Layout

```
shiny/.agents/skills/
  <skill-name>/
    SKILL.md          # required
    <supporting>.*    # optional: only for heavy reference or reusable scripts
```

- Directory names are short kebab-case topics: `debugging`, `testing`,
  `modules`, `express`, ...
- Names are **unprefixed** (no `shiny-` prefix): installers namespace skills
  by package, and the description scopes the skill to Shiny for Python.
- Keep everything in `SKILL.md` unless a supporting file earns its keep
  (100+ lines of API reference, or a runnable script an agent should copy).

## Frontmatter contract

```yaml
---
name: <must match the directory name>
description: Use when <triggering conditions, symptoms, and temptations>...
---
```

- `description` states **when to load the skill, never what it teaches or the
  workflow it contains**. If the description summarizes the process, agents
  follow the summary and skip the body. Good descriptions list the situations,
  symptoms, and search phrases an agent would have when the skill applies —
  including the *wrong* approach it might be about to take (e.g. "...or when
  tempted to add print statements or hidden outputs").
- Third person, starts with "Use when", under ~500 characters.
- Descriptions across skills must not overlap: agents pick a skill by
  description alone, so two skills matching the same symptom means the wrong
  one gets loaded. When adding a skill, re-read the other descriptions and
  sharpen the boundaries.

These rules (name matches directory, description present) are enforced by
`tests/pytest/test_packaging.py`.

## Content shape

Skills are reference docs, not tutorials. The shape that works:

1. **Overview** — the core principle in 1-3 sentences, including what NOT to
   do (the workaround the skill replaces).
2. **Task-oriented sections** — one per job the agent came to do, each with a
   short runnable example against the **public API only** (imports included,
   copy-paste ready). One excellent example per pattern; no variations.
3. **Quick-reference table** for enumerable facts (env vars, flags, marker
   strings).
4. **Common mistakes** — concrete symptom → fix pairs, especially the
   non-obvious gotchas (e.g. module namespacing of ids, 404 when a feature
   flag is off).

Keep a skill focused on one topic and roughly 400-800 words. If a section
outgrows that, it is probably a second skill. Prefer extending an existing
skill over creating a new one; create a new directory only for a genuinely
separate topic with its own triggering conditions.

## Maintenance

- Bundled skills are **user-facing documentation**. When a PR changes an API
  that a skill documents, update the skill in the same PR — grep
  `shiny/.agents/skills/` for the API name as part of the change.
- Skills describe behavior as shipped, not as planned: never document an API
  before it is merged.
- Adding or materially changing a skill warrants a CHANGELOG entry.

## Validation

- `pytest tests/pytest/test_packaging.py` — checks the frontmatter contract
  and that every file under `shiny/.agents/` is matched by the
  `[tool.setuptools.package-data]` globs in `pyproject.toml`. The explicit
  `.agents/**` glob is required because `**` does not match hidden
  directories; without it skills silently drop out of the wheel.
- To confirm against a real build:
  `uv build --wheel && unzip -l dist/shiny-*.whl | grep .agents`
- For a new skill, do a before/after check: give a fresh agent (no skill) a
  task the skill targets and note what it reaches for; then repeat with the
  skill available. If the "after" run doesn't change the approach, the
  description isn't triggering or the body isn't teaching — fix before
  shipping.
