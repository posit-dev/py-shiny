---
title: "CI and Tooling"
description: "The dev toolchain (Makefile targets, uv, pyproject extras, type checkers, pre-commit) and the GitHub Actions workflows: what runs on PRs, matrices, Playwright sharding, deploy tests, docs build, and PyPI release. Read before changing the Makefile, pyproject dependencies, or .github/, or when a CI job fails and you need to know what it actually ran."
---

# CI and Tooling

The `Makefile` is the single entry point: CI workflows call `make` targets
rather than tools directly, so a target's behavior locally is what CI runs.
Merge policy and flaky-test handling live in
[commitConventions.md](commitConventions.md); this doc does not repeat them.

## Make targets

| Target | What it actually runs |
|---|---|
| `format` | `black .` then `isort .` |
| `check-format` | `black --check .` + `isort --check-only --diff .` |
| `check-lint` / `lint` | `flake8 --show-source .` (config in `[tool.flake8]`, via Flake8-pyproject) |
| `check-types` | **Pyrefly only** (`check-pyrefly` -> `pyrefly check`) |
| `check-pyright` / `pyright` | `pyright` (strict, `pyrightconfig.json`) |
| `update-pyrefly-baseline` | `pyrefly check --baseline pyrefly-baseline.json --update-baseline` |
| `check-tests` / `test` | `python tests/pytest/asyncio_prevent.py`, then `pytest` |
| `check` | `check-format check-lint check-types check-tests` |
| `check-fix` | same as `check` but runs `format` first |
| `typings` | Generates third-party stubs into `typings/` (see below) |
| `test-update-snapshots` | `pytest --snapshot-update` (syrupy) |
| `playwright` | `pytest` over `TEST_FILE` with all three browsers, per-test timeout, `--snapshot-warn-unused` |
| `playwright-shiny` / `-examples` / `-ai` / `-deploys` | `playwright` scoped to `tests/playwright/{shiny,examples,ai_generated_apps,deploys}/$(SUB_FILE)`; deploys is chromium only |
| `playwright-debug` | `pytest -c tests/playwright/playwright-pytest.ini` (chromium, headed, slowmo, `--maxfail=1`) |
| `playwright-show-trace` | `npx playwright show-trace` on newest `test-results/*/trace.zip` or `TRACE=` |
| `js-build` / `js-watch` | `npm install` + `npm run build`/`watch` in `js/` (see [assets.md](assets.md)) |
| `docs` / `docs-quartodoc` | `cd docs && make quartodoc` |
| `upgrade-html-deps` | `scripts/htmlDependencies.R` (requires R) |
| `update-testing-docs` | `docs` + repomix + `process_docs.py` -> `shiny/pytest/_generate/_data/testing-documentation.json` |
| `dist` / `release` | `clean`, `python -m build` sdist + wheel; `release` adds `twine upload` |

`ci-*` targets are the `uv pip` variants CI uses: `ci-install-deps`
(`-e ".[dev,test]"`), `ci-install-wheel` (`uv build`, then install the wheel
over the editable install), `ci-install-docs` (adds `doc` extra + shinylive
from GitHub), `ci-install-rsconnect`, `ci-install-ai-deps`,
`ci-check-mypy-can-run`.

Playwright knobs (Makefile variables): `SUB_FILE`, `TEST_FILE`,
`PYTEST_BROWSERS`, `PYTEST_EXTRA_ARGS` (e.g. `"--tracing on"`),
`PLAYWRIGHT_TEST_TIMEOUT=120` with `--timeout-method=thread` and
`faulthandler_timeout=110` (dumps stacks before the kill). `-v` is added only
when `CI=true`. `install-playwright` skips `playwright install` entirely when
`PW_TEST_CONNECT_WS_ENDPOINT` is set (remote browser server).

## Type checking: Pyrefly and Pyright

- Two checkers coexist during a migration. `check-types` runs Pyrefly only;
  Pyright runs only via `make check-pyright` and the separate `pyright` CI job.
  Run both before pushing.
- `[tool.pyrefly]` in `pyproject.toml`: `permissive-ignores = true` (so
  `# pyright: ignore` comments also silence Pyrefly), `unused-ignore` and
  `implicit-any` are errors, `site-package-path = ["typings"]`, and a
  `tests/playwright/**` sub-config that treats `conftest` imports as `Any`.
- `pyrefly-baseline.json` holds accepted pre-existing errors; it is currently
  empty (`"errors": []`). Only regenerate it with `make update-pyrefly-baseline`
  after intentionally fixing (not adding) errors.
- `pyrightconfig.json`: strict mode, `pythonPlatform: All`, and the same
  ignore list as Pyrefly's `project-excludes` (keep them in sync).
