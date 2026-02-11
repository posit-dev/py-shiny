# ADR System Implementation Plan

## Overview

Set up an Architecture Decision Record (ADR) system for the py-shiny project with Claude Code integration. This includes documentation guidance, ADR templates, and Claude commands for creating/managing ADRs.

## Current State

- `.claude/` folder exists with `skills/` subdirectory
- No `CLAUDE.md` file at root or in `.claude/`
- `docs/` folder exists (Quarto/Quartodoc-based)
- No existing ADR system

## Files to Create

### 1. `.claude/CLAUDE.md` - Claude Code Instructions

Purpose: Root-level guidance for how Claude should interact with this codebase.

Contents:
- Project overview (py-shiny: Python implementation of Shiny web framework)
- Folder structure explanation
- Key development patterns and conventions
- Testing requirements
- Documentation standards
- Reference to existing skills (port-from-bslib)
- Reference to ADR system

### 2. `docs/adr/README.md` - ADR System Documentation

Purpose: Explain the ADR system and how to use it.

Contents:
- What are ADRs and why we use them
- ADR naming convention: `NNNN-<kebab-case-title>.md`
- ADR lifecycle (proposed → accepted/rejected → deprecated/superseded)
- How to create a new ADR (manual and via Claude commands)
- Index of existing ADRs (to be maintained)

### 3. `docs/adr/_template.md` - MADR Template

Purpose: Standard template for new ADRs following MADR format.

Sections (per MADR specification):
- Title (in H1)
- Metadata block (Status, Deciders, Date, Technical Story)
- Context and Problem Statement
- Decision Drivers
- Considered Options
- Decision Outcome
  - Positive Consequences
  - Negative Consequences
- Pros and Cons of Options (subsections per option)
- Links

### 4. `.claude/commands/adr-create.md` - Create ADR from User Plan

Purpose: Claude command to create an ADR when user provides a plan.

Workflow:
1. Prompt user for their plan/decision details
2. Extract key decision points
3. Guide through MADR sections
4. Generate ADR file with next sequence number
5. Offer to create PR or commit

### 5. `.claude/commands/adr-from-current.md` - Create ADR from Active Plan

Purpose: Claude command to create an ADR from Claude's currently active plan.

Workflow:
1. Read the current PLAN.md or active todo list
2. Transform plan into ADR format
3. Prompt for any missing information (deciders, alternatives considered)
4. Generate ADR file
5. Clean up temporary plan file if appropriate

### 6. `.claude/commands/adr-interview.md` - Interview-Based ADR Creation

Purpose: Guide user through creating an ADR about a past decision.

Workflow:
1. Ask about the decision context
2. Probe for problem statement
3. Explore alternatives that were considered
4. Document the chosen approach and reasoning
5. Capture consequences (positive and negative)
6. Generate complete ADR

## Implementation Order

1. **`.claude/CLAUDE.md`** - Foundation for Claude interaction
2. **`docs/adr/_template.md`** - Template needed by commands
3. **`docs/adr/README.md`** - Documentation for the system
4. **`.claude/commands/adr-create.md`** - Primary command
5. **`.claude/commands/adr-from-current.md`** - Plan conversion
6. **`.claude/commands/adr-interview.md`** - Interview workflow

## File Details

### `.claude/CLAUDE.md` Structure

```markdown
# Claude Code Instructions for py-shiny

## Project Overview
[Brief description of py-shiny]

## Folder Structure
- `shiny/` - Main Python package
- `js/` - TypeScript/JavaScript source
- `tests/` - Test suite
- `docs/` - Documentation (Quarto)
- `docs/adr/` - Architecture Decision Records
- `.claude/` - Claude Code configuration
  - `skills/` - Specialized task guidance
  - `commands/` - Reusable Claude commands

## Development Conventions
[Key patterns, testing, etc.]

## ADR System
[Reference to docs/adr/README.md]
```

### `docs/adr/_template.md` Structure

```markdown
# [Title]

## Status
[proposed | rejected | accepted | deprecated | superseded by [ADR-NNNN](NNNN-*.md)]

## Deciders
- [List of people involved]

## Date
YYYY-MM-DD

## Technical Story
[Description or ticket/issue reference]

## Context and Problem Statement
[2-3 sentences or a focused question]

## Decision Drivers
- [Driver 1]
- [Driver 2]
- ...

## Considered Options
1. [Option 1]
2. [Option 2]
3. [Option 3]

## Decision Outcome
Chosen option: "[Option N]", because [justification].

### Positive Consequences
- [Consequence 1]
- [Consequence 2]

### Negative Consequences
- [Consequence 1]
- [Consequence 2]

## Pros and Cons of Options

### [Option 1]
- Good, because [argument]
- Bad, because [argument]

### [Option 2]
- Good, because [argument]
- Bad, because [argument]

### [Option 3]
- Good, because [argument]
- Bad, because [argument]

## Links
- [Link type] [Link to ADR or resource]
```

### Command File Patterns

Each command in `.claude/commands/` should:
1. Have a clear title and description
2. Define the workflow steps
3. Specify required inputs
4. Include the expected output format
5. Reference the template location

## Notes

- ADR numbering starts at 0001
- Use kebab-case for ADR filenames
- Status should be updated as decisions evolve
- Consider creating an initial ADR (0001) documenting the decision to use ADRs
