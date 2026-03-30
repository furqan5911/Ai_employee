# generate-briefing

Generate the Monday Morning CEO Briefing — a proactive weekly business summary.

## Trigger

Use this skill when:
- It is Monday morning (scheduled at 7:00 AM)
- User says "generate briefing", "CEO briefing", "weekly summary", "business audit"
- Orchestrator triggers the weekly briefing task

## Instructions

1. **Determine the period**
   - Default: last 7 days (Monday to Sunday)
   - Use today's date for the filename

2. **Gather data from vault**
   - Read `Business_Goals.md`: revenue targets, active projects, key metrics
   - Read `Accounting/Current_Month.md`: income, expenses, outstanding invoices
   - Scan `/Done/` folder: count and categorize items completed this week
   - Scan `/Plans/` folder: identify delayed or stalled tasks
   - Read `Logs/*.jsonl` from the past 7 days: action summary

3. **Analyze subscriptions** (use audit_logic patterns)
   - Look for recurring charges in Accounting/Current_Month.md
   - Flag any subscription matching SUBSCRIPTION_PATTERNS that has no recent usage
   - Flag any cost increases > 20%

4. **Identify bottlenecks**
   - Tasks in /Plans/ older than their estimated completion date
   - Items that sat in /Needs_Action/ longer than 48 hours
   - Pending approvals older than 24 hours

5. **Generate proactive suggestions**
   - Cost savings opportunities (unused subscriptions)
   - Upcoming deadlines in the next 14 days
   - Revenue gaps vs. targets
   - Process improvement observations

6. **Write the briefing**
   - File: `/Briefings/<YYYY-MM-DD>_Monday_Briefing.md`
   - Use the template at `/Briefings/TEMPLATE_Monday_Briefing.md`
   - Keep it executive-level: concise, actionable, no fluff

7. **Update Dashboard.md**
   - Add briefing link to "Latest AI Suggestion" section
   - Update "Last Updated" timestamp

## Briefing Quality Standards

- Executive summary: MAX 3 sentences
- Revenue section: always show % of monthly target
- Bottlenecks: show actual delay, not just "delayed"
- Suggestions: always include a specific $ amount or time saved
- Tone: confident, direct, like a trusted senior employee briefing the CEO

## Output

Confirm with: "✅ CEO Briefing generated: /Briefings/<date>_Monday_Briefing.md"
