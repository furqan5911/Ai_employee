# process-inbox

Scan /Needs_Action/ for pending items, prioritize them, and process each one.

## Trigger

Use this skill when:
- New files appear in /Needs_Action/
- User says "check inbox", "process inbox", "what's new", "what needs action"
- Orchestrator triggers a processing cycle

## Instructions

1. **Read context first**
   - Read `Dashboard.md` to understand current state
   - Read `Company_Handbook.md` for rules and priority matrix

2. **Scan /Needs_Action/**
   - List all .md files (ignore .gitkeep)
   - Read each file's frontmatter: `type`, `priority`, `status`

3. **Prioritize**
   - 🔴 CRITICAL first: legal, security, payment overdue
   - 🟠 HIGH second: client messages, invoices, deadlines today
   - 🟡 MEDIUM third: general emails, follow-ups
   - 🟢 LOW last: admin, FYI items

4. **Process each item**
   - For simple/informational: summarize and move to /Done/
   - For tasks requiring action: use `create-plan` skill
   - For sensitive actions (email new contact, payment, social post): use `request-approval` skill
   - For items needing human input: leave in /Needs_Action/ with a note added

5. **After all items processed**
   - Use `update-dashboard` skill to refresh Dashboard.md
   - Use `audit-log` skill to record what was done
   - Output summary of what was processed

## Output Format

```
## Inbox Processing Complete

**Processed**: N items
**Actions taken**:
- [item] → [what was done]
- ...

**Pending approval**: N items in /Pending_Approval/
**Needs human input**: N items still in /Needs_Action/
```

Output `<promise>TASK_COMPLETE</promise>` when all items are processed.
