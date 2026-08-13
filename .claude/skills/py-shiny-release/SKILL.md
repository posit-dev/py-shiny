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
- **Shut down every long-running process a phase started before marking it complete** (see
  below)

### Clean up background processes at the end of each phase

Several phases start servers or watchers that never exit on their own — most notably Phase 6's
`make serve` (a watch-mode dev server on port 3000). Left running, they hold ports, keep
rebuilding on file changes, and clutter the background task list for the rest of a release that
spans many hours.

When a phase is done, before marking it complete:

1. Identify what the phase left behind, e.g.:
   ```bash
   lsof -nP -iTCP:3000 -sTCP:LISTEN     # Phase 6 `make serve`
   lsof -nP -iTCP:8100 -sTCP:LISTEN     # Playwright's _shinylive webServer
   ```
2. Kill it and confirm the port actually closed, rather than assuming:
   ```bash
   kill <pid>
   curl -s -o /dev/null -m 3 -w "%{http_code}\n" http://localhost:3000/ || echo closed
   ```
3. Say in the phase wrap-up which processes were shut down.

Only keep a server alive past its phase if a later step genuinely needs it, and say so
explicitly. Note that Playwright's own `webServer` (port 8100) stops itself when a run
finishes — it is `make serve` that lingers.

Watchers that poll CI or PyPI are fine to leave; they exit on their own. It is the servers
that need killing.

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
3. **Scan the holding PR's own diff for `TODO: release` markers before merging it.** A
   holding PR frequently carries its own stopgaps — most often a `requirements.txt` or
   `pyproject.toml` switched to `git+https://github.com/posit-dev/py-shiny.git@main`
   because the API it needs is not on PyPI yet. Merging the holding PR without reverting
   those leaves a **git dependency in the downstream repo**, which is exactly what the
   pre-release gate screens for everywhere else. Resolve them, verify against the newly
   published wheel that the API really exists (check the parameter names the downstream
   code passes, not just that the symbol imports), then merge.
4. Do NOT complete the release while any `TODO: release` marker is unresolved: either the
   action has been performed and the marker removed, or the user has explicitly deferred it.

There is no standing holding item at the moment. When one exists, describe it here with
its holding PR link and whether it acts before or after publish, and delete the note once
the release that consumes it has shipped.

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

Most repos' PyPI publish workflows are gated on the GH Release **title**. The gate is not
the same everywhere — check the workflow file if unsure. Use the titles below regardless,
for consistency:

| Repo | Title to use | Publish gate |
|------|--------------|--------------|
| py-htmltools | `htmltools 0.7.0` | starts with `htmltools` |
| py-shiny | `shiny 1.7.0` | starts with `shiny` |
| py-shinyswatch | `shinyswatch 0.12.0` | **not** `TEST` (see below) |
| py-shinywidgets | `shinywidgets 0.8.1` | starts with `shinywidgets` |
| py-shinylive | `shinylive 0.8.10` | starts with `shinylive` |

**Two different failure modes**, so it matters which gate a repo uses:

- **Prefix gates** (py-shiny, py-htmltools, py-shinywidgets, py-shinylive) fail *silently*:
  a mistitled release makes the publish step skip while the workflow still reports success,
  so the package never reaches PyPI. See Phase 7 for how to recover (recreate the GH Release
  object to re-fire `release: published`; keep the tag).
- **py-shinyswatch inverts this.** `.github/workflows/pytest.yaml` gates prod publish on
  `if: ${{ !startsWith(github.event.release.name, 'TEST') }}` and test-PyPI publish on
  `startsWith(..., 'TEST')`. So *any* non-`TEST` title publishes to prod — the title is
  cosmetic, and the real hazard is the opposite one: an accidental `TEST` prefix silently
  diverts the release to test.pypi.org.

Also, before writing release notes, check existing releases for format conventions:
`gh api repos/<org>/<repo>/releases --jq '.[:3] | .[] | .body'`

### Publishing to PyPI is not instantaneous

After a `Deploy to PyPI` job reports success, PyPI's index can lag by minutes. Two
consequences:

- Poll **PyPI itself**, not just the workflow, before starting a phase that installs the
  new version: `curl -s https://pypi.org/pypi/<pkg>/json | jq -r .info.version`.
- A downstream repo's CI may still fail to resolve the new floor
  (`ERROR: Could not find a version that satisfies the requirement shiny>=X.Y.Z`) on one
  runner while the rest of the matrix succeeds. That is a stale index, not a bad pin —
  **rerun the job**, do not weaken the requirement.

### Verifying build commands

When running a long build through a pipe (`make all 2>&1 | tail -60`), the reported exit
status comes from `tail`, not from `make` — a failed build looks like success. Either drop
the pipe, use `set -o pipefail`, or verify the build from its artifacts (expected wheels
present and at the expected versions) rather than from the exit code.

### Never report CI status from a truncated or PR-level view

Two ways a status report goes wrong, both of which happened during the v1.7.0 train — once
claiming green when a check was failing, once claiming no-CI when everything had passed:

- **Do not pipe the check list through `head`.** These repos have 8-350 checks and the failing
  one is rarely in the first few. Aggregate instead of sampling, then list only what is not
  passing:

  ```bash
  gh pr checks <N> --repo <repo> --json state \
    --jq '[.[]|.state]|group_by(.)|map({state:.[0],n:length})'
  gh pr checks <N> --repo <repo> --json name,state,link \
    --jq '.[]|select(.state!="SUCCESS" and .state!="SKIPPED")|"\(.name) \(.state)\n  \(.link)"'
  ```

- **`gh pr checks` reports on the PR's current head.** If anything pushed a commit after
  yours (a formatter bot, for instance), checks can read as missing or blocked even though CI
  passed on your commit. Confirm by listing runs with their SHAs (`gh run list --json
  headSha,status,conclusion`) and comparing against `gh pr view --json headRefOid`.

Relatedly, `mergeStateStatus: BLOCKED` does **not** mean CI failed — it usually means a
required review is missing, or a check suite is awaiting approval. Check which before
reporting.

### Read existing PR and issue comments before investigating

Downstream repos accumulate diagnosis in comment threads across release cycles. Before
digging into a failure — especially a recurring one on a conda-forge feedstock — read the
comments on the open and recently closed PRs. During the v1.7.0 train a full root-cause
analysis of the feedstock failure already existed in a PR comment, and was re-derived from
scratch instead.

### Clone downstream repos outside the py-shiny working tree

Cloning a release repo into a subdirectory of py-shiny (e.g. `.context/`) makes tooling walk
up and pick up py-shiny's configuration. `pytest` in particular resolves py-shiny's
`pytest.ini` as its rootdir and then fails with `unrecognized arguments: --numprocesses`.
Clone to a sibling directory, or override with `-o addopts="" --rootdir=.`.

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
