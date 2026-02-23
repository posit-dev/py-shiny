# Create ADR from Current Plan

Convert Claude's currently active plan (PLAN.md or todo list) into an Architecture Decision Record.

## Workflow

1. **Locate the current plan**

   Check for an active plan in these locations (in order):
   - `PLAN.md` in the repository root
   - Active todo list from the current session
   - Recent planning discussion in the conversation

   If no plan is found, inform the user and suggest using `/adr-create` or `/adr-interview` instead.

2. **Read the template**

   Read `adr/_template.md` to understand the expected format.

3. **Determine the next ADR number**

   List existing ADRs in `adr/` and find the next sequence number.

4. **Analyze the plan**

   Extract from the current plan:
   - **Problem Statement**: What issue is the plan addressing?
   - **Proposed Solution**: What approach does the plan take?
   - **Implementation Steps**: These often reveal decision drivers
   - **Alternatives**: Any options mentioned or implied

5. **Transform into ADR format**

   Map plan elements to ADR sections:

   | Plan Element | → | ADR Section |
   |--------------|---|-------------|
   | Plan title | → | Title (concise, use kebab-case for filename) |
   | Overview/why this is needed | → | Context and Problem Statement |
   | Goals/requirements mentioned | → | Decision Drivers |
   | Implementation approach | → | Decision Outcome (the "what", not the "how") |
   | Alternative approaches mentioned | → | Considered Options |
   | Benefits/rationale | → | Positive Consequences |
   | Trade-offs/concerns | → | Negative Consequences |
   | Related issues/PRs | → | Technical Story + Links section |

   **Key transformation principle**: Plans describe "how to implement", ADRs describe "what we decided and why".

6. **Fill gaps with the user**

   Plans often lack some ADR elements. Ask the user:
   - "What alternatives did you consider before this plan?"
   - "Who should be listed as deciders?"
   - "What are the potential downsides of this approach?"

   **Status determination**:
   - If the plan is actively being implemented → status is "accepted"
   - If the plan is awaiting approval → status is "proposed"
   - If unclear, ask: "Is this decision already approved, or awaiting review?"

7. **Generate the ADR**

   Create `adr/NNNN-<title>.md` based on the transformed plan.

8. **Handle the plan file**

   Ask the user: "The plan has been converted to ADR. Would you like me to:
   - Keep PLAN.md as-is (for continued implementation tracking)
   - Delete PLAN.md (if implementation is complete)
   - Archive PLAN.md somewhere else"

9. **Update the index**

   Add a link to the new ADR in `adr/README.md`.

## Example

Given a `PLAN.md` like:

```markdown
# Add Reactive Polling to File Watcher

## Overview
Implement reactive polling for file system changes in Shiny apps.

## Implementation
1. Add watchdog dependency for file system events
2. Create reactive poll wrapper
3. Integrate with reactive graph
4. Add examples showing auto-reload patterns
```

Claude would:
1. Identify the problem: need reactive file system monitoring
2. Identify the decision: use watchdog library with reactive polling
3. Ask about alternatives considered (OS-native watchers, manual polling, etc.)
4. Generate an ADR capturing the file watching decision

## Notes

- The plan likely contains implementation details not needed in the ADR
- Focus on extracting the "why" and "what" rather than "how"
- ADRs are about decisions, plans are about execution
- Keep the ADR focused on the architectural choice, not implementation steps
