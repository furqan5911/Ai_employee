# vault-cleanup

Prepare vault for safe GitHub push by removing/redacting sensitive data.

## Trigger

Use this skill when:
- User is preparing to push to GitHub
- User says: "cleanup vault", "prepare for github", "safe to push"
- Before running `git push` command
- User wants to check if vault is safe to share

## When NOT to Use

- DO NOT use during normal operation (only before git push)
- DO NOT use automatically (wastes time and tokens)
- DO NOT use if not pushing to GitHub

## Instructions

1. **Scan folders for sensitive data**
   - `/Needs_Action/` - May contain emails, personal info
   - `/Pending_Approval/` - May contain approval details
   - `/In_Progress/` - May contain active work
   - `/Logs/` - May contain activity data
   - Check for: email addresses, phone numbers, API keys, passwords, names

2. **Report findings**
   - List files that contain sensitive data
   - Show what type of data (email, name, etc.)
   - Recommend action: redact, delete, or keep as-is

3. **Offer cleanup options**
   - Option A: Redact sensitive info (replace with [REDACTED])
   - Option B: Delete file entirely
   - Option C: Move to a separate private folder
   - Option D: Add to .gitignore (for future files)

4. **Perform cleanup**
   - Apply user's chosen action
   - Confirm changes
   - Update .gitignore if needed

## What to Redact

```markdown
# Common sensitive patterns:
- Email addresses: user@example.com → [EMAIL]
- Phone numbers: +1-555-123-4567 → [PHONE]
- Names: John Doe → [NAME]
- Addresses: 123 Main St → [ADDRESS]
- API keys: sk-xxxxx → [API_KEY]
- Financial data: $123.45 → $[AMOUNT]
- Company names: Acme Corp → [COMPANY]
```

## Safe Folders (Can push as-is)

- ✅ `/Done/` - Completed tasks (review first)
- ✅ `/Briefings/` - Generated reports (safe)
- ✅ `/Accounting/` - Financial logs (review for personal info)
- ✅ `/Plans/` - Task plans (usually safe)
- ✅ `/Rejected/` - Rejected items (usually safe)

## Unsafe Folders (Must clean)

- ❌ `/Needs_Action/` - Contains raw emails/data
- ❌ `/Pending_Approval/` - May have sensitive approvals
- ❌ `/In_Progress/` - Active work with personal data
- ⚠️ `/Logs/` - May contain activity data
- ⚠️ `/Inbox/` - Raw input files

## Files NEVER to Push

Check `.gitignore` contains:
```
.env
credentials.json
token.json
.mcp.json
*_session/
*.pem
*.key
*.p12
```

## Output Format

```markdown
## Vault Cleanup Report

**Files Scanned**: N
**Sensitive Files Found**: N

### Needs Attention
| File | Issue | Action |
|------|-------|--------|
| Needs_Action/email_123.md | Contains email address | Redact |
| Pending_Approval/payment.md | Contains bank info | Delete |

### Safe to Push
- Briefings/2026-03-30_Briefing.md
- Plans/PLAN_example.md

### Recommended Action
[What to do next]

### After Cleanup
- Run: git status
- Run: git add .
- Run: git commit -m "Clean vault for GitHub"
- Run: git push
```

## Quick Cleanup Command

```bash
# One-liner to clear sensitive folders
rm -rf AI_Employee_Vault/Needs_Action/*
rm -rf AI_Employee_Vault/Pending_Approval/*
rm -rf AI_Employee_Vault/In_Progress/*
rm -rf AI_Employee_Vault/Logs/*

# Then re-create .gitkeep files
touch AI_Employee_Vault/Needs_Action/.gitkeep
touch AI_Employee_Vault/Pending_Approval/.gitkeep
touch AI_Employee_Vault/In_Progress/.gitkeep
touch AI_Employee_Vault/Logs/.gitkeep
```

## Token Efficiency

- Scans filenames first (fast)
- Reads content only for files with suspicious names
- ~1000-2000 tokens for typical vault

## Related Skills

- `update-dashboard`: Refresh after cleanup
- `end-session`: Create session log after push
