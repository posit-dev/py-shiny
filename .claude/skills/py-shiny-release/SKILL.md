---
name: py-shiny-release
description: >
  Walk through the full Shiny for Python release train interactively, phase by phase.
  Use when the user says "release", "start a release", "py-shiny release", "release train",
  or wants to publish new versions of py-shiny and its ecosystem packages (py-htmltools,
  py-shinyswatch, py-shinywidgets, shinylive, py-shinylive, r-shinylive). Guides through
  version bumps, CI checks, tagging, PyPI publishing, conda-forge, Huggingface, site updates,
  and blog post publication.
---

# Shiny for Python Release Train

Walk through releasing the full py-shiny ecosystem interactively. Each phase requires
explicit user confirmation before proceeding to the next.

## Interactive Protocol

- Present one phase at a time with its checklist
- After presenting a phase, **stop and wait** for the user to confirm completion or ask for help
- Use `gh` CLI for GitHub operations (PRs, releases, tags)
- Track progress with a TodoWrite checklist
- If the user says "skip", mark the phase done and move on
- If a phase fails, help debug before moving on
- Never proceed to the next phase until the current one is resolved or explicitly skipped

### Pre-release gate (REQUIRED before any release action)

Before tagging, creating a GH Release, or pushing a tag for ANY package, **stop and run
this verification checklist with the user**:

1. **Show the release summary**:
   - Package name and version
   - RC branch name and PR link
   - CI status (link to the passing run)
   - Changelog entry (show the relevant section)
   - Dependency check result (any git-based deps found?)
   - **`TODO: release` markers** — run `grep -rn "TODO: release" . | grep -v '\.git/'` and
     list every marker with its holding PR and whether it acts before/after publish (see
     "Release-blocking `TODO: release` markers" above). None may be left unaddressed.
   - For py-shiny: shinylive example test results
2. **Ask for explicit confirmation**:
   > "Ready to release **{package} v{version}**? This will tag the commit and publish
   > to {registry}. Please confirm with 'yes' to proceed."
3. **Do NOT proceed** until the user explicitly says "yes", "go", "proceed", or equivalent
4. If the user raises concerns, address them before re-presenting the gate

## Getting Started

1. Ask the user which version of py-shiny is being released (e.g., `1.3.0`)
2. Ask if py-htmltools also needs a release (and what version)
3. Ask if any Shiny HTML Dependencies were updated (triggers shinyswatch prerequisite)
4. **Scan for release-blocking `TODO: release` markers** (see below) and fold each into
   the TodoWrite checklist
5. Create a TodoWrite checklist of all 13 phases plus any `TODO: release` items
6. Begin with Phase 1

## Release-blocking `TODO: release` markers

Some changes cannot land on their own and must be actioned during a release — e.g. a
temporary CI pin to an unmerged "holding" PR in a downstream repo, a dependency that
can only be un-pinned once an upstream package is on PyPI, or a docs version bump. These
are marked in-code with a greppable comment of the form:

```
TODO: release - <what to do, and when (before/after PyPI publish), plus the holding PR link>
```

**At the start of every release, and again at the pre-release gate, scan the py-shiny
repo for these markers and resolve each one:**

```bash
grep -rn "TODO: release" . ':!*.lock' 2>/dev/null | grep -v '\.git/'
```

For each marker:
1. Read it — it says what to do and whether it happens **before** or **after** the PyPI
   publish, and links the holding PR it depends on.
2. Add it to the TodoWrite checklist at the correct point in the phase order.
3. Do NOT complete the release while any `TODO: release` marker is unresolved: either the
   action has been performed and the marker removed, or the user has explicitly deferred it.