- mypy is not a checker here: `[tool.mypy] ignore_errors = true`;
  `ci-check-mypy-can-run` only proves mypy doesn't crash on `shiny/`.

### Stubs (`typings/`)

Both `check-pyrefly` and `check-pyright` depend on `typings`, which builds
gitignored stubs: `pyrefly stubgen --include-private` for folium, uvicorn, and
seaborn; matplotlib stubs are `git clone`d from
`microsoft/python-type-stubs` (needs network). These are file targets, so they
are built once and never refreshed; `make clean-test` deletes `typings/`.

## uv and why `uv run make ...`

- There is no committed lockfile (`/uv.lock` is gitignored) and no
  `[dependency-groups]`; dev tooling lives in the `dev` extra with version
  floors (`black>=26.1.0`, `pyrefly>=1.2.0`, `pyright>=1.1.407`, ...).
- `uv run make format check-lint check-types` puts the project `.venv/bin` on
  `PATH`, so `make` picks up the venv's black/isort/flake8/pyrefly instead of
  whatever is on the system `PATH`. A stale system black can miss a new
  target-version rule that CI's fresh install enforces. Install the venv with
  `uv pip install -e ".[dev,test,doc]"`.
- CI installs with `astral-sh/setup-uv` (`activate-environment: true`, cache
  keyed on `pyproject.toml` + Python version) inside the composite action
  `.github/py-shiny/setup`, which runs `ci-install-deps` then
  `ci-install-wheel`. Default Python there is 3.14.

## pyproject extras

- Runtime deps include `narwhals>=2.26.0` (data frame abstraction); pandas and
  polars are not runtime deps.
- `theme` (libsass, brand_yml), `otel` (opentelemetry-sdk/distro).
- `test`: pytest + plugins (asyncio, playwright, xdist, shard, timeout,
  rerunfailures, cov), syrupy, and many app deps used by examples/tests
  (polars, dask, pyarrow, plotly, seaborn, shinywidgets, logfire, ...).
- `dev`: formatters/linters/type checkers, pre-commit, pandas + pandas-stubs,
  polars, numpy, matplotlib, chatlas.
- `doc`: quartodoc, griffe `<2.0.0`, shinylive, jupyter.
- `add-test`: AI test generator deps (inspect-ai, openai, anthropic).

## pytest configuration

- `pytest.ini`: `testpaths=tests/pytest/`, `--numprocesses auto`,
  `asyncio_mode=strict`, and `filterwarnings = error` (any stray warning fails
  a test; add narrow third-party ignores there, assert expected ones with
  `pytest.warns()`).
- `tests/pytest/asyncio_prevent.py` runs in a clean process before pytest to
  ensure importing shiny never touches the event loop.
- Retries are opt-in per test via `@pytest.mark.flaky(...)`
  (pytest-rerunfailures), mostly under `tests/playwright/`; deploy tests use
  `reruns = 3` in CI (`tests/playwright/utils/deploy_utils.py`).

## Pre-commit

`.pre-commit-config.yaml` runs only `black` (rev 26.1.0). It does not run
isort, flake8, or any type checker.

## GitHub Actions workflows

| Workflow (file) | Triggers | What it does |
|---|---|---|
| Run tests (`pytest.yaml`) | PRs, push to `main`/`rc-*`, release published, nightly cron, dispatch | Main suite; jobs below |
| Build API docs (`build-docs.yaml`) | PRs, push to `main`/`docs-**`, dispatch | PRs: quartodoc only. `main`: + shinylive build, `docs` site, GitHub Pages deploy. `docs-**`: full build, no deploy |
| Run deploy tests (`deploy-tests.yaml`) | push to `main`/`rc-*`/`deploy-**`, dispatch (not PRs) | Deploys apps to a local Posit Connect (`posit-dev/with-connect`, license secret) across 4 shiny/rsconnect source combos; `concurrency` serializes each config |
| Verify built assets (`verify-js-built.yaml`) | PRs, push to `main`/`rc-*` | `npm ci && npm run build` in `js/`; fails on any diff |
| Conventional Commits (`verify-conventional-commits.yaml`) | PR opened/edited/sync | Lints the PR title; sticky comment on failure |
| Verify testing docs (`verify-testing-docs-on-change.yml`) | PRs touching `shiny/playwright/controller/**` or `docs/_quartodoc-testing.yml` | Reruns `make update-testing-docs`; comments and fails if the JSON changed |
| Verify test generation prompts (`verify-test-generation-prompts.yaml`) | PRs touching `shiny/pytest/_generate/**`, dispatch | LLM eval of `shiny add test` (3 attempts, quality gate); needs OpenAI/Anthropic secrets |
| Issue Management (`triage-issues.yaml`) | issue opened | Adds `needs-triage` for non-maintainers |

### Jobs in `pytest.yaml`

