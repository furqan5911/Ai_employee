# audit-log

Append a structured entry to today's audit log for every action taken.

## Trigger

Use this skill:
- After EVERY external action (email sent, payment made, file deleted, social post)
- After processing items from /Needs_Action/
- After executing an approved action
- After generating a briefing
- When user asks "what did you do today", "show me the log", "activity summary"

## Instructions

### Writing a Log Entry

Append to `/Logs/YYYY-MM-DD.jsonl` (JSON Lines format — one JSON object per line):

```json
{
  "timestamp": "<ISO 8601 timestamp>",
  "action_type": "<see Action Types below>",
  "actor": "claude_code",
  "target": "<what was acted upon>",
  "parameters": {"<key>": "<value>"},
  "approval_status": "<approved|auto|pending|not_required>",
  "approved_by": "<human|system|auto>",
  "result": "<success|error|skipped|dry_run>",
  "error": "<error message if result=error>"
}
```

### Action Types

| action_type | When to use |
|---|---|
| `inbox_scan` | Scanned /Needs_Action/ |
| `task_processed` | Processed a Needs_Action item |
| `plan_created` | Created a Plan.md |
| `approval_requested` | Created a Pending_Approval file |
| `approval_executed` | Executed an approved action |
| `email_drafted` | Drafted an email (not sent) |
| `email_sent` | Sent an email via MCP |
| `payment_drafted` | Drafted a payment request |
| `social_post_drafted` | Drafted a social media post |
| `dashboard_updated` | Updated Dashboard.md |
| `briefing_generated` | Generated a CEO briefing |
| `file_moved` | Moved a file between folders |
| `system_alert` | Watchdog or system event |

### Reading the Log

When user asks about activity, read today's `.jsonl` file and summarize:
- Total actions taken
- Actions by type
- Any errors
- Success rate

### Log Retention

Logs in `/Logs/` should be retained for 90 days minimum.
Do not delete log files.

### Example Entry

```json
{"timestamp": "2026-03-21T14:30:00Z", "action_type": "task_processed", "actor": "claude_code", "target": "EMAIL_20260321_client_invoice.md", "parameters": {"priority": "high", "type": "email"}, "approval_status": "not_required", "approved_by": "auto", "result": "success"}
```
