# create-plan

Create a structured Plan.md file for any multi-step task (3+ steps).

## Trigger

Use this skill when:
- A task in /Needs_Action/ requires 3 or more distinct steps
- User says "create a plan", "make a plan for", "plan this out"
- An action item is complex and needs step-by-step tracking

## Instructions

1. **Understand the task**
   - Read the source file in /Needs_Action/ fully
   - Identify all required steps
   - Note any dependencies between steps
   - Identify which steps require human approval

2. **Create the plan file**
   - Filename: `Plans/PLAN_<descriptive-name>_<YYYYMMDD>.md`
   - Use the template below

3. **Claim the task**
   - Move the original /Needs_Action/ item to /In_Progress/ (claim-by-move rule)
   - This prevents duplicate processing

4. **Begin execution**
   - Work through each checkbox in order
   - Check off steps as they complete
   - For approval-required steps: create file in /Pending_Approval/ and STOP
   - Resume after approval is moved to /Approved/

## Plan File Template

```markdown
---
created: <ISO timestamp>
source_file: <original Needs_Action filename>
status: in_progress
priority: <high|medium|low>
estimated_completion: <ISO timestamp>
---

## Objective

<One sentence describing what this plan accomplishes>

## Context

<Brief context from the source file>

## Steps

- [ ] Step 1: <action>
- [ ] Step 2: <action>
- [ ] Step 3: <action> ⚠️ REQUIRES APPROVAL
- [ ] Step 4: <action>
- [ ] Step 5: Log completion and move to /Done/

## Approval Required

<Describe what needs human approval and why>
See: /Pending_Approval/<filename>

## Completion Criteria

<What does "done" look like for this task>
```

## Ralph Wiggum Loop

For long tasks, after completing a plan step, output `<promise>TASK_COMPLETE</promise>`
only when ALL steps are checked off and files moved to /Done/.

If interrupted, re-read the plan file and continue from the first unchecked step.
