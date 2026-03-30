# exec-plan

Execute a plan from /Plans/ - implements the Ralph Wiggum persistence pattern for multi-step tasks.

## Trigger

Use this skill when:
- A plan file exists in `/Plans/` and needs to be executed
- User says: "execute plan", "continue plan", "work on plan", "finish plan"
- User references a specific plan: "work on PLAN_invoice"
- After approval is granted (file moved to /Approved/)

## When NOT to Use

- DO NOT use for single-step tasks (do them directly)
- DO NOT use if no plan exists (use create-plan first)
- DO NOT use if plan is already complete (in /Done/)

## Instructions

1. **Find the plan**
   - If user specified plan name, use that
   - Otherwise, find most recent plan in /Plans/
   - Read the plan file

2. **Check status**
   - If plan is marked "complete" or "done", move to /Done/ and exit
   - If plan has approval pending, wait for approval
   - Note current progress (which checkboxes are complete)

3. **Execute steps**
   - Start from first UNCHECKED step
   - Execute the step
   - Update checkbox: [ ] → [x]
   - Save the plan file

4. **Handle approvals**
   - If step requires approval, create approval file using `request-approval` skill
   - STOP and wait for user to move file to /Approved/
   - Resume from this step when approval granted

5. **Complete or continue**
   - If all checkboxes done: move plan to /Done/, output `<promise>TASK_COMPLETE</promise>`
   - If steps remain: output progress and next step
   - Update related files (Dashboard, Logs)

## Output Format

```markdown
## Executing: [Plan Name]

**Progress**: N/M steps complete (X%)

### Completed Steps
- [x] Step 1
- [x] Step 2

### Current Step
→ [ ] Step 3: [description]
[Executing...]

### Remaining
- [ ] Step 4
- [ ] Step 5

### Next Action
[What happens next or if approval needed]
```

## Plan File Format

Plans should follow this format:

```markdown
---
created: 2026-03-30T10:00:00Z
status: in_progress
priority: high
---

## Objective
[What this plan accomplishes]

## Steps
- [x] Step 1: Completed
- [ ] Step 2: Current step
- [ ] Step 3: Next step ⚠️ REQUIRES APPROVAL
- [ ] Step 4: Final step

## Completion Criteria
[What "done" looks like]
```

## Persistence Pattern

This skill implements the Ralph Wiggum loop:
1. Read plan state
2. Execute next step
3. Update plan file
4. Repeat until all steps complete
5. Output `<promise>TASK_COMPLETE</promise>`

If interrupted, re-reading the plan resumes from where it left off.

## Token Efficiency

- Reads one plan file per execution
- Updates plan file after each step
- Avoids re-reading completed steps
- ~1000-2000 tokens per step depending on task

## Related Skills

- `create-plan`: Creates new plans
- `request-approval`: Handles approval steps
- `process-inbox`: Handles items in Needs_Action
