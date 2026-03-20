# Release Phases - Detailed Steps

## Phase 1: Prerequisites

- [ ] Check if any Shiny HTML Dependencies were updated or added
- [ ] If yes, show the user which files changed (e.g., `git diff main -- shiny/www/shared/`) and ask if py-shinyswatch and/or py-shinywidgets need to be updated before proceeding

Ask the user: "Were any Shiny HTML Dependencies updated or added in this release cycle? Here are the changed files: [show diff]. Does py-shinyswatch or py-shinywidgets need updating?"

---

## Phase 2: Release py-htmltools

Repo: `posit-dev/py-htmltools`

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/py-htmltools/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version

Follow the general package release pattern:

- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Verify `pyproject.toml` has no git-based dependencies
- [ ] Bump version in `htmltools/__init__.py`
- [ ] Bump version in changelog
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, CI status, changelog, dep check) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Create GH Release (copy changelog content, mark as Latest)
- [ ] Wait for PyPI publish to succeed

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
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, CI status, changelog, dep check, shinylive test results) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Create GH Release (copy changelog content, mark as Latest)
- [ ] Wait for PyPI publish to succeed

### Shinylive example testing procedure

Dynamically retrieve the current example list and test each app:

1. Fetch the example list from the GitHub API:
   ```bash
   gh api repos/posit-dev/shinylive/contents/examples/python \
     --jq '.[].name' | sort
   ```
2. The base URL for each example is:
   `https://posit-dev.github.io/py-shiny/shinylive/py/examples/#EXAMPLE_NAME`
3. For each example, use Playwright MCP tools to:
   a. Navigate to the example URL (`browser_navigate`)
   b. Wait for the app to load (`browser_wait_for` - wait for the shinylive app iframe or output to appear)
   c. Check browser console messages (`browser_console_messages`) for Python errors/tracebacks
   d. Record the result (pass/fail + any error text)
4. After visiting all examples, present a summary table:
   ```
   | Example | URL | Status | Errors |
   |---------|-----|--------|--------|
   | basic_app | <link> | OK | - |
   | cpuinfo | <link> | ERROR | TypeError: ... |
   ```
5. If any apps have errors, present the broken app links prominently for user verification:
   ```
   Broken apps found (please verify manually):
   - cpuinfo: https://posit-dev.github.io/py-shiny/shinylive/py/examples/#cpuinfo
     Error: TypeError: ...
   ```

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

- [ ] **Confirm version**: Look up the current version (`gh api repos/posit-dev/shinylive/releases/latest --jq .tag_name`), suggest the next minor bump, and ask the user to confirm the release version
- [ ] Checkout branch `rc-vX.Y.Z`
- [ ] Bump version in `package.json`
- [ ] Run `make submodules submodules-pull-shiny` to init all submodules and then update py-shiny submodule
- [ ] Run `make clean && make all`
- [ ] Check `shinylive_lock.json` for released package versions
- [ ] Add and/or edit examples to use new features or API
- [ ] Run `make serve` and automatically test all local shinylive examples for errors (see procedure below)
- [ ] Commit and push
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, submodule versions, build output) and get explicit user confirmation before tagging
- [ ] Tag commit and push tag
- [ ] Push to `main` branch (for github.io)
- [ ] After deploy to github.io finishes, test apps on github.io using the same Playwright-based example testing procedure
- [ ] Only after github.io apps pass: push to `deploy` branch (for shinylive.io)
- [ ] After deploy to shinylive.io finishes, test apps on shinylive.io
- [ ] Create GH Release
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
- [ ] Bump version of the package
- [ ] Bump version of the shinylive (JS) bundle dependency
- [ ] Update changelog
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Verify no additional commits were added beyond release prep
- [ ] **PRE-RELEASE GATE**: Present release summary (package, version, shinylive JS version, changelog) and get explicit user confirmation before proceeding
- [ ] Squash merge the RC PR into main via GitHub (this is the release commit)
- [ ] Tag the squash commit on main: `git checkout main && git pull && git tag vX.Y.Z && git push origin vX.Y.Z`
- [ ] Create GH Release
- [ ] Wait for PyPI publish to succeed

If PyPI fails, delete tag and release, fix, redo.

Ask user: "Is py-shinylive being released this cycle?"

---

## Phase 8: Update r-shinylive

Repo: `posit-dev/r-shinylive`

Use the shinylive JS version from Phase 6 (already known at this point).

- [ ] Check for any existing open PRs that bump `SHINYLIVE_ASSETS_VERSION` (`gh pr list --repo posit-dev/r-shinylive --state open --search "SHINYLIVE_ASSETS_VERSION"`). If found, close them.
- [ ] Create a branch with the `SHINYLIVE_ASSETS_VERSION` update to the Phase 6 shinylive JS version
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR

---

## Phase 9: Update py-shiny (post-release)

Repo: `posit-dev/py-shiny`

- [ ] Create a branch to bump shinylive `[docs]` version to the latest py-shinylive release
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

- [ ] Check `conda-forge/py-htmltools-feedstock` for auto-created PR from bot
- [ ] Check `conda-forge/py-shiny-feedstock` for auto-created PR from bot
- [ ] If PRs exist and tests pass, they should auto-merge
- [ ] If auto-merge doesn't happen, create an issue with the appropriate bot command

Ask user: "Have the conda-forge bot PRs appeared? Any issues with auto-merge?"

---

## Phase 12: Huggingface

Repo: https://huggingface.co/spaces/posit/shiny-for-python-template

- [ ] Update `requirements.txt` with new package versions

---

## Phase 13: Publish blog post

Repo: shiny-dev-center

- [ ] Write or finalize the release blog post
- [ ] Open PR for review
- [ ] Merge and publish

Ask user: "The blog post should be written in a fresh Claude session to avoid context bloat from this release skill. Please start a new session and use `/release-post` to draft the blog post. Let me know when it's done so we can mark this phase complete."
