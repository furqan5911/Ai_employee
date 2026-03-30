# 🔒 SECURITY.md — GitHub Upload Safety Guide

> **AI Employee Hackathon Submission**
> **Read this BEFORE pushing to GitHub**

---

## 📋 Quick Summary

| File/Folder | Push to GitHub? | Action |
|-------------|-----------------|--------|
| `credentials.json` | ❌ **NEVER** | Already in `.gitignore` |
| `token.json` | ❌ **NEVER** | Already in `.gitignore` |
| `.env` | ❌ **NEVER** | Already in `.gitignore` |
| `.mcp.json` | ❌ **NEVER** | Contains SMTP password |
| `AI_Employee_Vault/Needs_Action/` | ⚠️ **REVIEW** | May contain your emails |
| `AI_Employee_Vault/Pending_Approval/` | ⚠️ **REVIEW** | May have sensitive approvals |
| `AI_Employee_Vault/In_Progress/` | ⚠️ **REVIEW** | Active work items |
| `AI_Employee_Vault/Approved/` | ⚠️ **REVIEW** | Approved actions |
| `AI_Employee_Vault/Logs/` | ⚠️ **REVIEW** | May contain activity data |
| Everything else | ✅ **YES** | Safe to push |

---

## ✅ SAFE to Push (No Review Needed)

### Project Root
| File | Why It's Safe |
|------|---------------|
| `README.md` | Documentation only |
| `CLAUDE.md` | Project instructions |
| `SECURITY.md` | This file |
| `.gitignore` | Prevents secrets from being pushed |
| `.env.example` | Template only (no real credentials) |

### Scripts
| Folder | Why It's Safe |
|--------|---------------|
| `scripts/*.py` | All Python code — no credentials |
| `email_mcp_server.py` | Code only — credentials in `.mcp.json` |
| `*.bat`, `*.ps1` | Management scripts — no secrets |

### AI_Employee_Vault (Safe Subfolders)
| Folder | Why It's Safe |
|--------|---------------|
| `Dashboard.md` | Status dashboard only |
| `Company_Handbook.md` | Business rules only |
| `Business_Goals.md` | Your targets only |
| `Briefings/` | Generated reports |
| `Done/` | Completed tasks (sanitized) |
| `Accounting/` | Financial logs (if sanitized) |

---

## ⚠️ REVIEW Before Pushing

### Needs_Action Folder
**Risk**: May contain emails from your contacts, including:
- Email addresses
- Message content
- Personal information

**Action**: Review each file. Consider:
- Removing personal email addresses
- Redacting sensitive content
- Deleting the folder entirely before pushing

### Pending_Approval Folder
**Risk**: May contain:
- Draft emails to external parties
- Payment requests
- Approval requests with sensitive details

**Action**: Review each file. Consider:
- Removing recipient email addresses
- Redacting payment amounts
- Deleting the folder entirely before pushing

### Logs Folder
**Risk**: `*.jsonl` files may contain:
- Email addresses
- Activity patterns
- Timestamps of your actions

**Action**: Consider deleting all `Logs/*.jsonl` files before pushing.

---

## ❌ NEVER Push (Protected by .gitignore)

These files are already in `.gitignore` and **will NOT be pushed** to GitHub:

| File | Contains | Protected By |
|------|----------|--------------|
| `credentials.json` | Gmail API secrets | `.gitignore` |
| `token.json` | Gmail OAuth token | `.gitignore` |
| `.env` | All environment variables/secrets | `.gitignore` |
| `.mcp.json` | SMTP credentials | Not in `.gitignore` — **DELETE before push!** |
| `*_session/` | Session files | `.gitignore` |
| `*.pem`, `*.key`, `*.p12` | Certificates and keys | `.gitignore` |

---

## 🚨 CRITICAL: .mcp.json

**The `.mcp.json` file contains your SMTP password and is NOT in `.gitignore`!**

**Before pushing to GitHub:**

```bash
# Option 1: Delete .mcp.json (you'll need to recreate it later)
rm .mcp.json

# Option 2: Add to .gitignore then delete
echo ".mcp.json" >> .gitignore
rm .mcp.json
```

---

## 📝 Pre-Push Checklist

Run this checklist before `git push`:

- [ ] **1. Delete `.mcp.json`** (or add to `.gitignore`)
- [ ] **2. Review `AI_Employee_Vault/Needs_Action/`** — remove sensitive emails
- [ ] **3. Review `AI_Employee_Vault/Pending_Approval/`** — redact sensitive info
- [ ] **4. Delete `AI_Employee_Vault/Logs/*.jsonl`** — audit logs may contain data
- [ ] **5. Verify `.gitignore` contains:**
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
- [ ] **6. Run `git status`** — verify no sensitive files are staged**
  ```bash
  git status
  # Look for: credentials.json, token.json, .env, .mcp.json
  # If you see them: git reset <filename>
  ```

---

## 🔍 How to Verify Your Push is Safe

```bash
# Check what will be pushed
git diff --cached --name-only

# Check if .mcp.json is in the commit
git log --all --full-history -- ".mcp.json"

# If .mcp.json appears in history, you must remove it:
# WARNING: This rewrites history — only do this BEFORE pushing
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .mcp.json" \
  --prune-empty --tag-name-filter cat -- --all
```

---

## 📞 If You Accidentally Pushed Credentials

If you accidentally pushed `credentials.json`, `token.json`, or `.mcp.json`:

1. **Immediately** delete the files from the repo
2. **Revoke** the Gmail App Password: https://myaccount.google.com/apppasswords
3. **Revoke** the OAuth token: https://myaccount.google.com/permissions
4. **Regenerate** credentials and reconfigure locally
5. **Consider** the repository compromised — contact GitHub support if needed

---

## 🏆 Safe Repository Structure

After cleaning, your GitHub repo should look like:

```
ai employee/
├── README.md                   ✅
├── CLAUDE.md                   ✅
├── SECURITY.md                 ✅
├── .gitignore                  ✅
├── .env.example                ✅
│
├── scripts/                    ✅
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   ├── approval_executor.py
│   └── ...
│
├── email_mcp_server.py         ✅
│
├── AI_Employee_Vault/          ✅ (selective)
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── Briefings/
│   └── Done/
│
└── *.bat, *.ps1                ✅
```

**NOT in GitHub (protected by .gitignore or deleted):**
- ❌ .mcp.json
- ❌ credentials.json
- ❌ token.json
- ❌ .env
- ❌ Needs_Action/
- ❌ Pending_Approval/
- ❌ Logs/

---

*Created for Panaversity Personal AI Employee Hackathon 0 — 2026*
*Silver Tier Submission*
