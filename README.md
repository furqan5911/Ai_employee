# 🤖 Personal AI Employee — Silver Tier

> **Tagline**: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.
>
> Built for the **Panaversity Personal AI Employee Hackathon 0 — 2026**
>
> **Tier**: 🥈 **SILVER TIER** — Functional Assistant

---

## 🎯 What Is This?

A **Digital FTE (Full-Time Equivalent)** — an AI agent powered by Claude Code that proactively manages your personal and business affairs 24/7, using your local Obsidian vault as its brain and file system.

| Feature | Human FTE | This AI Employee |
|---------|-----------|-----------------|
| **Availability** | 40 hrs/week | 168 hrs/week (24/7) |
| **Monthly Cost** | $4,000–$8,000+ | ~$20 in API costs |
| **Consistency** | 85–95% | 99%+ |
| **Ramp-up Time** | 3–6 months | Minutes |
| **Annual Hours** | ~2,000 hours | ~8,760 hours |

---

## 🏆 Silver Tier Features

✅ **All Bronze Features** plus:
- ✅ **Gmail Integration** — Monitors Gmail, creates action files for important emails
- ✅ **Email MCP Server** — Sends/replies to emails automatically
- ✅ **Context-Aware Replies** — Understands email content, drafts intelligent responses
- ✅ **Human-in-the-Loop (HITL)** — Approval workflow for sensitive actions
- ✅ **Auto-Reply to Known Contacts** — Replies to you automatically
- ✅ **Scheduled Tasks** — Windows Task Scheduler integration
- ✅ **Audit Logging** — Every action logged and reviewable

---

## 🏗️ Architecture (Silver Tier)

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SOURCES                           │
├─────────────────┬─────────────────┬─────────────────────────────┤
│     Gmail       │    Files       │     (Future: WhatsApp)    │
└────────┬────────┴────────┬────────┴─────────┬─────────────────────┘
         │                 │                  │
         ▼                 ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Gmail Watcher│ │FileSystemWatch│ │     (Future) │            │
│  │  (Python)    │ │   (Python)   │ │             │            │
│  └──────┬───────┘ └──────┬───────┘ └──────────────┘            │
└─────────┼────────────────┼────────────────────────────────────┘
          │                │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Local)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ /Needs_Action/  │ /Pending_Approval/ │  /Approved/     │  │
│  │ /In_Progress/   │ /Rejected/        │  /Done/        │  │
│  │ Dashboard.md    │ Company_Handbook.md │ Business_Goals.md│  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                      CLAUDE CODE                          │ │
│  │   Read → Think → Plan → Write → Request Approval          │ │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
          ┌────────────────┴────────────────┐
          ▼                                  ▼
┌────────────────────────────┐    ┌────────────────────────────────┐
│    HUMAN-IN-THE-LOOP       │    │         ACTION LAYER           │
│  Review approval files    │    │  ┌─────────────────────────┐   │
│  Move to /Approved        │────┼─▶│  │    Email MCP Server        │   │
│                            │    │  │  (sends replies)         │   │
└────────────────────────────┘    │  └─────────────────────────┘   │
                                     │
                                     ▼
                         ┌────────────────────────────────┐
                         │     EXTERNAL ACTIONS           │
                         │  Send emails → Gmail          │
                         └────────────────────────────────┘