**Known holding item (as of py-shiny #2364 — `render.download` deprecation):**
`.github/workflows/pytest.yaml` temporarily pins the `py-shiny-templates` checkout to the
branch of [posit-dev/py-shiny-templates#55](https://github.com/posit-dev/py-shiny-templates/pull/55)
(which migrates the templates to `render.download_button`/`render.download_link`). During
Phase 3 (py-shiny), **after** this py-shiny version is published to PyPI: merge
py-shiny-templates#55, then open a follow-up py-shiny PR removing the `ref:` pin so CI
tracks the templates' default branch again. Remove the `TODO: release` comment in that PR.

## Phase Overview

```
[ ] Phase 1:  Prerequisites (shinyswatch update if HTML deps changed)
[ ] Phase 2:  Release py-htmltools
[ ] Phase 3:  Release py-shiny
[ ] Phase 4:  Release py-shinyswatch
[ ] Phase 5:  Release py-shinywidgets
[ ] Phase 6:  Update Shinylive (JS) repo
[ ] Phase 7:  Update py-shinylive
[ ] Phase 8:  Update r-shinylive
[ ] Phase 9:  Update py-shiny (bump shinylive docs version)
[ ] Phase 10: Update py-shiny-site
[ ] Phase 11: Conda-forge
[ ] Phase 12: Huggingface
[ ] Phase 13: Publish blog post
```

For detailed steps in each phase, read [references/release-phases.md](references/release-phases.md).

## Repos

| Package | Repo | Registry |
|---------|------|----------|
| py-htmltools | `posit-dev/py-htmltools` | PyPI |
| py-shiny | `posit-dev/py-shiny` | PyPI |
| py-shinyswatch | `posit-dev/py-shinyswatch` | PyPI |
| py-shinywidgets | `posit-dev/py-shinywidgets` | PyPI |
| shinylive (JS) | `posit-dev/shinylive` | GH Release artifact |
| py-shinylive | `posit-dev/py-shinylive` | PyPI |
| r-shinylive | `posit-dev/r-shinylive` | CRAN |
| py-shiny-site | `posit-dev/py-shiny-site` | GitHub Pages |
| conda htmltools | `conda-forge/py-htmltools-feedstock` | conda-forge |
| conda shiny | `conda-forge/py-shiny-feedstock` | conda-forge |

## General Package Release Pattern

Many phases (2-5, 7) follow this common flow:

1. Checkout branch `rc-vX.Y.Z`
2. Verify `pyproject.toml` has no git-based deps (e.g., no `htmltools @ git+https://...`)
3. Bump version (changelog + `__init__.py`, or tag-based for py-shiny)
4. Commit, push, open PR, wait for CI
5. Verify no additional commits were added to the RC branch beyond the release prep
6. **Run the pre-release gate** (see above) - present summary and get explicit user confirmation
7. Squash merge the RC PR into main via GitHub (this is the release commit)
8. Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
9. Create GH Release with changelog content, mark as "Latest"
10. Wait for PyPI publish to succeed
11. If publish fails: delete tag + GH Release, fix, redo

### GH Release naming conventions

Each repo's PyPI publish workflow triggers based on the GH Release **title** matching a specific
prefix. Always check the workflow file if unsure, but the known patterns are:

| Repo | Release title must start with | Example |
|------|-------------------------------|---------|
| py-htmltools | `htmltools` | `htmltools 0.6.1` |
| py-shiny | `shiny` | `shiny 1.6.1` |
| py-shinyswatch | `shinyswatch` | `shinyswatch 0.10.0` |
| py-shinywidgets | `shinywidgets` | `shinywidgets 0.8.0` |
| py-shinylive | `shinylive` | `shinylive 0.8.8` |

Also, before writing release notes, check existing releases for format conventions:
`gh api repos/<org>/<repo>/releases --jq '.[:3] | .[] | .body'`

## Parallelism

Once the PyPI packages are published (phases 2-7), several later phases can run concurrently
since they are independent:

- **Phases 8, 9, 10** (r-shinylive, py-shiny docs bump, py-shiny-site) can all be started
  in parallel — they don't depend on each other, only on the earlier PyPI releases.
- **Phase 11** (conda-forge) is passive — just checking for bot PRs — and can be monitored
  alongside other work.
- **Phase 12** (Huggingface) is a quick restart/check and can be done anytime after py-shiny
  is on PyPI.

When the user asks to skip ahead or work on multiple phases, take advantage of this. Open PRs
for independent phases, watch CI in the background, and report results as they come in.

## On Failure

- For PyPI failures: remind user to delete the tag and GH Release before retrying
- For CI failures: help investigate logs with `gh run view`
- For shinylive build failures: check `make clean && make all` output
- Never proceed to the next phase until the current one is resolved or explicitly skipped
