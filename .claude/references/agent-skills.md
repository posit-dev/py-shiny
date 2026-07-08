# Bundled Agent Skills

The shiny package ships [Agent Skills](https://agentskills.io) under
`shiny/.agents/skills/` — one directory per skill, each with a `SKILL.md`,
following the [Agent Skills specification](https://agentskills.io/specification).
They are **package data**: they ship in the wheel and are discovered by
installers such as [library-skills](https://library-skills.io) (which symlinks
them into a project's `.agents/skills/` or `.claude/skills/`). The `shiny
skills list|get|path` CLI subcommands (implemented in `shiny/_main/_skills.py`)
are a zero-dependency way to read them: `get <name>` prints the SKILL.md, and
`path <name>` prints the skill's directory so supporting files
(`references/`, `scripts/`) can be read from the installed package.

**Audience:** coding agents *using* shiny to build, test, and debug apps — not
contributors to shiny itself. Contributor-facing guidance belongs in
`.claude/references/`, not here. If a topic serves both audiences, the bundled
skill documents the public API and the reference file documents the internals.

## Layout

Per the spec, a skill is a directory containing at minimum a `SKILL.md`, plus
three conventional optional directories:

```
shiny/.agents/skills/
  <skill-name>/
    SKILL.md          # required: frontmatter + instructions
    scripts/          # optional: self-contained runnable code
    references/       # optional: on-demand docs (loaded only when needed)
    assets/           # optional: templates, images, data files
```

- Skill names are short topics: `debugging`, `testing`, `modules`, `express`, ...
- Names are **unprefixed** (no `shiny-` prefix): installers namespace skills
  by package, and the description scopes the skill to Shiny for Python.
- Keep everything in `SKILL.md` until a file earns its keep. Heavy reference
  material (100+ lines) goes in `references/` — agents load those on demand,
  so smaller focused files cost less context. Link with relative paths from
  the skill root (`references/REFERENCE.md`) and keep references one level
  deep — no chains of files pointing at files.

## Frontmatter

```yaml
---
name: <skill-name>
description: <what the skill covers and when to use it>
---
```

Required fields (spec constraints):

- `name` — 1-64 characters; lowercase letters, numbers, and hyphens only; no
  leading, trailing, or consecutive hyphens; **must match the directory name**.
- `description` — 1-1024 characters, non-empty. Covers both *what the skill
  does* and *when to use it*, with keywords agents would match on.

How to write the description (this is the only part of a skill loaded at
startup — agents decide from it alone whether to activate the skill):

- Lead with a one-clause summary of what the skill covers, then "Use when…"
  listing triggering conditions, symptoms, and search phrases — including the
  *wrong* approach an agent might be about to take (e.g. "…or when tempted to
  add print statements or hidden outputs").
- Do **not** summarize the skill's workflow or step-by-step process: agents
  that get the recipe from the description follow it and skip the body.
- Third person. Descriptions across skills must not overlap: agents pick a
  skill by description alone, so two skills matching the same symptom means
  the wrong one gets loaded. When adding a skill, re-read the other
  descriptions and sharpen the boundaries.

Optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`) are
defined by the spec but usually unnecessary here: skills inherit the package's
MIT license, and `compatibility` is only for skills with environment
requirements beyond shiny itself (e.g. requires Playwright installed).

The name/directory match and description presence are enforced by
`tests/pytest/test_packaging.py`.

## Body content

The body is loaded in full once a skill activates, so size it for progressive
disclosure: keep `SKILL.md` under ~500 lines (well under 5000 tokens), moving
detail to `references/`. Skills are reference docs, not tutorials. The shape
that works:

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

Anything in `scripts/` must be self-contained (or clearly document its
dependencies), emit helpful error messages, and handle edge cases — agents
run these directly.

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
- The spec's reference validator checks frontmatter and naming conventions:
  `uvx --from skills-ref agentskills validate shiny/.agents/skills/<name>`
  (see [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)).
- To confirm against a real build:
  `uv build --wheel && unzip -l dist/shiny-*.whl | grep .agents`
- For a new skill, do a before/after check: give a fresh agent (no skill) a
  task the skill targets and note what it reaches for; then repeat with the
  skill available. If the "after" run doesn't change the approach, the
  description isn't triggering or the body isn't teaching — fix before
  shipping.
