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

# Before opening a PR, run the checks through uv so the pinned toolchain is
# used (bare `make` may pick up a system black/isort/pyright with different
# versions and miss failures that CI catches, e.g. a py3.14 black target or a
# pyright error). This must pass:
uv run make format check-lint check-types
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

`.claude/references/architecture.md` explains how the internals work: the reactive
system, session hierarchy, Express vs Core mode, HTML generation and dependencies,
input/output bindings, the module system, testing architecture, and the JS build.
Read the relevant section before working on any of those areas.

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

Before implementing a UI component or output renderer, read
`.claude/references/component-patterns.md` — it has the step-by-step checklists
(file layout, exports, examples, controllers, tests) and the rules for pairing
output components with renderers.

### Bundled Agent Skills

The shiny package ships Agent Skills under `shiny/.agents/skills/` — reference
docs that teach coding agents how to use shiny's public APIs (debugging,
testing, etc.). Treat them like user-facing documentation: when a change
touches an API that a skill documents, update the skill in the same PR. Before
adding or editing a skill, read `.claude/references/agent-skills.md` for the
layout, frontmatter contract, content shape, scoping rules, and validation
steps.

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

Commit messages and PR titles use **conventional commits**. Read
`.claude/references/commit-conventions.md` for the format, types, and guidelines
before committing or opening a PR — and for the merge policy and flaky-test
handling before merging one.

Before creating a PR, confirm `uv run make format check-lint check-types`
passes. Run it through `uv run` (not bare `make`) so the pinned black/isort/
pyright versions are used — a system toolchain can silently miss failures that
CI then rejects.

## Common Pitfalls

- **Forgetting to run `make format`**: Always format before committing
- **Missing HTML deps**: If styles don't work, ensure `components_dependencies()` is included
- **Express mode confusion**: Remember Express uses AST transformation; debugging requires understanding the transformed code
- **Session context errors**: Always access `input`/`output` within reactive context
- **Reactive graph debugging**: Use `reactive.flush()` to force synchronous execution in tests
- **Playwright timing**: Use `.expect_*()` methods which auto-wait; avoid manual `sleep()`
- **Asset updates**: After running `make upgrade-html-deps`, verify theme preset files were updated
- **Stale bundled skills**: When changing a public API, grep `shiny/.agents/skills/` for it — bundled Agent Skills document public APIs and must be updated in the same PR
