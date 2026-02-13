# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

py-shiny is a Python web framework for building reactive web applications. It maintains feature parity with Shiny for R, often porting UI components from the R bslib package. The codebase consists of Python server-side code, TypeScript/JavaScript client-side code, and vendored assets from upstream packages.

## Development Commands

### Essential Commands
```bash
# Install dev dependencies
pip install -e ".[dev,test,doc]"

# Format code (always run before committing)
make format              # Auto-fix with black and isort
make check-format        # Check only

# Type checking
make check-types         # Run pyright (requires typings)

# Run tests
make test                # Unit tests only (pytest)
make playwright          # All end-to-end tests (slow)
make playwright-shiny SUB_FILE="inputs/test_foo.py"  # Single test

# Comprehensive checks
make check               # Format, lint, types, unit tests
make check-fix           # Same but auto-fixes formatting
```

### Asset Management
```bash
# Vendor assets from upstream (bslib, shiny, sass, htmltools)
make upgrade-html-deps   # Requires R installed

# Build JavaScript/TypeScript
make js-build            # One-time build
make js-watch            # Continuous rebuild
```

### Documentation
```bash
# Build API docs (slow, run at the end)
make docs                # Build with quartodoc
make docs-preview        # Build and serve locally
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

### Reactive System

The reactive system is based on a **push-pull** model with three core abstractions:

- **Context**: Tracks reactive dependencies during execution. When a reactive consumer (Calc/Effect) runs, it creates a Context that records which reactive sources (Value) it reads from.
- **Dependents**: Each reactive source maintains a list of downstream consumers that depend on it. When a source invalidates, it notifies all dependents.
- **ReactiveEnvironment**: Global singleton managing the reactive graph, execution queue, and flush cycles.

Key implementation details:
- `Value()` is the reactive source (observable)
- `Calc_()` is a cached computed value (recomputes only when dependencies change)
- `Effect_()` is a side-effect that re-executes when dependencies change
- `event()` decorator suppresses reactive dependencies for specific reads
- The reactive graph is built automatically through the Context's dependency tracking
- Execution uses a priority queue to ensure correct invalidation ordering

### Session Hierarchy

Sessions manage the lifetime and state of a Shiny application:

- **Session (ABC)**: Base interface defining core session operations
- **AppSession**: Concrete implementation for a single user's session
- **SessionProxy**: Thread-safe proxy that delegates to the appropriate AppSession
- **Inputs/Outputs**: Dynamic objects providing dict-like access to input/output values

Session management:
- Each WebSocket connection gets its own AppSession
- `get_current_session()` retrieves the current session from thread-local or async context
- Sessions track input values, output invalidations, file uploads, downloads, and more
- Session context is established using `session_context(session)` context manager

### Express vs Core Mode

**Core mode** is imperative: you explicitly construct UI and define server logic in a function.

**Express mode** transforms Python code using AST manipulation:
- `@render.text` decorators are hoisted into a synthetic `server()` function
- UI elements are collected into a synthetic `ui` object
- Top-level code runs in a special context where UI calls are recorded
- `RecallContextManager` enables UI elements to render themselves automatically
- The transformation happens at import time via `_run.py` and `_node_transformers.py`

Critical difference: Express mode uses **execution order** (top-to-bottom) for UI layout, while Core mode uses explicit nesting.

### HTML Generation and Dependencies

HTML is generated using the `htmltools` package:
- UI functions return `Tag` or `TagList` objects
- Tags are mutable; use `.add_class()`, `.add_style()`, `.attrs()` to modify
- HTML dependencies are attached to tags and automatically bundled
- `components_dependencies()` returns bslib component dependencies

Asset vendoring:
- SCSS source files from bslib are in `shiny/www/shared/sass/bslib/components/scss/`
- Compiled CSS is generated for all theme presets (27 files in `shiny/www/shared/sass/preset/`)
- JavaScript bundles are in `shiny/www/shared/bslib/components/components.min.js`
- `make upgrade-html-deps` runs `scripts/htmlDependencies.R` to update all assets

### Input/Output Bindings

Client-server communication works through bindings:

**Input bindings** (client → server):
- Registered via CSS class selectors in TypeScript (e.g., `.bslib-input-foo`)
- Implement `getValue()`, `setValue()`, `subscribe()` methods
- Send values to server using `Shiny.setInputValue(id, value)`
- Server receives via `input.foo()` which returns a reactive Value

**Output bindings** (server → client):
- Server defines output using `@render.text`, `@render.plot`, etc.
- Renderers inherit from `Renderer` base class
- Client subscribes to output via `Shiny.bindOutput()` in TypeScript
- Updates are sent as messages through the WebSocket

**Update functions**:
- Use `session.send_input_message()` to update input widgets from server
- Client handles via `receiveMessage()` in the input binding

### Module System

Modules enable namespaced, reusable components:
- `@module.ui` decorator creates a UI function with automatic ID namespacing
- `@module.server` decorator creates a server function with namespace context
- Inside a module, use `resolve_id()` to namespace IDs
- `resolve_id_or_none()` for optional namespacing
- Modules can be nested; namespaces compose with `parent-child` format

Implementation: `_namespaces.py` manages the namespace stack, `module.py` provides decorators.

### Testing Architecture

**Unit tests** (`tests/pytest/`):
- Use standard pytest with syrupy for snapshots
- Focus on Python API correctness, parameter validation, edge cases
- Run with `make test` or `pytest`

**Playwright tests** (`tests/playwright/`):
- End-to-end tests using Playwright with custom controllers
- Controllers in `shiny/playwright/controller/` provide high-level APIs for interacting with inputs/outputs
- Each input component should have a controller class
- Test apps live alongside test files
- Run with `make playwright` (all browsers) or `make playwright-debug` (chromium, headed)

**Playwright controller pattern**:
```python
from shiny.playwright.controller import InputText, OutputText

