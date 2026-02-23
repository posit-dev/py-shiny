# Interview-Based ADR Creation

Guide the user through an interactive interview to document a past architectural decision.

## Purpose

Sometimes decisions were made in the past without formal documentation. This command helps retroactively capture those decisions through a structured conversation.

## Interview Flow

### Phase 1: Set the Stage

Start with: "I'll help you document a past architectural decision as an ADR. Let's start with the basics."

**Question 1**: "What decision would you like to document? Give me a brief title or description."

*Wait for response before continuing.*

### Phase 2: Understand the Context

**Question 2**: "When was this decision made? (Approximate date is fine)"

**Question 3**: "Who was involved in making this decision?"

**Question 4**: "What was the situation that led to needing this decision? What problem were you trying to solve?"

*Summarize back*: "So if I understand correctly, [summary of context]. Is that right?"

### Phase 3: Explore Alternatives

**Question 5**: "What options did you consider? Even briefly considered or rejected ideas count."

*Wait for response listing options.*

For each option mentioned, **immediately** ask:
- "Tell me about [option] - what were the pros?"
- "What were the cons or concerns about [option]?"
- *Summarize*: "So [option] was good for [pros] but had issues with [cons]. Is that right?"

Then move to the next option.

If they only mention one option: "Was there ever any discussion of doing it differently? Even approaches that were quickly dismissed?"

### Phase 4: Understand the Decision

**Question 6**: "Which option did you ultimately choose?"

**Question 7**: "What were the main reasons for choosing this approach?"

**Question 8**: "Were there any trade-offs you accepted? Things you gave up or risks you took on?"

### Phase 5: Capture Consequences

**Question 9**: "Looking back, what were the positive outcomes of this decision?"

**Question 10**: "Were there any negative consequences or challenges that resulted?"

**Question 11**: "If you were making this decision again today, would you decide differently? Why or why not?"

### Phase 6: Generate the ADR

1. Read `adr/_template.md`
2. Determine the next ADR number from `adr/`
3. Synthesize interview answers into ADR format
4. Create the file at `adr/NNNN-<title>.md`
5. Update `adr/README.md` index

**Present the draft**: "Here's the ADR I've created based on our conversation. Please review it:"

*Show the full ADR content*

**Ask**: "Would you like me to make any changes before we finalize it?"

### Phase 7: Finalize

After any revisions:
- Save the final ADR
- Set status to "accepted" (since this is a past decision already in effect)
- Confirm: "ADR created at `adr/NNNN-title.md`. The decision has been documented!"

## Interview Tips

- **Be patient**: Let the user think and recall details
- **Probe gently**: If answers are vague, ask follow-up questions
- **Validate understanding**: Summarize back to confirm accuracy
- **Accept uncertainty**: "I don't remember" is a valid answer
- **Note gaps**: If information is missing, note it in the ADR

## Notes

- Past decisions should typically have status "accepted"
- If a decision has since been reversed, note it as "superseded" or "deprecated"
- Link to any related PRs or issues if the user can recall them
- It's okay to have some sections less detailed for older decisions
