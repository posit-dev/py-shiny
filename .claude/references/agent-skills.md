# Bundled Agent Skills

The shiny package ships a single [Agent Skill](https://agentskills.io) under
`shiny/.agents/skills/shiny-for-python/`, following the [Agent Skills
specification](https://agentskills.io/specification). Its `SKILL.md` is a
grouped router: a short index of topics, each pointing at a
`references/<topic>.md` file with the actual instructions. It is **package
data**: it ships in the wheel and is discovered by installers such as
[library-skills](https://library-skills.io) (which symlinks it into a
project's `.agents/skills/` or `.claude/skills/`). The `shiny skills
list|path` CLI subcommands (implemented in `shiny/_main/_skills.py`) are a
zero-dependency way to inspect it: `list` shows each bundled skill's name and
description, and `path <name>` prints the skill's directory so its `SKILL.md`
and supporting files (`references/`, `scripts/`) can be read from the installed
package.

**Audience:** coding agents *using* shiny to build, test, and debug apps — not
contributors to shiny itself. Contributor-facing guidance belongs in
`.claude/references/`, not here. If a topic serves both audiences, the bundled
skill documents the public API and the reference file documents the internals.

## Layout

Per the spec, a skill is a directory containing at minimum a `SKILL.md`, plus
three conventional optional directories:

```
shiny/.agents/skills/
  shiny-for-python/
    SKILL.md          # required: frontmatter + grouped index of topics
    scripts/          # optional: self-contained runnable code
    references/       # one file per topic, e.g. debugging.md, testing.md, modules.md
    assets/           # optional: templates, images, data files
```

- There is **one** skill directory, `shiny-for-python`; it is not prefixed
  further (installers namespace skills by package, and the description scopes
  the skill to Shiny for Python).
- `SKILL.md`'s body is a grouped index: short sections that bucket related
  topics (core concepts, layout/UI, outputs, app capabilities, extending
  shiny, ...), each with a row per topic linking to its
  `references/<topic>.md` file and a one-line "use when" trigger.
- **Adding a new topic does not mean creating a new top-level skill
  directory.** Add a `references/<topic>.md` file with the topic's
  instructions, then add one index row for it in `shiny-for-python/SKILL.md`
  (which bucket it belongs in, plus its "use when" trigger). Link with
  relative paths from the skill root (`references/<topic>.md`) and keep
  references one level deep — no chains of files pointing at files.

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
- Third person. There is only one skill, so its description is a single
  umbrella statement covering every domain the index groups (reactivity,
  layout, outputs, testing, ...) — the description's job is to get the skill
  to activate at all. Disambiguating between topics is the index's job: each
  row's "use when" trigger in `SKILL.md` (and, if that topic has its own
  activation notes, the top of its `references/<topic>.md`) is what routes
  the agent to the right reference file once the skill is loaded.

Optional fields (`license`, `compatibility`, `metadata`, `allowed-tools`) are
defined by the spec but usually unnecessary here: skills inherit the package's
MIT license, and `compatibility` is only for skills with environment
requirements beyond shiny itself (e.g. requires Playwright installed).

The name/directory match and description presence are enforced by
`tests/pytest/test_packaging.py`, which parses the frontmatter as real YAML
(installers like library-skills use a strict parser). Watch for YAML-special
sequences in an unquoted `description`: a `: ` (colon-space) or ` #` makes the
value invalid YAML — wrap the whole description in double quotes if it contains
one (e.g. `description: "…Index skill: read this…"`).

## Body content

`SKILL.md`'s body is just the index — short bucket headings and one row per
topic — so it stays small even as topics are added. Each topic's real content
lives in its own `references/<topic>.md`, loaded on demand only when that
topic is relevant, so size each one for progressive disclosure: keep it well
under 5000 tokens. Skills are reference docs, not tutorials. The shape that
works for a `references/<topic>.md` file:

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

Keep a `references/<topic>.md` focused on one topic and roughly 400-800
words. If a section outgrows that, it is probably a second topic. Prefer
extending an existing topic file over creating a new one; add a new
`references/<topic>.md` (plus its index row) only for a genuinely separate
topic with its own triggering conditions.

Anything in `scripts/` must be self-contained (or clearly document its
dependencies), emit helpful error messages, and handle edge cases — agents
run these directly.

## Maintenance

- Bundled skills are **user-facing documentation**. When a PR changes an API
  that a skill documents, update the skill in the same PR — grep
  `shiny/.agents/skills/` for the API name as part of the change.
- Skills describe behavior as shipped, not as planned: never document an API
  before it is merged.
- Adding or materially changing a topic warrants a CHANGELOG entry.

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
- For a new topic, do a before/after check: give a fresh agent (no skill) a
  task the topic targets and note what it reaches for; then repeat with the
  skill available. If the "after" run doesn't change the approach, the
  umbrella description isn't triggering, the index row isn't routing to the
  right reference file, or the reference file isn't teaching — fix before
  shipping.