text_input = InputText(page, "my_input")
text_input.set("foo")
text_input.expect_value("foo")

text_output = OutputText(page, "my_output")
text_output.expect_value("You entered: foo")
```

### JavaScript/TypeScript Build

Client-side code is in `js/`:
- Entry point: `js/src/shiny/index.ts`
- Build tool: esbuild via `js/build.ts`
- Output: `shiny/www/shared/py-shiny/shiny.js` and minified variant
- TypeScript definitions for Python-JS interop

Development workflow:
- `make js-watch` for continuous rebuilds during development
- Changes to `js/src/` require rebuilding to see effects in Python apps
- Source maps are generated for debugging

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
- `scripts/htmlDependencies.R` - Vendors assets from bslib/shiny/sass/htmltools
- `shiny/_versions.py` - Version tracking for vendored dependencies
- `shiny/ui/_html_deps_*.py` - HTML dependency definitions

### Configuration
- `pyproject.toml` - Package config, dependencies, tool settings
- `pyrightconfig.json` - Pyright type checker configuration
- `pytest.ini` - Pytest configuration
- `.pre-commit-config.yaml` - Pre-commit hook configuration

### Documentation
- `docs/_quartodoc-core.yml` - Core API reference config
- `docs/_quartodoc-express.yml` - Express API reference config
- `docs/_quartodoc-testing.yml` - Testing API reference config
- Add new functions here to include in generated docs (alphabetical order within sections)

## Important Patterns

### Component Implementation Pattern

When implementing a UI component:
1. Create file in `shiny/ui/_component_name.py`
2. Use `@add_example()` decorator with example from `shiny/api-examples/`
3. Use `resolve_id()` for module support
4. Use `restore_input()` for bookmarking support (input components)
5. Return Tag/TagList with `components_dependencies()` for bslib deps
6. Export from `shiny/ui/__init__.py` (and `shiny/express/ui/__init__.py` if applicable)

### Renderer Implementation Pattern

When creating a custom renderer:
1. Inherit from `Renderer[T]` base class
2. Implement `auto_output_ui()` for automatic UI generation
3. Implement `render()` async method returning the rendered value
4. Use `@output_transformer()` decorator for post-processing
5. Register in `shiny/render/__init__.py`

### Type Checking Notes

- Pyright is the primary type checker (not mypy)
- Some packages require manual stubs: run `make pyright-typings` to generate
- Stubs are placed in `typings/` (gitignored)
- Parameter types: prefer `Optional[T]` over `T | None` for user-facing APIs
- Use `Literal` instead of `Enum` for string options

## Git Commit and PR Conventions

This project uses **conventional commits** for commit messages and PR titles:

### Commit Message Format
```
<type>: <description>

[optional body]

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

### Common Types
- **feat**: New feature (e.g., `feat: Add input_submit_textarea component`)
- **fix**: Bug fix (e.g., `fix: Resolve session context error in modules`)
- **docs**: Documentation changes (e.g., `docs: Update reactive programming guide`)
- **refactor**: Code refactoring without behavior change
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependency updates
- **perf**: Performance improvements
- **style**: Code style/formatting changes (not user-facing style)

### Guidelines
- Use present tense: "Add feature" not "Added feature"
- Keep the description concise (under 72 characters for the first line)
- Use sentence case: "Add feature" not "add feature"
- No period at the end of the subject line
- Body is optional but useful for explaining "why" not "what"
- Always include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` when Claude writes the code

### PR Titles
PR titles should follow the same conventional commit format:
- `feat: Add Toolbar component`
- `fix: Pin griffe to <2.0.0 for quartodoc compatibility`
- `refactor: Simplify reactive graph invalidation logic`

## Porting from bslib

For comprehensive guidance on porting components from R's bslib package, see `.claude/skills/port-from-bslib/SKILL.md`. Key steps:

1. Locate and study the bslib source (R, TypeScript, SCSS)
2. Create Python implementation in `shiny/ui/`
3. Run `make upgrade-html-deps` to vendor compiled assets
4. Create API examples in `shiny/api-examples/`
5. Create Playwright controller (if input component)
6. Port unit tests and create end-to-end tests
7. Update quartodoc YAML files
8. Update `CHANGELOG.md`

## Common Pitfalls

- **Forgetting to run `make format`**: Always format before committing
- **Missing HTML deps**: If styles don't work, ensure `components_dependencies()` is included
- **Express mode confusion**: Remember Express uses AST transformation; debugging requires understanding the transformed code
- **Session context errors**: Always access `input`/`output` within reactive context
- **Reactive graph debugging**: Use `reactive.flush()` to force synchronous execution in tests
- **Playwright timing**: Use `.expect_*()` methods which auto-wait; avoid manual `sleep()`
- **Asset updates**: After running `make upgrade-html-deps`, verify theme preset files were updated