```

---

## 📁 Project Structure

```
ai employee/
├── README.md                   ← This file
├── .gitignore                  ← Security: keeps secrets out of git
├── SECURITY.md                 ← ⚠️ What's SAFE to push to GitHub
│
├── CLAUDE.md                   ← AI Employee's brain stem
├── .env.example                ← Environment template (DO NOT use real .env)
│
├── .mcp.json                   ← Email MCP server configuration
│
├── email_mcp_server.py         ← Custom Email MCP server (Silver)
│
├── scripts/                    ← All watcher and automation scripts
│   ├── base_watcher.py        ← Base class for all watchers
│   ├── filesystem_watcher.py  ← File system monitoring (Bronze)
│   ├── gmail_watcher.py       ← Gmail monitoring (Silver) ✅
│   ├── approval_executor.py    ← Executes approved actions (Silver) ✅
│   ├── scheduler_tasks.py      ← Scheduled task runners (Silver) ✅
│   ├── orchestrator.py         ← Master orchestrator
│   ├── ralph_wiggum.py         ← Stop hook for persistence
│   └── audit_logger.py         ← Centralized logging
│
├── AI_Employee_Vault/           ← Obsidian Vault (SAFE to push)
│   ├── Dashboard.md             ← Live status board
│   ├── Company_Handbook.md      ← Rules of engagement
│   ├── Business_Goals.md        ← KPIs, targets
│   │
│   ├── Inbox/                   ← Drop files for processing
│   ├── Needs_Action/            └── ⚠️ May have your emails (review first)
│   ├── In_Progress/             └── ⚠️ May have active work
│   ├── Pending_Approval/        └── ⚠️ May have sensitive approvals
│   ├── Approved/                └── ⚠️ May have approved actions
│   ├── Done/                    ← ✅ Safe (completed tasks)
│   │
│   ├── Accounting/              ← Financial logs
│   ├── Briefings/               ← Generated briefings
│   └── Logs/                    ← Audit trail (⚠️ May contain activity data)
│
├── credentials.json             ← ⚠️ DO NOT PUSH (Gmail API)
├── token.json                   ← ⚠️ DO NOT PUSH (Gmail OAuth token)
│
└── setup_windows_scheduler_test.ps1      ← Testing mode (1-2 min intervals)
├── setup_windows_scheduler.ps1            ← Production mode (hourly/daily)
├── STOP_AI_EMPLOYEE.bat                   ← Stop all tasks
└── ENABLE_TEST_TASKS.bat                 ← Resume tasks
```

---

## 🚀 Quick Start (Silver Tier)

### Prerequisites

| Tool | Required Version | Installation |
|------|-----------------|--------------|
| Claude Code | Latest | `npm install -g @anthropic/claude-code` |
| Python | 3.13+ | `python --version` |
| MCP Python SDK | Latest | `pip install mcp` |
| Obsidian | 1.10.6+ | Download from obsidian.md |

### Setup Steps

#### 1. Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd ai employee

# Install dependencies
pip install mcp

# Copy environment template
cp .env.example .env
# Edit .env with your actual values (DO NOT commit .env)
```

#### 2. Configure Gmail (Optional - for email monitoring)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable Gmail API
3. Create OAuth 2.0 credentials → Download as `credentials.json`
4. Run Gmail setup:
   ```bash
   python scripts/setup_gmail.py
   ```

#### 3. Configure Email MCP

Edit `.mcp.json` with your Gmail credentials:
```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": ["C:\\Users\\path\\to\\email_mcp_server.py"],
      "env": {
        "SMTP_SERVER": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "your-email@gmail.com",
        "SMTP_PASSWORD": "your-app-password",
        "EMAIL_FROM": "your-email@gmail.com"
      }
    }
  }
}
```

> **Security**: Your credentials stay in `.mcp.json` locally and are NOT pushed to GitHub (see `.gitignore`).

#### 4. Start the System

```bash
# Run Gmail watcher (manual mode for testing)
python scripts/gmail_watcher.py --once

# Or enable scheduled tasks (production)
.\setup_windows_scheduler.ps1
```

#### 5. Process Emails

When emails arrive:
1. **From you (known contact)** → AI replies automatically ✅
2. **From new person** → AI creates approval file → You approve → AI sends ✅

---

## 🔒 Security & GitHub Safety

### ✅ SAFE to Push to GitHub:

| Folder/File | Safe to Push? | Notes |
|------------|----------------|-------|
| `AI_Employee_Vault/Dashboard.md` | ✅ Yes | Status dashboard only |
| `AI_Employee_Vault/Company_Handbook.md` | ✅ Yes | Business rules |
| `AI_Employee_Vault/Business_Goals.md` | ✅ Yes | Your targets |
| `AI_Employee_Vault/Briefings/` | ✅ Yes | Generated reports |
| `AI_Employee_Vault/Done/` | ✅ Yes | Completed tasks |
| `scripts/` | ✅ Yes | All Python scripts |
| `CLAUDE.md` | ✅ Yes | Project instructions |
| `README.md` | ✅ Yes | This file |
| `SECURITY.md` | ✅ Yes | Security guide |
| `.gitignore` | ✅ Yes | Keeps secrets out |

### ⚠️ REVIEW Before Pushing:

| Folder/File | Safe? | Action Required |
|------------|-------|----------------|
| `AI_Employee_Vault/Needs_Action/` | ⚠️ REVIEW | May contain your emails |
| `AI_Employee_Vault/In_Progress/` | ⚠️ REVIEW | Active work items |
| `AI_Employee_Vault/Pending_Approval/` | ⚠️ REVIEW | May have sensitive approvals |
| `AI_Employee_Vault/Approved/` | ⚠️ REVIEW | Approved actions |
| `AI_Employee_Vault/Logs/` | ⚠️ REVIEW | May contain activity data |
| `credentials.json` | ❌ NO | Contains Gmail API secrets |
| `token.json` | ❌ NO | Contains OAuth token |
| `.env` | ❌ NO | Contains all secrets |

