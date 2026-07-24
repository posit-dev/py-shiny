# Release Phases - Detailed Steps

## Phase 1: Prerequisites

- [ ] Check if any Shiny HTML Dependencies were updated or added
- [ ] If yes, show the user which files changed (e.g., `git diff main -- shiny/www/shared/`) and ask if py-shinyswatch and/or py-shinywidgets need to be updated before proceeding
- [ ] **Python version check**: Look up the current [Python release schedule](https://devguide.python.org/versions/) and check if any Python versions have reached end-of-life since the last release. If so, ask the user whether to drop them from the following packages during this release cycle:
  - py-shiny (`pyproject.toml`, CI workflow)
  - py-htmltools (`pyproject.toml`, CI workflow)
  - py-shinyswatch (`setup.cfg` or `pyproject.toml`, CI workflow)
  - py-shinywidgets (`setup.cfg` or `pyproject.toml`, CI workflow)
  - py-shinylive (`setup.cfg`, CI workflow)

  Also check if a new Python version should be added to test matrices (e.g., 3.13, 3.14).

Ask the user: "Were any Shiny HTML Dependencies updated or added in this release cycle? Here are the changed files: [show diff]. Does py-shinyswatch or py-shinywidgets need updating?"

---

## Phase 2: Release py-htmltools

Repo: `posit-dev/py-htmltools`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-htmltools/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version

Follow the general package release pattern:

- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Verify `pyproject.toml` has no git-based dependencies
- [ ] Bump `__version__` in `htmltools/__init__.py` to the release version (e.g., `0.7.1`). `pyproject.toml` resolves the version from this attribute at build time (via `[tool.setuptools.dynamic]`) — it is **not** derived from the git tag, so this manual bump is required.
- [ ] Update `CHANGELOG.md`: rename `[UNRELEASED]` to `[X.Y.Z] - YYYY-MM-DD`
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, CI status, changelog, dep check) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z`
- [ ] Push the tag first (before pushing main): `git push origin vX.Y.Z`
- [ ] Create GH Release. **Important**: The release title must start with `htmltools` (e.g., `htmltools 0.6.1`) — the PyPI publish workflow depends on this naming convention.
- [ ] Wait for PyPI publish to succeed
- [ ] Only after PyPI succeeds: push main to origin (`git push origin main`)

If CI fails, fix issues before continuing. If PyPI fails, delete tag and release, fix, redo.

Ask user: "Is py-htmltools being released this cycle?"

---

## Phase 3: Release py-shiny

Repo: `posit-dev/py-shiny`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-shiny/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version
- [ ] Automatically test all shinylive examples for errors (see procedure below)
- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Verify `pyproject.toml` has no git-based dependencies (e.g., no `htmltools @ git+https://...`)
- [ ] Note: for py-shiny, tagging the commit triggers the version bump automatically (no manual `__init__.py` edit needed)
- [ ] Bump version in CHANGELOG.md
- [ ] Update `CITATION.cff`: set `version:` to `X.Y.Z` and `date-released:` to today's date (`YYYY-MM-DD`, the intended release date).
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, CI status, changelog, dep check, shinylive test results) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Create GH Release (title: `shiny X.Y.Z`, copy changelog content, mark as Latest). **Important**: The release title must be `shiny X.Y.Z` (not `vX.Y.Z`) — the PyPI publish workflow depends on this naming convention.
- [ ] Wait for PyPI publish to succeed

### Shinylive example testing procedure

A reusable Playwright test script is available at [`references/test_shinylive_site.py`](references/test_shinylive_site.py). It:
- Takes a base URL as argument (works for local, github.io, or shinylive.io)
- Uses fresh browser contexts per example (no cached state)
- Appends a cache-busting `?v={timestamp}` query param
- Tests all Python examples in parallel batches of 5
- Reports pass/fail with console errors

