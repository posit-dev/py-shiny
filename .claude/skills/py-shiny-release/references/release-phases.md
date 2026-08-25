# Release Phases - Detailed Steps

## Phase 1: Prerequisites

- [ ] Check if any Shiny HTML Dependencies were updated or added. A quick signal is
      `git diff v<PREV>..origin/main -- shiny/_versions.py shiny/www/` — a bumped
      `shiny_html_deps` plus changes under `shiny/www/shared/sass/` means the theme
      presets moved.
- [ ] If yes, show the user which files changed (e.g., `git diff main -- shiny/www/shared/`) and ask if py-shinyswatch and/or py-shinywidgets need to be updated before proceeding

**py-shinyswatch is almost always affected, and the answer is Phase 4, not Phase 1.**
shinyswatch *commits* pre-built CSS — `shinyswatch/bsw5/<theme>/bootswatch.min.css`, 26
files — compiled from shiny's own theme presets by `scripts/update_themes.py`. Those files
go stale whenever shiny's preset SCSS changes, and the staleness is invisible: apps render,
just without the new component's styles.

Because the script compiles against the *installed* shiny, it can only run once the new
py-shiny is on PyPI. So nothing blocks Phase 3 — but plan on a shinyswatch release in
Phase 4 whenever the presets moved.

To confirm whether a regeneration is actually needed, grep the committed CSS for a selector
that the new shiny release added, e.g.:

```bash
# 0 matches in shinyswatch => stale
gh api repos/posit-dev/py-shinyswatch/contents/shinyswatch/bsw5/darkly/bootswatch.min.css \
  --jq '.content' | base64 -d | grep -c "offcanvas-footer"
```

py-shinywidgets does **not** vendor shiny SCSS, so it is usually unaffected.
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

Follow the general package release pattern (same as Phase 2), plus the theme regeneration
below when Phase 1 found that shiny's presets moved.

### Regenerating the pre-built themes

Must happen **after** the new py-shiny is on PyPI — the script compiles against the
installed shiny.

- [ ] Install the *released* shiny plus shinyswatch's dev extras into a venv. The extras
      matter: `scripts/update_themes.py` imports `black` and `sass`, and
      `scripts/get_theme_values.py` imports `tinycss2`. All are declared under
      `[options.extras_require] dev` in `setup.cfg`, so `pip install -e ".[dev]"` is the
      right move — a hand-rolled minimal venv will fail **partway through**, after all 26
      CSS files are already written but before `_bsw5.py`/`theme.py` are regenerated, which
      looks deceptively like a successful run.
- [ ] Run `make update-bootswatch` (= `python3 scripts/update_themes.py`)
- [ ] **Verify the regeneration actually took**, by grepping the regenerated CSS for a
      selector the new shiny release added — do not assume the script worked:

      ```bash
      # expect this to go from 0 -> 1, in every theme
      for f in shinyswatch/bsw5/*/bootswatch.min.css; do
        grep -c "offcanvas-footer" "$f" | grep -q '^0$' && echo "MISSING: $f"
      done
      ```

      `git status` should show ~26 modified `bootswatch.min.css` files. `_bsw5.py` and
      `theme.py` change only when the theme list or Bootstrap version changed.
- [ ] Bump `__version__` in `shinyswatch/__init__.py` (`setup.cfg` resolves the version
      from this attribute via `version = attr:`, so this is the real bump)
- [ ] Raise the shiny floor in `setup.cfg` (`install_requires`) to the new release
- [ ] `CHANGELOG.md`: follow the established wording — "Update pre-built shinyswatch themes
      for use with Shiny vX.Y.Z." — plus a line noting the new shiny floor

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
- [ ] **Update the PyPI-sourced pins by hand** — see "The `latest` trap" below. At minimum
      check `shinyswatch`, which tracks a py-shiny release of its own.