### 🔒 Protected by .gitignore:

```
.env                          ← All your credentials
credentials.json              ← Gmail API secrets
token.json                    ← Gmail OAuth token
*_session/                   ← Session files
*.pem, *.key, *.p12          ← Certificates and keys
```

---

## 📊 Features & Capabilities

### Email Automation

| Scenario | Automation | Example |
|----------|------------|---------|
| **Email from YOU arrives** | ✅ Auto-reply | You: "Status?" → AI: "All systems operational!" |
| **Client asks for invoice** | ✅ Auto-reply (if known) | Client: "Send invoice #123" → AI: Attaches and sends |
| **Unknown person emails** | ⚠️ Approval required | Creates approval → You approve → AI sends |
| **Payment request >$50** | ⚠️ Approval required | Creates approval → You approve → AI pays |

### Scheduling

| Task | Interval | Status |
|------|----------|--------|
| Gmail Check | Every 2 minutes | ✅ Working |
| Inbox Scan | Every 1 minute | ✅ Working |
| Dashboard Refresh | Every 2 minutes | ✅ Working |

---

## 🧪 Testing

### Manual Testing

```bash
# Test Gmail watcher
python scripts/gmail_watcher.py --once

# Test email sending
python -c "
from email_mcp_server import send_email
import asyncio
asyncio.run(send_email('you@email.com', 'Test', 'Body'))
"

# Test scheduler task
python scripts/scheduler_tasks.py dashboard_refresh
```

### Stop/Start Tasks

| Action | Command |
|--------|---------|
| **Stop all** | `STOP_AI_EMPLOYEE.bat` |
| **Resume** | `ENABLE_TEST_TASKS.bat` |
| **Remove tasks** | `remove_tasks_test.ps1` |

---

## 📝 Agent Skills

All AI functionality is implemented as Claude Code Agent Skills:

| Skill | Purpose |
|-------|---------|
| `process-inbox` | Scan and prioritize `/Needs_Action/` |
| `create-plan` | Generate multi-step task plans |
| `request-approval` | Create HITL approval files |
| `update-dashboard` | Refresh `Dashboard.md` |
| `generate-briefing` | Create CEO briefings |
| `audit-log` | Append to audit log |
| `file-watcher` | Manual `/Inbox/` scan |

---

## 🎯 Hackathon Submission

**Tier Declared**: 🥈 **SILVER TIER**

**Submit Form**: https://forms.gle/JR9T1SJq5rmQyGkGA

### Judging Criteria Compliance

| Criteria | Weight | Status |
|----------|--------|--------|
| **Functionality** (30%) | ✅ | All core features working |
| **Innovation** (25%) | ✅ | Email MCP + context-aware replies |
| **Practicality** (20%) | ✅ | Actually usable daily |
| **Security** (15%) | ✅ | HITL safeguards + credential protection |
| **Documentation** (10%) | ✅ | Complete docs + setup guide |

---

## 📚 Resources

| Resource | Link |
|----------|------|
| Claude Code Docs | https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows |
| MCP Introduction | https://modelcontextprotocol.io/introduction |
| Hackathon Guide | https://docs.google.com/document/d/1ofTMR1IE7jEMvXM-rdsGXy6unI4DLS_gc6dmZo8WPkI |
| Wednesday Zoom | https://us06web.zoom.us/j/87188707642 (passcode: 744832) |

---

## 🏆 Tier Completion Status

| Tier | Status | Completion |
|------|--------|------------|
| 🥉 **Bronze** | ✅ Complete | 100% |
| 🥈 **Silver** | ✅ Complete | 100% |
| 🥇 **Gold** | 🔴 Not Started | 0% |
| 💎 **Platinum** | 🔴 Not Started | 0% |

---

## 📞 Support

- **Issues**: Check `SECURITY.md` for common issues
- **Questions**: Join Wednesday Zoom meetings
- **Updates**: Check `Briefings/` folder for latest status

---

## 📄 License

MIT License - See LICENSE file for details

---

*Built with ❤️ using Claude Code | Panaversity Hackathon 0 — 2026*
*Silver Tier — Fully Functional Personal AI Employee*
