# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

py-shiny is a Python web framework for building reactive web applications. It maintains feature parity with Shiny for R, often porting UI components from the R bslib package. The codebase consists of Python server-side code, TypeScript/JavaScript client-side code, and vendored assets from upstream packages.

## Development Commands

### Essential Commands
```bash
# Install dev dependencies (requires Python 3.10+)
pip install -e ".[dev,test,doc]"
pre-commit install       # Optional: auto-format/lint on commit

# Format code (always run before committing)
make format              # Auto-fix with black and isort
make check-format        # Check only
make check-lint          # Lint with flake8

# Type checking
make check-types         # Run pyright (requires typings)

# Run tests
make test                # Unit tests only (pytest)
pytest tests/pytest/test_foo.py::test_name  # Single unit test
make playwright          # All end-to-end tests (slow)
make playwright-shiny SUB_FILE="inputs/test_foo.py"  # Single test

# Comprehensive checks
make check               # Format, lint, types, unit tests
make check-fix           # Same but auto-fixes formatting
```

### Running Apps
```bash
shiny run app.py --reload --launch-browser  # Dev server with auto-reload
SHINY_LOG_LEVEL=DEBUG shiny run app.py      # Verbose logging
```

### Asset Management

See `.claude/references/assets.md` for details.
```bash
# Vendor assets from upstream (bslib, shiny, sass, htmltools)
make upgrade-html-deps   # Requires R installed

# Build JavaScript/TypeScript
make js-build            # One-time build
make js-watch            # Continuous rebuild
```

### Testing Shortcuts
```bash
# Update test snapshots
make test-update-snapshots

# Debug Playwright tests (headed, chromium only)
make playwright-debug TEST_FILE="tests/playwright/shiny/inputs/test_foo.py"

# Show trace of failed Playwright tests
make playwright-show-trace

# Run specific test suites
make playwright-shiny     # Tests in tests/playwright/shiny/
make playwright-examples  # Tests in tests/playwright/examples/
```

## Architecture

See `.claude/references/architecture.md` for the full guide. Topic summaries:

- **Reactive system** (`shiny/reactive/`): push-pull model. `Value` is the source,
  `Calc_` a cached computed value, `Effect_` a side-effect. A per-execution `Context`
  records dependencies automatically; the `ReactiveEnvironment` singleton manages the
  graph and flush cycles
- **Sessions** (`shiny/session/`): each WebSocket connection gets an `AppSession`;
  `get_current_session()` / `session_context()` manage the active session context
- **Express vs Core**: Core is explicit UI construction + a server function. Express
  rewrites the app via AST transformation at import time (`shiny/express/_run.py`,
  `_node_transformers.py`) and lays out UI in execution order
- **HTML/assets**: UI functions return `htmltools` `Tag`/`TagList` objects with
  attached HTML dependencies; bslib CSS/JS/SCSS is vendored under `shiny/www/shared/`
  via `make upgrade-html-deps`
- **Input/output bindings**: TypeScript input bindings send values via
  `Shiny.setInputValue()`; renderers push output over the WebSocket; server-initiated
  updates go through `session.send_input_message()`
- **Modules** (`shiny/module.py`, `shiny/_namespaces.py`): `@module.ui` /
  `@module.server` namespace IDs; `resolve_id()` applies the namespace stack
- **Testing**: unit tests in `tests/pytest/` (pytest + syrupy snapshots); end-to-end
  tests in `tests/playwright/` driven by controller classes from
  `shiny/playwright/controller/`
- **JS build** (`js/`): esbuild via `js/build.ts` outputs to
  `shiny/www/shared/py-shiny/`; rebuild (`make js-build` / `js-watch`) to see changes

## Key Files

### Core Python Files
- `shiny/_app.py` - App class and entry point
- `shiny/session/_session.py` - Session hierarchy (AppSession, SessionProxy)
- `shiny/reactive/_core.py` - Reactive system (Context, Dependents, ReactiveEnvironment)
- `shiny/reactive/_reactives.py` - Reactive primitives (Value, Calc_, Effect_)
- `shiny/express/_run.py` - Express mode execution
- `shiny/express/_node_transformers.py` - AST transformation for Express mode
- `shiny/render/renderer/_renderer.py` - Base renderer class
- `shiny/module.py` - Module decorators and namespacing

### Asset Management
- `.claude/references/assets.md` - Vendored bslib/shiny assets and the py-shiny JS bundle (key files, commands, pitfalls)