**Usage:**
```bash
# Local (during Phase 6 build)
python references/test_shinylive_site.py "http://localhost:3000/examples/"

# github.io (after main branch deploy)
python references/test_shinylive_site.py "https://posit-dev.github.io/shinylive/py/examples/"

# shinylive.io (after deploy branch push)
python references/test_shinylive_site.py "https://shinylive.io/py/examples/"

# Phase 3: py-shiny docs site shinylive
python references/test_shinylive_site.py "https://posit-dev.github.io/py-shiny/shinylive/py/examples/"
```

**Requires:** `pip install playwright && playwright install chromium`

After running, present results to the user:

Ask user: "I've tested all N shinylive examples. X passed, Y had errors. Here are the broken apps for you to verify: [links]. Should we proceed or investigate the errors?"

---

## Phase 4: Release py-shinyswatch

Repo: `posit-dev/py-shinyswatch`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-shinyswatch/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version

Follow the general package release pattern (same as Phase 2).

Ask user: "Is py-shinyswatch being released? What version? Do we need to update docs after shinylive updates?"

---

## Phase 5: Release py-shinywidgets

Repo: `posit-dev/py-shinywidgets`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-shinywidgets/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version

Follow the general package release pattern (same as Phase 2).

Ask user: "Is py-shinywidgets being released this cycle? What version?"

---

## Phase 6: Update Shinylive (JS) repo

Repo: `posit-dev/shinylive`

### Submodule updates

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/shinylive/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version
- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Bump version in `package.json`
- [ ] Run `make submodules` to init all submodules
- [ ] Update **all** Python package submodules to their latest released versions — not just py-shiny:
  - `packages/py-shiny` → latest py-shiny tag
  - `packages/py-htmltools` → latest py-htmltools tag (if released this cycle)
  - `packages/py-shinywidgets` → latest py-shinywidgets tag
  - `packages/py-faicons` → check if update needed
- [ ] Run `make clean && make all`
- [ ] **Verify `shinylive_lock.json`** — check that ALL package versions match their latest releases. The lockfile reflects what's actually bundled. Don't trust that updating one submodule will cascade to others.
- [ ] Run `npm install --package-lock-only` to sync `package-lock.json` version with `package.json`

### Local testing and PR

- [ ] Add and/or edit examples to use new features or API
- [ ] Run `make serve` and automatically test all local shinylive examples for errors (see procedure below)
- [ ] Commit and push RC branch
- [ ] Open a PR from `rc-vX.Y.Z` → `main` for visibility and CI
- [ ] Wait for CI to pass (if any)
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, submodule versions, build output, local test results) and get explicit user confirmation before proceeding
- [ ] Update the PR description to reflect the final set of changes (package versions, Makefile changes, etc.)
- [ ] Check PR reviews/feedback (e.g., Copilot) and address before merging

### Release and deploy

- [ ] Squash merge the RC PR into `main` via GitHub
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] **DEPLOY GATE 1 (github.io)**: Wait for the `main` branch deploy to github.io to finish. Then bust all browser caches and verify apps work on github.io using the Playwright-based example testing procedure. **Important**: When testing, always append a cache-busting query parameter (e.g., `?v={timestamp}`) to URLs or use a fresh incognito/private browser context to ensure you're testing the newly deployed version, not a cached old version. **Do NOT push to `deploy` until github.io is verified.**
- [ ] Ask user: "github.io apps have been tested — X passed, Y failed. Ready to push to `deploy` (shinylive.io)?" Get explicit confirmation.
- [ ] Only after github.io verification passes and user confirms: push to `deploy` branch (for shinylive.io) using `git push origin main:deploy`
- [ ] **DEPLOY GATE 2 (shinylive.io)**: Wait for the `deploy` branch deploy to shinylive.io to finish. Then bust all browser caches and verify apps work on shinylive.io using the same testing procedure with cache-busting (fresh incognito context or `?v={timestamp}` query params).
- [ ] Create GH Release. Check existing release note conventions (`gh api repos/posit-dev/shinylive/releases --jq '.[:3] | .[] | .body'`) and match the format used by recent releases.
- [ ] Wait for release to succeed and build artifact to appear in GH Release page

