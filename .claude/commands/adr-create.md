# Create ADR from User Plan

Create an Architecture Decision Record from a plan provided by the user.

## Workflow

1. **Get the plan from the user**

   Ask the user: "Please describe the decision or plan you want to document as an ADR. Include:
   - What problem are you solving?
   - What options did you consider?
   - What did you decide and why?"

2. **Read the template**

   Read `adr/_template.md` to understand the expected format.

3. **Determine the next ADR number**

   List existing ADRs in `adr/` and find the next sequence number:
   - If no ADRs exist, use `0001`
   - Otherwise, increment from the highest existing number

4. **Extract information from the plan**

   From the user's input, identify:
   - **Title**: A concise name for the decision
   - **Context**: The situation and problem being addressed
   - **Decision Drivers**: Key factors influencing the choice
   - **Options**: Alternatives that were considered
   - **Decision**: The chosen option
   - **Reasoning**: Why this option was selected
   - **Consequences**: Expected outcomes (positive and negative)

5. **Fill in any gaps**

   If the user's plan is missing information, ask clarifying questions:
   - "Who are the deciders for this decision?"
   - "What alternatives did you consider besides [chosen option]?"
   - "What are the potential downsides of this approach?"

6. **Generate the ADR**

   Create the ADR file at `adr/NNNN-<kebab-case-title>.md` using the template.

   Set the status to "proposed" unless the user indicates it's already accepted.

7. **Update the index**

   Add a link to the new ADR in `adr/README.md` under the Index section.

8. **Present the result**

   Show the user the created ADR and ask if any changes are needed.

## Example Interaction

**User**: I want to document our decision to use MADR format for ADRs.

**Claude**: I'll create an ADR for that. Let me gather some details:
- Who should be listed as deciders?
- What other formats did you consider (e.g., Y-statements, Nygard format)?
- What drove the decision to choose MADR?

**User**: The team decided. We considered plain markdown and Y-statements. MADR was chosen for its comprehensive structure and wide adoption.

**Claude**: *Creates `adr/0001-use-madr-format-for-adrs.md`*

## Notes

- Always use kebab-case for the filename
- Set today's date in YYYY-MM-DD format
- Link to relevant GitHub issues if mentioned
- Keep the title concise (under 50 characters ideally)
