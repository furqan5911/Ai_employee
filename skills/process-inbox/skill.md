# process-inbox

Process all items in /Needs_Action/ - prioritize, handle, or create plans for each.

## Trigger

Use this skill when:
- User says: "process inbox", "handle pending", "what needs action", "process items"
- Items exist in /Needs_Action/ and need processing
- User wants to clear the pending queue
- Scheduled inbox processing (every 30 min)

## When NOT to Use

- DO NOT use for single specific items (handle directly instead)
- DO NOT use if /Needs_Action/ is empty
- DO NOT use if user wants to work on a specific plan

## Instructions

1. **Quick scan first** (token efficient)
   - List filenames in /Needs_Action/ only (don't read content yet)
   - Count by type: EMAIL_, FILE_, TASK_, etc.
   - Identify urgency from filenames

2. **Prioritize by urgency**
   - 🔴 CRITICAL: payment_overdue, legal_, security_, urgent_
   - 🟠 HIGH: invoice_, client_, deadline_
   - 🟡 MEDIUM: email_, task_, request_
   - 🟢 LOW: fyi_, admin_, newsletter_

3. **Process each item by type**

   **EMAIL_ files** → Use `process-email` skill
   - Read email content
   - Categorize and draft response
   - Create approval or move to Done

   **FILE_ files** → Read and determine action
   - Read file content
   - If invoice: create payment approval
   - If document: summarize and move to Done
   - If requires action: create plan

   **TASK_ files** → Use `create-plan` if multi-step
   - Read task requirements
   - If simple: do directly
   - If complex (3+ steps): create plan

4. **Move processed items**
   - Done: Move to /Done/
   - Needs approval: Move to /In_Progress/ + create approval in /Pending_Approval/
   - Plan created: Move to /In_Progress/ + plan in /Plans/

5. **Update Dashboard**
   - Use `update-dashboard` skill
   - Show counts: processed, remaining, awaiting approval

## Output Format

```markdown
## Inbox Processing Complete

**Total Processed**: N items
**Time Taken**: ~X minutes

### Results Summary
| Category | Processed | Awaiting Approval | Done |
|----------|-----------|-------------------|------|
| Emails | N | N | N |
| Files | N | N | N |
| Tasks | N | N | N |

### Awaiting Your Approval
- [item] - [brief description]
- [item] - [brief description]

### Completed
- [item] - [what was done]

### Remaining in Needs_Action
- [item] - [why not processed yet]
```

## Token Efficiency

**LIGHTWEIGHT MODE** (default):
- Scan filenames only
- Read only high-priority items
- ~1000-1500 tokens

**DEEP MODE** (user requests):
- Read all items
- Full processing
- ~3000-5000 tokens

## Processing Rules

From `Company_Handbook.md`:
- 🔴 CRITICAL: Process immediately, alert user
- 🟠 HIGH: Process within 2 hours
- 🟡 MEDIUM: Process within 24 hours
- 🟢 LOW: Process within 72 hours

## Related Skills

- `process-email`: Handles email items specifically
- `create-plan`: Creates plans for complex tasks
- `request-approval`: Creates approval files
- `update-dashboard`: Refreshes status