### Configuration
- `pyproject.toml` - Package config, dependencies, tool settings
- `pyrightconfig.json` - Pyright type checker configuration
- `pytest.ini` - Pytest configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration

### Documentation
- `.claude/references/documentation-style.md` - Docstring conventions, `@add_example()` workflow, quartodoc registration, docs build commands

## Important Patterns

### Component and Renderer Implementation

See `.claude/references/component-patterns.md` for the full checklists. In short:

- **UI components**: `shiny/ui/_component_name.py`; use `resolve_id()` (modules) and
  `restore_input()` (bookmarking); export from `shiny/ui/__init__.py` and
  `shiny/express/ui/__init__.py`; add example, controller, quartodoc entries, tests
- **Renderers**: inherit `Renderer[IT]`; implement `auto_output_ui()` plus either
  `transform()` (simple) or `render()` (full control); export from
  `shiny/render/__init__.py`. Do not use the deprecated `@output_transformer()`.
  Output components and renderers map 1:1 — add them as a pair

### Documentation Style

See `.claude/references/documentation-style.md` for the full guide. In short:

- **NumPy-style (numpydoc) docstrings** with dash-underlined sections; bare
  parameter names (no types) with indented descriptions; `Returns` uses a `:` placeholder
- Cross-reference API objects with Sphinx roles: `` :func:`~shiny.ui.update_slider` ``
- Input components document their server value in a `Notes` Quarto callout
- Attach runnable examples with `@add_example()` (apps in `shiny/api-examples/<name>/`
  as `app-core.py` + `app-express.py`), not inline `Examples` sections
- Register new public API in `docs/_quartodoc-*.yml` (alphabetical within sections)

### Type Checking Notes

- Pyright is the primary type checker (not mypy)
- Some packages require manual stubs: run `make pyright-typings` to generate
- Stubs are placed in `typings/` (gitignored)
- Parameter types: prefer `T | None` over `Optional[T]` when no default `None` value is provided
- Use `Literal` instead of `Enum` for string options

## Code Style Preferences

Beyond PEP 8 and standard Python conventions, the following style preferences are used in this codebase:

### Import Organization

- **Always place imports at the top of the file**, not inline within functions
- Group imports in standard order: stdlib, third-party, local relative
- Avoid lazy/deferred imports unless absolutely necessary for circular dependency resolution
- When moving inline imports to the top, update any test mocks to patch the new import location

### Parameter Naming

- Use **named arguments** for all parameters except the first positional parameter in function calls
- Choose descriptive parameter names that clarify intent:
  - Use `required_level` not `level` when the parameter represents a threshold/minimum
  - Use `collection_level` not `level` when the parameter represents a current setting
- Good: `with_otel_span("name", attributes=attrs, required_level=OtelCollectLevel.SESSION)`
- Bad: `with_otel_span("name", attrs, OtelCollectLevel.SESSION)`

### Constants and Magic Values

- Use constants for values that appear multiple times across the codebase
- Inline single-use attribute/configuration values directly at point of use
- Document constants with docstrings explaining their purpose

### Error Handling

- Be explicit about which exceptions are caught and why
- Use type-specific exception handling rather than broad `except Exception`
- Document exception behavior in function docstrings

## Git Commit and PR Conventions

See `.claude/references/commit-conventions.md` for the full guide. In short:
**conventional commits** for commit messages and PR titles
(`<type>: <Description>` — sentence case, present tense, ≤72 chars, no trailing
period). Types: feat, fix, docs, refactor, test, chore, perf, style.

## Porting from bslib

New Bootstrap components are developed in R's bslib package first, then ported here
(vendoring bslib's compiled assets rather than reimplementing them). For the complete
workflow — studying the bslib source, Python implementation, asset vendoring, tests,
and docs — use the `.claude/skills/port-from-bslib/SKILL.md` skill.

## Common Pitfalls

- **Forgetting to run `make format`**: Always format before committing
- **Missing HTML deps**: If styles don't work, ensure `components_dependencies()` is included
- **Express mode confusion**: Remember Express uses AST transformation; debugging requires understanding the transformed code
- **Session context errors**: Always access `input`/`output` within reactive context
- **Reactive graph debugging**: Use `reactive.flush()` to force synchronous execution in tests
- **Playwright timing**: Use `.expect_*()` methods which auto-wait; avoid manual `sleep()`
- **Asset updates**: After running `make upgrade-html-deps`, verify theme preset files were updated