### Local shinylive example testing procedure

Same approach as the Phase 3 shinylive testing, but against the local `make serve` URL:

1. Determine the local serve URL (typically `http://localhost:8080`)
2. List Python examples from the local repo's `examples/python/` directory
3. The base URL for each example is:
   `http://localhost:8080/py/examples/#EXAMPLE_NAME`
4. For each example, use Playwright MCP tools to:
   a. Navigate to the example URL (`browser_navigate`)
   b. Wait for the app to load (`browser_wait_for`)
   c. Check browser console messages (`browser_console_messages`) for Python errors/tracebacks
   d. Record the result (pass/fail + any error text)
5. Present the same summary table and broken app links as in Phase 3
6. Ask user to verify any broken apps before proceeding

If release fails, delete tag and GH Release, fix, redo.

Ask user: "Which package submodules need updating?"

---

## Phase 7: Update py-shinylive

Repo: `posit-dev/py-shinylive`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-shinylive/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version
- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Bump `SHINYLIVE_PACKAGE_VERSION` in `shinylive/_version/__init__.py`
- [ ] Bump `SHINYLIVE_ASSETS_VERSION` in `shinylive/_version/__init__.py` to the Phase 6 shinylive JS version
- [ ] Update `CHANGELOG.md`
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, shinylive JS version, changelog) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Create GH Release with title **`shinylive X.Y.Z`** (NOT `py-shinylive X.Y.Z` and NOT `vX.Y.Z`). The `.github/workflows/build.yml` "Deploy to PyPI" step is gated by `if: startsWith(github.event.release.name, 'shinylive')` — if the release title does not start with `shinylive`, the publish step silently skips and the package never reaches PyPI even though the workflow reports success.
- [ ] Wait for PyPI publish to succeed

If PyPI fails, delete tag and release, fix, redo. If the publish step was skipped because of a mistitled release (e.g. `py-shinylive X.Y.Z`), delete the GH Release object only (keep the tag) and recreate it with title `shinylive X.Y.Z` — this re-fires the `release: published` event and the publish step will then match the `startsWith('shinylive')` predicate.

Ask user: "Is py-shinylive being released this cycle?"

---

## Phase 8: Update r-shinylive

Repo: `posit-dev/r-shinylive`

Use the shinylive JS version from Phase 6 (already known at this point).

- [ ] Check for any existing open PRs that bump `SHINYLIVE_ASSETS_VERSION` (`gh pr list --repo posit-dev/r-shinylive --state open --search "SHINYLIVE_ASSETS_VERSION"`). If found, close them.
- [ ] Create a branch with the following changes:
  - Update `SHINYLIVE_ASSETS_VERSION` in `R/version.R` to the Phase 6 shinylive JS version
  - Bump `Version` in `DESCRIPTION` to the next dev version (e.g., `0.4.1.9000`)
  - Add a `NEWS.md` entry under the dev version heading (e.g., `# shinylive 0.4.1.9000`) noting the assets update
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR (squash merge)

---

## Phase 9: Update py-shiny (post-release)

Repo: `posit-dev/py-shiny`

- [ ] Create a branch to bump shinylive version in the `[doc]` extras of `pyproject.toml` (e.g., `"shinylive>=0.8.8"`)
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR

---

## Phase 10: Update py-shiny-site

Repo: `posit-dev/py-shiny-site`

- [ ] Update the py-shiny submodule to point to the release tag
- [ ] Update py-shinylive version in `requirements.txt`
- [ ] Create a PR
- [ ] Use deployment preview to verify:
  - [ ] API docs are correct
  - [ ] Examples run properly
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR

Ask user: "Ready to update the docs site? I'll help create the PR."

---