- [ ] Run `make clean && make all`
- [ ] **Verify `shinylive_lock.json`** — check that ALL package versions match their latest releases. The lockfile reflects what's actually bundled. Don't trust that updating one submodule will cascade to others.
- [ ] Cross-check the built wheels: `ls build/shinylive/pyodide/*.whl` should show the
      expected versions of shiny, shinyswatch, htmltools, shinywidgets and faicons.
- [ ] Run `npm install --package-lock-only` to sync `package-lock.json` version with `package.json`
- [ ] **Grep the bundled examples for anything the new py-shiny deprecated** — see
      "Deprecations break the bundled examples" below.

### Deprecations break the bundled examples

A py-shiny release that deprecates a renderer or UI function will make any shinylive example
still using it print a `ShinyDeprecationWarning` on load, and `examples-smoke-test` fails on
that: `SUSPECT_PATTERNS` in `playwright/examples-smoke-helpers.ts` matches `/Warning\b/` and
`/Deprecat/i` in the shinylive terminal.

So for every entry in the new release's **Deprecations** changelog section:

```bash
grep -rn "render\.download\|<other deprecated API>" examples/ export_template/ site_template/
```

Migrate what turns up, in the release PR. (In v1.7.0, `examples/python/file_download_core`
used `@render.download` three times and had to move to `@render.download_button`.)
`export_template/` and `site_template/` matter too — they ship to users. Ignore hits under
`_shinylive/py`, `_shinylive/r`, `venv/`, `build/` and `packages/`: those are build output or
submodules.

### The `latest` trap: PyPI pins do not update themselves

`shinylive_requirements.json` marks some packages `{"source": "pypi", "version": "latest"}`.
**`make all` will not move them.** It runs `update_packages_lock_local`, which filters the
requirements down to `source: "local"` and then merges into the existing lockfile — PyPI
entries are carried over verbatim and never re-resolved. `"latest"` means "latest as of the
last full regen". This is how `shinyswatch` sat at 0.8.0 (April 2023) until shinylive#235
noticed, two and a half years later.

