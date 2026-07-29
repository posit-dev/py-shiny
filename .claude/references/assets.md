# Asset Management

py-shiny ships two kinds of client-side assets:

1. **Vendored assets** from upstream packages (bslib, shiny, sass, htmltools),
   pulled in by an R script.
2. **py-shiny's own TypeScript bundle**, built from `js/` with esbuild.

## Vendored upstream assets

```bash
make upgrade-html-deps   # Requires R installed
```

This runs `scripts/htmlDependencies.R`, which vendors compiled assets from the
upstream R packages into the repo:

- SCSS source files from bslib: `shiny/www/shared/sass/bslib/components/scss/`
- Compiled CSS for all theme presets: `shiny/www/shared/sass/preset/` (27 files)
- bslib JavaScript bundle: `shiny/www/shared/bslib/components/components.min.js`
- Upstream package versions are recorded in `shiny/_versions.py`

Related files:

- `shiny/ui/_html_deps_*.py` — `HTMLDependency` definitions that attach these
  assets to UI components
- `components_dependencies()` — returns the bslib component dependencies; a
  component whose styles don't load is usually missing this

**Pitfall**: after running `make upgrade-html-deps`, verify the theme preset
files under `shiny/www/shared/sass/preset/` were actually updated — a partial
run can leave presets stale.

## py-shiny TypeScript bundle

Client-side code is in `js/`:

- Entry point: `js/src/shiny/index.ts`
- Build tool: esbuild via `js/build.ts`
- Output: `shiny/www/shared/py-shiny/shiny.js` and minified variant, with
  source maps for debugging
- TypeScript definitions for Python-JS interop

```bash
make js-build        # One-time build (npm install runs automatically)
make js-watch        # Continuous rebuild on change
make js-watch-fast   # Continuous rebuild, skipping lint and minification
```

Changes to `js/src/` are invisible to Python apps until rebuilt — the apps load
the committed bundle from `shiny/www/shared/py-shiny/`.

## When assets come from bslib

New Bootstrap components are developed in the R bslib package first and ported
here; the port vendors bslib's compiled JS/CSS rather than reimplementing it.
See `.claude/skills/port-from-bslib/SKILL.md` for that full workflow.