- `check`: Python 3.10-3.14 x ubuntu/windows/macOS. Steps: `check-tests`,
  `check-types` (not Windows), `check-lint`, `check-format`,
  `ci-check-mypy-can-run` (not Windows). Each step runs even if an earlier one
  failed.
- `pyright`: single run, ubuntu, Python 3.13, `make check-pyright`.
- `oldest-deps`: Python 3.10, `uv pip compile --resolution lowest-direct` of
  runtime + `theme`/`otel`, then `check-tests` (logfire skipped).
- `playwright-shiny`, `playwright-examples`: Python x {chromium, firefox,
  webkit} x 4 shards; `playwright-ai`: same with 2 shards. Each runs
  `--numprocesses 3 --num-shards N --shard-id K` (pytest-shard) with a
  10-minute step timeout ("healthy shards finish in ~4 minutes").
  `playwright-examples` also checks out `posit-dev/py-shiny-templates` and
  `npm ci`s `examples/brownian/shinymediapipe`.
- `playwright-deploys-precheck`: Python 3.10, runs deploy tests locally with
  `DEPLOY_APPS=false` (no Connect).
- `test-narwhals-integration`: Python 3.12, via composite actions
  `.github/py-shiny/narwhals-setup` and `narwhals-test`, which run
  `make narwhals-test-integration` (`check-types check-tests` + the
  `tests/playwright/shiny/components/data_frame/data_type/` Playwright tests on
  chromium). These actions take a `shiny-dir` input so narwhals' own CI can
  reuse them against a py-shiny checkout.
- `pypi`: only on `release` events, `needs: [check]`. Builds with `make dist`
  on Python 3.10; release name starting `TEST` -> TestPyPI, starting `shiny` ->
  PyPI. Release events skip every other job except `check`.
- `pr-gate` ("PR checks"): fans in every job above; the required status check.

**Draft PRs** run a reduced matrix: `check` on Python 3.14 + ubuntu only;
Playwright jobs on 3.14 + chromium only. Marking ready for review reruns the
full matrix.

**Playwright in CI** never installs browsers on the runner:
`.github/py-shiny/setup-playwright-remote` starts a `playwright run-server`
Docker container (image mirrored to GHCR with the npm package baked in,
falling back to MCR) and exports `PW_TEST_CONNECT_WS_ENDPOINT`. The Playwright
image version tracks the installed Python `playwright` package. Jobs using it
need `permissions: packages: write`.

`.github/py-shiny/check` is a composite version of the `check` steps kept for
py-htmltools' CI; keep it in sync when changing what `check` runs.

## Slow or flaky spots

- Playwright matrices are the bulk of CI (60 + 60 + 30 jobs on a full PR).
- MCR image pulls are intermittently blocked for Actions runners (retried 5x
  in `setup-playwright-remote`); a cold GHCR cache adds an image build.
- Deploy tests wait on external Connect deploys (30-minute step timeout) and
  carry `@pytest.mark.flaky` reruns.
- `verify-test-generation-prompts` is LLM-nondeterministic and fails on fork
  PRs without API-key secrets.

## Pitfalls

- `make check-types` does **not** run Pyright.
  CI's `pyright` job will still fail you; run `make check-pyright` too.
- Stale `typings/` stubs persist across dependency upgrades; `make clean-test`
  then rerun the type check to regenerate.
- `check` in CI skips type checking (and the mypy smoke test) on Windows.
- Playwright CI shards pass `--snapshot-warn-unused`; locally a sharded or
  single-browser run with plain `pytest` can error on "unused snapshots". Never
  `--snapshot-update` to silence it except from an all-browser, unsharded run.
- `filterwarnings = error` means a new upstream `DeprecationWarning` can break
  unrelated unit tests overnight (nightly cron catches these first).
- Adding a job to `pytest.yaml` without listing it in `pr-gate.needs` means its
  failures won't block merges. Workflows outside `pytest.yaml` are not part of
  the gate.
- Committed JS bundles must match a fresh `npm ci && npm run build` with the
  Node version in `js/.nvmrc`, or `verify-js-built` fails.
- After changing a Playwright controller, run `make update-testing-docs` and
  commit `shiny/pytest/_generate/_data/testing-documentation.json`, or
  `verify-testing-docs-on-change` fails. `docs/api/` is gitignored, so the
  Makefile's `repomix` call needs `--no-gitignore`; without it, newer repomix
  packs zero files and the JSON becomes `[]`.
- A workflow's own `paths` filter must use its exact filename (`.yml` vs
  `.yaml`), or editing only the workflow won't trigger it.
- `oldest-deps` installs runtime deps at their declared floors, so code using
  an API newer than a floor fails there first: raise the floor in
  `pyproject.toml` (or make the test skip when the dep is absent, as the
  logfire tests do).