The obvious fix is unavailable: a full `make update_packages_lock` is **broken** — see
[shinylive#233](https://github.com/posit-dev/shinylive/issues/233). It moves ~28 packages
and yields a lockfile that fails at runtime with
`No known package with name 'jupyterlab_widgets'`, breaking every shinywidgets app. **Do not
run it** as part of a release.

Instead, edit the single entry, generating it with the repo's own helper so field order and
formatting match the file (this also pulls the package's real dependency specs from PyPI, so
e.g. a raised `shiny>=` floor comes along automatically):

```bash
python -c "
import sys, json; sys.path.insert(0, 'scripts')
import pyodide_packages as pp
print(json.dumps(pp._get_pypi_package_info('shinyswatch', 'latest'), indent=2))
"
```

Splice `version`, `filename`, `sha256`, `url` and `depends` into the existing block, keeping
the file's compact one-line-per-dependency style. Expect a ~5-line diff. Re-verify after
`make all` that the edit survived (it should — the local pass does not disturb it).

Harmless finding, so don't chase it: `build/shinylive/pyodide` will contain a couple of
wheels not referenced by `pyodide-lock.json` (e.g. `anyio`, `narwhals`). Those are pyodide's
own upstream versions, which shinylive's older pins override in the merged lock. Both files
land on disk; only the pinned ones load. Missing `*-tests.tar` entries are likewise expected.

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
- [ ] **Confirm the deployed bundle is actually the new one** before reading the sweep results.
      A stale CDN response passes the sweep while proving nothing, so check the served
      lockfile rather than assuming:

      ```bash
      curl -s "https://posit-dev.github.io/shinylive/shinylive/shinylive_lock.json?v=$(date +%s)" \
        | python -c "import json,sys; d=json.load(sys.stdin); print(d['shiny']['version'], d['shinyswatch']['version'])"
      ```

      Tell the user which surface is live and which is not at this point — github.io is
      staging; shinylive.io is untouched and still serving the previous release.
- [ ] Ask user: "github.io apps have been tested — X passed, Y failed. Ready to push to `deploy` (shinylive.io)?" Get explicit confirmation.
- [ ] Only after github.io verification passes and user confirms: push to `deploy` branch (for shinylive.io) using `git push origin main:deploy`
- [ ] **DEPLOY GATE 2 (shinylive.io)**: Wait for the `deploy` branch deploy to shinylive.io to finish. Then bust all browser caches and verify apps work on shinylive.io using the same testing procedure with cache-busting (fresh incognito context or `?v={timestamp}` query params).
- [ ] Create GH Release. Check existing release note conventions (`gh api repos/posit-dev/shinylive/releases --jq '.[:3] | .[] | .body'`) and match the format used by recent releases.
- [ ] Wait for release to succeed and build artifact to appear in GH Release page
- [ ] Confirm the artifact really uploaded — `gh release view vX.Y.Z --repo posit-dev/shinylive
      --json assets` should show `shinylive-X.Y.Z.tar.gz` with `state=uploaded` (it is ~435 MB,
      so it appears a while after the release object does). Phases 7 and 8 pin this as
      `SHINYLIVE_ASSETS_VERSION`, so a missing artifact blocks both.
- [ ] **Clean up**: kill the `make serve` dev server this phase started (port 3000) and confirm
      the port closed. See "Clean up background processes at the end of each phase" in
      `SKILL.md`.

### Local shinylive example testing procedure

**Run the repo's own smoke suite — `test_shinylive_site.py` is not a substitute for it.**

```bash
make examples-smoke-test                       # everything
npx playwright test --config playwright-examples.config.ts --project=py
npx playwright test --config playwright-examples.config.ts --project=py -g "File download"
```

`examples-smoke.spec.ts` asserts three things per example: no suspect lines in the shinylive
**terminal**, no `.shiny-output-error` in the app frame, and no browser console errors. The
release skill's `test_shinylive_site.py` only covers console errors plus tracebacks in the app
iframe — it has no notion of the terminal pane, so it will happily pass a bundle whose
examples emit deprecation warnings on load. That exact gap let a broken bundle look clean
during the v1.7.0 train; only `examples-smoke-test` caught it.

Expect one fewer test than there are examples: the `Non-Apps` category holds entries that load
a plain script into the editor and never start an app, and `exampleAppTitles()` filters them
out (`NON_APP_CATEGORIES`). In v1.7.0 that was 27 tests for 28 examples.

**The smoke test reads `_shinylive/`, not `build/`.** `readExamplesJson()` loads
`_shinylive/<engine>/shinylive/examples.json` and the config serves that directory on port
8100. So after editing an example, `make all` is not enough — run `make _shinylive`
(`rm -rf _shinylive/py _shinylive/r` first for a clean rebuild) or the suite will keep testing
the old copy and appear not to have fixed anything.

`test_shinylive_site.py` is still useful as a quick check against a running dev server. Note
the local URL layout differs from the deployed one: `make serve` binds **port 3000** and serves
examples at **`/examples/`** — `/py/examples/` exists only on the deployed site and 404s
locally. Root serves `/app/`, `/editor/`, `/examples/` and `/shinylive/`.

```bash
python references/test_shinylive_site.py "http://localhost:3000/examples/"
```

Sanity check the example counts against `examples/index.json`:

```bash
python -c "
import json; d = json.load(open('build/shinylive/examples.json'))
[print(e['engine'], sum(len(c['apps']) for c in e['examples'])) for e in d]
"
```

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
  - Bump `Version` in `DESCRIPTION` to the next dev version (e.g., `0.4.1.9000`) — **only if
    it is not already a dev version**. If it already ends in `.9000` there is nothing to do,
    and the NEWS entry goes under the existing `# shinylive (development version)` heading.
  - Add a `NEWS.md` entry noting the assets update. Match the established wording, which
    links the release and calls out what changed for R users — usually whether the bundled
    webR moved, since a py-shiny-only bump does not affect R apps.
- [ ] Commit, push, open PR
- [ ] Wait for CI to pass
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR (squash merge)

**This does not ship to users.** r-shinylive releases through CRAN, so a dev-version assets
bump reaches R users only at its next CRAN release. Say so when reporting the phase complete,
or it reads as though the R side is live like the PyPI packages are.

**Note the assets version may skip releases.** If a shinylive version was cut but never
deployed to shinylive.io (see the note on v0.10.13), r-shinylive will be behind by more than
one. Bump to the current one and mention the skip in the PR body.

### A formatter bot may push to your PR branch

`r-shinylive` runs an `air format` workflow that commits fixes directly to PR branches. Two
consequences:

1. Your PR can pick up an **unrelated** formatting change (a pre-existing violation elsewhere
   in the package). Harmless, but mention it in the squash-merge body so it does not look like
   part of the release change.
2. Because the push is from a bot, GitHub gates the resulting workflow run as
   `action_required` with **zero jobs**. This makes `gh pr checks` report
   *"no checks reported on the branch"* and the PR show `mergeStateStatus: BLOCKED`, which
   looks exactly like CI never ran — when in fact it passed on your commit.

Diagnose by listing runs with their SHAs rather than trusting the PR-level view:

```bash
gh run list --repo posit-dev/r-shinylive --limit 5 \
  --json databaseId,status,conclusion,headSha,event
gh pr view <N> --repo posit-dev/r-shinylive --json headRefOid   # compare
```

Then approve the gated run so checks report against the new head:

```bash
gh api -X POST repos/posit-dev/r-shinylive/actions/runs/<RUN_ID>/approve
```

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

- [ ] Update the py-shiny submodule to point to the release tag. **Check how far behind it
      was** — if it lagged by more than one release, the PR also lands the intermediate ones,
      which is worth saying in the PR body (a skipped security patch especially).
- [ ] Update py-shinylive version in `requirements.txt`. Note this is an **exact** pin
      (`shinylive==0.8.11`), not a floor.
- [ ] Create a PR
- [ ] Use deployment preview to verify:
  - [ ] API docs are correct — especially pages for APIs the release added
  - [ ] Deprecations render as deprecated
  - [ ] Examples run properly. Embedded editors now execute the new shiny, so an example using
        a newly deprecated API will print a deprecation warning in the browser console.
- [ ] Ask user to confirm before merging the PR
- [ ] Merge PR

### Expect the doc-coverage test to fail when the release adds UI components

`components/test_ui_api_has_page.py::test_every_ui_export_has_a_page` asserts that every
`shiny.ui` / `shiny.express.ui` export is either documented or explicitly opted out. It
computes `API - DOCUMENTED - KNOWN_MISSING_COMPONENTS`, so **any new UI export fails the
`apps` job until a page exists**:

```
AssertionError: These shiny.ui / shiny.express.ui exports have no doc page:
  ['Offcanvas', 'hide_offcanvas', 'offcanvas', 'show_offcanvas', 'toggle_offcanvas'].
```

This is predictable rather than surprising: scan the release's **New features** changelog
section for new UI exports before opening the PR. Options are to write the `components/` page
and list the exports in its `relevant-functions` front-matter, or add them to
`KNOWN_MISSING_COMPONENTS` (`_TODO_NEEDS_COMPONENT_PAGE` is the bucket for "real component,
page not written yet"). Writing docs mid-release-train is usually out of scope, so the normal
outcome is to file an issue, get the user's sign-off, and merge with the failure — but surface
it rather than letting it look like an unexplained red check.

### The deploy preview URL is not posted as a comment

Nothing comments the Netlify URL on the PR. It follows the pattern
`https://pr-<N>--pyshiny.netlify.app`, and can be confirmed from the `deploy` job log:

```bash
gh api repos/posit-dev/py-shiny-site/actions/jobs/<JOB_ID>/logs | grep -a environment_url
```

### `main` requires an approving review

`required_approving_review_count: 1`, so `mergeStateStatus: BLOCKED` here usually means
"needs review", not "CI failed" — check which before reporting. Merging therefore needs either
a reviewer or, with the user's explicit approval, `gh pr merge --squash --admin`. If merging
with a known failure, record the failure and its tracking issue in the squash-merge body so
the history explains itself.

Ask user: "Ready to update the docs site? I'll help create the PR."

---

## Phase 11: Conda-forge

- [ ] Check each feedstock in the inventory below for an auto-created bot PR, for every
      package that was actually released in this train
- [ ] **Read the existing PRs' comments before investigating anything.** Prior cycles'
      analysis usually lives there, and re-deriving it wastes a lot of time.
- [ ] **Sync `recipe/meta.yaml`'s `run:` section by hand** — see below. The bot does not do
      this, and it is the usual reason a bump fails.
- [ ] Verify `about/license_file` against the new sdist, in both directions (below)
- [ ] If tests pass, `[bot-automerge]` lands it without help

### Feedstock inventory (verified 2026-08-25)

| conda package | Feedstock | Released in phase |
|---------------|-----------|-------------------|
| `htmltools` | `conda-forge/py-htmltools-feedstock` | 2 |
| `shiny` | `conda-forge/py-shiny-feedstock` | 3 |
| `shinyswatch` | `conda-forge/shinyswatch-feedstock` | 4 |
| `shinywidgets` | `conda-forge/shinywidgets-feedstock` | 5 |
| `shinychat` | `conda-forge/shinychat-feedstock` | — (own cadence) |
| `faicons` | `conda-forge/faicons-feedstock` | — (own cadence) |
| `shiny-validate` | `conda-forge/shiny-validate-feedstock` | — (own cadence) |

`shinychat`, `faicons`, and `shiny-validate` are not part of the release train, but if one of
them happened to be released alongside py-shiny or have an outdated feedstock, check its bot PR too.

Bump the feedstocks in dependency order — `htmltools` → `shiny` → (`shinyswatch`,
`shinywidgets`, `shinychat`) — because the downstream recipes' test phase imports `shiny`. A
downstream bump opened before `shiny` has landed will fail to solve; that is expected, so
leave it parked rather than trying to fix the recipe.

### Feedstocks pending creation (staged-recipes)

Until a `staged-recipes` PR merges there is no feedstock and no bot PR to check. Verify the
current state rather than trusting this list, then move anything that has landed into the
table above:

| conda package | staged-recipes PR |
|---------------|-------------------|
| `shinylive` | https://github.com/conda-forge/staged-recipes/pull/34628 |
| `querychat`, `chatlas` | https://github.com/conda-forge/staged-recipes/pull/34629 |
| `brand-yml` | https://github.com/conda-forge/staged-recipes/pull/34630 |

```bash
# 200 = on conda-forge, 404 = still pending
for p in shinylive querychat chatlas brand-yml; do
  printf "%-12s %s\n" "$p" \
    "$(curl -s -o /dev/null -w '%{http_code}' https://api.anaconda.org/package/conda-forge/$p)"
done
```

### The bot bumps the version; it does not add dependencies

This is the single biggest trap in this phase. A bot PR only changes `version`, `sha256` and
`build/number`, then re-renders. **Whenever py-shiny gains a runtime dependency, the recipe
must be updated by hand or the build fails in the test phase**, typically with a
`ModuleNotFoundError` for the new dep during `import shiny`.

This failure mode is silent across releases: the bot keeps opening PRs, each fails the same
way, and they get closed. In July 2026 the feedstock was found stuck on **1.4.0 since April
2025** — every bump from 1.5.0 onward had failed because `shinychat` (new in 1.5.0) and
`opentelemetry-api` (new in 1.6.0) were never added.

Compute the gap from PyPI metadata rather than reading `pyproject.toml` by eye:

```bash
curl -s https://pypi.org/pypi/shiny/<VERSION>/json -o /tmp/shiny.json
python - <<'EOF'
import json, re
d = json.load(open("/tmp/shiny.json"))
for r in (d["info"]["requires_dist"] or []):
    if "extra ==" not in r:
        print(" ", r)
EOF
```

Diff that against the recipe's `run:` list. Check for three things: **missing** deps, deps
that were **replaced** upstream (`appdirs` → `platformdirs`), and **floors that drifted**
behind `pyproject.toml`. py-shiny raises floors fairly often — its lowest-direct-resolution
CI job exists precisely to catch stale minimums, so its bounds move more than most packages'.

Also apply the linter's `noarch: python` hint if it appears: `run:` should use
`python >={{ python_min }}`, not `python {{ python_min }}`.

### Triggering a bot PR

If no bot PR exists (or you want one for a newer version), open an **issue** on the feedstock
titled exactly:

```
@conda-forge-admin, please update version
```

`conda-forge-webservices` replies with a link to the PR it opened. Note it works in two
stages — first a `dummy commit for rerendering`, then the real
`ENH: updated version to X.Y.Z & Re-rendered ...`. Between those, the PR looks like it only
touched `README.md`; wait for the second commit before concluding anything.

The bot stops issuing PRs when more than 3 of its version-bump PRs are open, so close
superseded ones.

### Pushing to a bot PR's branch

Bot branches live on the **bot's fork**, not the feedstock. Check `maintainerCanModify` (it is
normally `true`), then push to that remote explicitly:

```bash
gh pr view <N> --repo conda-forge/py-shiny-feedstock \
  --json maintainerCanModify,headRepositoryOwner,headRefName
git remote add bot https://github.com/conda-forge-admin/py-shiny-feedstock.git
git fetch bot <branch> && git checkout -B <branch> bot/<branch>
# ... edit recipe/meta.yaml ...
git push bot HEAD:<branch>
```

The owner is `conda-forge-admin` for webservice PRs and `regro-cf-autotick-bot` for autotick
PRs. `git fetch origin <branch>` fails with `couldn't find remote ref` — that is the giveaway
that you are looking at the wrong repo.

Current `recipe-maintainers`: `cpsievert`, `schloerke`, `wch`, `sugatoray` — so both Carson
and Barret can push directly. (Verify with the recipe's `extra/recipe-maintainers` rather
than trusting this list.)

### Known issue: license_file references

`about/license_file` lists bundled license files from py-shiny. Check it **both ways** against
the new sdist:

```bash
curl -sL "https://pypi.org/packages/source/s/shiny/shiny-<VERSION>.tar.gz" -o /tmp/s.tar.gz
# 1. every listed path must still exist -- a stale one fails the build with
#    `ValueError: License file ... does not exist`
tar tzf /tmp/s.tar.gz | grep -iE "LICENSE|COPYING" | sed 's|^shiny-<VERSION>/||'
```

- **Stale paths** (listed but gone, because a vendored dependency was removed or renamed)
  break the build.
- **Missing paths** (bundled in the sdist but not listed) do not break the build but are a
  licensing-compliance gap. In July 2026 `shiny/www/shared/busy-indicators/spinners/LICENSE`
  was bundled and unlisted.

### Bot PR timing

The conda-forge bot (`regro-cf-autotick-bot`) typically creates PRs within a few hours of a
PyPI release, but it can sometimes take up to a day. If no PR appears after 24 hours, check
the bot's [status page](https://github.com/regro/cf-scripts) for outages, or trigger one with
the issue command above.

### When a dependency is not on conda-forge at all

A new py-shiny dependency may have no conda-forge package. Then the feedstock cannot build
until someone submits it to
[`conda-forge/staged-recipes`](https://github.com/conda-forge/staged-recipes), which is a
separate review queue with its own latency. Check with:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://api.anaconda.org/package/conda-forge/<name>
```

A build in a personal anaconda.org channel does not count — conda-forge recipes may only
depend on conda-forge packages. When this happens, still push the corrected recipe (it will
fail to solve, which is expected and explainable) so that the only remaining action once the
dependency lands is a CI rerun.

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
