# Claude Code Instructions for py-shiny

## Project Overview

py-shiny is the Python implementation of the Shiny web application framework. It enables building interactive web applications in Python with reactive programming patterns. The project maintains feature parity with Shiny for R, often porting components from the R bslib package.

## Folder Structure

```
py-shiny/
├── shiny/              # Main Python package
│   ├── ui/             # UI components (inputs, outputs, layouts)
│   ├── render/         # Output renderers
│   ├── express/        # Express mode API
│   ├── playwright/     # Playwright test controllers
│   ├── api-examples/   # Example apps for documentation
│   └── www/            # Static assets (CSS, JS, vendored deps)
├── js/                 # TypeScript/JavaScript source code
├── tests/              # Test suite
│   ├── pytest/         # Unit tests
│   └── playwright/     # End-to-end tests
├── adr/                # Architecture Decision Records
├── docs/               # Documentation (Quarto/Quartodoc)
├── scripts/            # Build and utility scripts
├── examples/           # Example applications
└── .claude/            # Claude Code configuration
    ├── skills/         # Specialized task guidance
    └── commands/       # Reusable slash commands
```

## Development Conventions

### Code Style
- Use `snake_case` for functions and variables
- Use `PascalCase` for classes
- Follow existing patterns in the codebase
- Type hints are required for public APIs

### Testing
- Unit tests: `pytest tests/pytest/`
- End-to-end tests: `pytest tests/playwright/`
- Run all checks: `make check`
- Format code: `make format`

### Quality Commands
- `make format` - Auto-fix formatting and linting
- `make check-types` - Run pyright type checking
- `make check-tests` - Run test suite
- `make playwright` - Run Playwright tests
- `make docs` - Build documentation

## Available Skills

- **port-from-bslib** (`.claude/skills/port-from-bslib/SKILL.md`): Comprehensive guide for porting UI components from R's bslib package to py-shiny.

## Available Commands

- **/adr-create**: Create an ADR from a user-provided plan
- **/adr-from-current**: Create an ADR from Claude's currently active plan
- **/adr-interview**: Guide through an interview to document a past decision

## Architecture Decision Records

This project uses ADRs to document significant architectural decisions. See `adr/README.md` for details on the ADR system.

### When to Create an ADR
- Adding new major features or components
- Changing existing architectural patterns
- Making technology or dependency choices
- Establishing new conventions or standards

### ADR Workflow
1. Use `/adr-create`, `/adr-from-current`, or `/adr-interview` commands
2. ADRs are stored in `adr/` with format `NNNN-<title>.md`
3. Follow the MADR template in `adr/_template.md`
