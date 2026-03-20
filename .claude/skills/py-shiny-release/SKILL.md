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
4. Create a TodoWrite checklist of all 13 phases
5. Begin with Phase 1

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

## On Failure

- For PyPI failures: remind user to delete the tag and GH Release before retrying
- For CI failures: help investigate logs with `gh run view`
- For shinylive build failures: check `make clean && make all` output
- Never proceed to the next phase until the current one is resolved or explicitly skipped