## Phase 11: Conda-forge

- [ ] Check `conda-forge/py-htmltools-feedstock` for auto-created PR from bot (only if py-htmltools was released)
- [ ] Check `conda-forge/py-shiny-feedstock` for auto-created PR from bot
- [ ] If PRs exist and tests pass, they should auto-merge (look for `[bot-automerge]` prefix)
- [ ] If auto-merge doesn't happen, create an issue with the appropriate bot command
- [ ] Note: Only py-htmltools and py-shiny have conda-forge feedstocks. py-shinyswatch, py-shinywidgets, and py-shinylive do NOT have feedstocks as of 2026-03.

### Known issue: license_file references

The feedstock `recipe/meta.yaml` has an `about/license_file` section that lists bundled license files from py-shiny (e.g., `shiny/www/shared/highlight/LICENSE`, `shiny/www/shared/busy-indicators/spinners/LICENSE`, `shiny/www/shared/jqueryui/LICENSE.txt`). If py-shiny removes or renames any vendored dependency between releases, these paths become stale and the conda-forge build will fail with `ValueError: License file ... does not exist`.

**If a build fails for this reason:**
1. Identify which license files no longer exist by checking `shiny/www/shared/` in the current release
2. Comment on the bot PR explaining which line(s) to remove from `license_file`
3. The feedstock maintainers (currently `wch` and `sugatoray`) can push the fix to the bot's branch or request a `bot-rerun` after updating `meta.yaml` on main
4. Note: Carson (cpsievert) is **not** a feedstock maintainer and cannot push directly — if this is needed, ask to be added or request a maintainer to act

### Bot PR timing

The conda-forge bot (`regro-cf-autotick-bot`) typically creates PRs within a few hours of a PyPI release, but it can sometimes take up to a day. If no PR appears after 24 hours, check the bot's [status page](https://github.com/regro/cf-scripts) for outages.

Ask user: "Have the conda-forge bot PRs appeared? Any issues with auto-merge?"

---

## Phase 12: Huggingface

Repo: https://huggingface.co/spaces/posit/shiny-for-python-template

This is a Hugging Face Space (not a GitHub repo), so `gh` CLI cannot be used. The Space runs a Shiny Express app (`app.py`) with a `Dockerfile` that installs from `requirements.txt`.

- [ ] Check the Space's current `requirements.txt` via the HF web UI or `WebFetch` on `https://huggingface.co/spaces/posit/shiny-for-python-template/raw/main/requirements.txt`
- [ ] The `requirements.txt` currently does **not** pin versions — `shiny`, `shinywidgets`, etc. are listed without version specifiers. This means a container restart will pull the latest versions from PyPI automatically.
- [ ] If the Space shows a "Runtime error", try **restarting the Space** from the HF Settings page first — this often resolves stale container issues after upstream packages are updated.
- [ ] If the restart doesn't fix it, investigate the container logs for dependency conflicts or app errors.
- [ ] Verify the Space loads and the dashboard works after the restart.

---

## Phase 13: Publish blog post

Repo: shiny-dev-center

- [ ] Write or finalize the release blog post
- [ ] Open PR for review
- [ ] Merge and publish

Ask user: "The blog post should be written in a fresh Claude session to avoid context bloat from this release skill. Please start a new session and use `/release-post` to draft the blog post. Let me know when it's done so we can mark this phase complete."

---

## Post-release: Cross-reference PRs

After all phases are complete, go back and comment on every PR created during this release train linking it to the original py-shiny release PR for traceability. Use:

```bash
gh pr comment <PR_NUMBER> --repo <REPO> --body "This PR is part of the py-shiny v<VERSION> release train. See posit-dev/py-shiny#<RELEASE_PR_NUMBER> for the originating release."
```

Do this for all PRs created across repos (py-shinyswatch, shinylive, py-shinylive, r-shinylive, py-shiny docs bump, py-shiny-site, etc.).
