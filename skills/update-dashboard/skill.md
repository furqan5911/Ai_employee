# update-dashboard

Refresh Dashboard.md with current system status, counts, and recent activity.

## Trigger

Use this skill when:
- After processing any items from /Needs_Action/
- After completing any significant action
- User says "update dashboard", "refresh status", "what's the status"
- Orchestrator runs a scheduled dashboard refresh (every 30 min)
- After generating a briefing

## Instructions

1. **Count items in each folder** (only .md files, exclude .gitkeep)
   - `/Needs_Action/` → pending items count
   - `/Pending_Approval/` → awaiting approval count
   - `/Approved/` → approved but not yet executed count
   - `/Done/` with today's date in filename → completed today count

2. **Read financial data**
   - Check `Accounting/Current_Month.md` for balance and revenue data
   - Note any pending invoices

3. **Read active projects**
   - Check `Business_Goals.md` for active projects and their status

4. **Compile recent activity** (last 10 actions)
   - Read today's log from `Logs/YYYY-MM-DD.jsonl`
   - Format as: `[HH:MM] <action> - <outcome>`

5. **Update Dashboard.md**
   - Update ONLY the dynamic values — never change the structure
   - Set "Last Updated" to current timestamp
   - Set system status to: 🟢 Active / 🟡 Issues / 🔴 Error

6. **System health check**
   - Verify key folders exist and are accessible
   - Note if any folder is unexpectedly large (>50 files in Needs_Action = backlog alert)

## Dashboard Sections to Update

- `Last Updated` timestamp
- `System Status` indicator
- Inbox Summary counts (Needs_Action, Pending_Approval, Approved, Done)
- Financial Snapshot (from Accounting/Current_Month.md)
- Active Projects (from Business_Goals.md)
- Pending Approvals list (top 3 most urgent)
- Recent Activity (last 10 entries from today's log)
- System Health table

## Important

- Preserve ALL markdown formatting exactly
- Only update values, never restructure the file
- If a section can't be updated (missing data), leave it as-is with a note
