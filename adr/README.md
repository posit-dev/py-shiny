# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records (ADRs) for the py-shiny project.

## What is an ADR?

An Architecture Decision Record captures an important architectural decision made along with its context and consequences. ADRs help teams:

- **Document** significant decisions for future reference
- **Communicate** decisions to team members and stakeholders
- **Understand** the reasoning behind existing architecture
- **Onboard** new contributors by explaining "why" things are the way they are

## ADR Format

We use the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Record) format. Each ADR includes:

- **Status**: proposed, accepted, rejected, deprecated, or superseded
- **Context**: The situation and problem being addressed
- **Decision Drivers**: Factors influencing the choice
- **Options Considered**: Alternatives that were evaluated
- **Decision Outcome**: The chosen option and its justification
- **Consequences**: Both positive and negative outcomes

See [`_template.md`](_template.md) for the full template.

## Naming Convention

ADRs follow the naming pattern:

```
NNNN-<kebab-case-title>.md
```

Where:
- `NNNN` is a 4-digit sequence number (0001, 0002, etc.)
- `<kebab-case-title>` is a short, descriptive title

Examples:
- `0001-use-adr-system.md`
- `0002-adopt-express-mode.md`
- `0003-vendor-bslib-assets.md`

## Creating an ADR

### Using Claude Commands

The easiest way to create an ADR is using the Claude slash commands:

| Command | When to Use | Description |
|---------|-------------|-------------|
| `/adr-create` | You have a plan to document | Create an ADR from a plan you provide in the conversation |
| `/adr-from-current` | Claude has an active plan/todo list | Convert Claude's current working plan into an ADR |
| `/adr-interview` | Documenting a past decision | Interactive interview to capture a decision already made |

**Which command should I use?**

```
┌─ Is the decision already made and implemented?
│
├─ YES → Use /adr-interview
│         (captures past decisions retroactively)
│
└─ NO → Is Claude currently working on a plan?
        │
        ├─ YES → Use /adr-from-current
        │         (converts active PLAN.md or todo list)
        │
        └─ NO → Use /adr-create
                  (you provide the plan details)
```

### Manual Creation

1. Copy `_template.md` to a new file with the next sequence number
2. Fill in all sections
3. Set status to "proposed"
4. Submit for review

## ADR Lifecycle

```
proposed → accepted → [deprecated | superseded]
    ↓
 rejected
```

- **proposed**: Initial state, under review
- **accepted**: Decision approved and in effect
- **rejected**: Decision not approved
- **deprecated**: Decision no longer relevant
- **superseded**: Replaced by a newer ADR (link to the new one)

## When to Write an ADR

Write an ADR when:

- Adding a new major feature or component
- Changing existing architectural patterns
- Making technology or dependency choices
- Establishing new conventions or standards
- Deprecating or removing significant functionality

You probably don't need an ADR for:

- Bug fixes
- Minor refactoring
- Documentation updates
- Routine dependency updates

## ADR Workflow and Review

### Creating and Proposing ADRs

1. **Create the ADR** using one of the Claude commands or manually
2. **Set status to "proposed"** for new decisions
3. **Submit a PR** that includes:
   - The ADR file (`adr/NNNN-title.md`)
   - Update to `adr/README.md` index
   - Any related implementation (if applicable)

### Reviewing ADRs

When reviewing an ADR PR, check:

- [ ] Title is clear and concise
- [ ] Context explains the problem adequately
- [ ] Decision drivers are well-justified
- [ ] Multiple options were considered
- [ ] Consequences (both positive and negative) are realistic
- [ ] Links to related issues/PRs are included
- [ ] Formatting follows the template

### Accepting ADRs

- **For proposed decisions**: Team lead or maintainer changes status from "proposed" to "accepted"
- **For past decisions** (via `/adr-interview`): Status is "accepted" immediately since decision is already in effect
- Acceptance can happen in the same PR or a follow-up commit

### Updating ADR Status

When circumstances change:

- **Deprecating**: Add note explaining why, set status to "deprecated"
- **Superseding**: Create new ADR, update old one with "superseded by [ADR-XXXX]" link
- **Rejecting**: Add rejection reason, set status to "rejected"

Status changes should be committed with explanation in commit message.

## Index

<!-- Add links to ADRs here as they are created -->

*No ADRs yet. Create the first one!*
