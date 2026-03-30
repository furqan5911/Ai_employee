# tier-upgrade

Track progress toward next hackathon tier and provide specific implementation steps.

## Trigger

Use this skill when:
- User asks: "what's next", "upgrade tier", "tier status", "gold tier", "platinum tier"
- User wants to move to next tier (Bronze→Silver→Gold→Platinum)
- User asks: "what do I need for [tier] tier"
- User says: "help me reach [tier] tier"

## When NOT to Use

- DO NOT use if user is working on a specific task (let them finish)
- DO NOT use automatically on session start (use ai-status instead)
- DO NOT use if current tier is not complete (finish current tier first)

## Tier Requirements Reference

### Bronze Tier (Foundation) ✅
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher script (Gmail OR file system)
- Claude Code reading from and writing to vault
- Basic folder structure: /Inbox, /Needs_Action, /Done
- All AI functionality as Agent Skills

### Silver Tier (Functional Assistant) ✅
- All Bronze requirements
- Two or more Watcher scripts (Gmail + FileSystem)
- Email MCP server for sending emails
- Human-in-the-loop approval workflow
- Basic scheduling via cron/Task Scheduler
- Context-aware email replies

### Gold Tier (Autonomous Employee) 🟡
- All Silver requirements
- WhatsApp Watcher (Playwright-based)
- LinkedIn auto-post integration
- Multiple MCP servers for different action types
- Full weekly CEO briefing with real data
- Ralph Wiggum loop for autonomous multi-step tasks
- Odoo Community accounting integration (optional)
- Facebook/Instagram/Twitter integration

### Platinum Tier (Always-On Cloud) 🔴
- All Gold requirements
- Cloud VM (Oracle/AWS/GCP) for 24/7 operation
- Cloud/local sync mechanism
- Work-zone specialization (cloud vs local)
- Cloud owns: email triage + draft replies
- Local owns: approvals, payments, final sends
- Odoo on Cloud VM with HTTPS
- Health monitoring and auto-restart

## Instructions

1. **Check current tier status**
   - Read CLAUDE.md for tier progress
   - Read Dashboard.md for recent work
   - Identify which tier we're currently on

2. **Show next tier requirements**
   - List what's needed for next tier
   - Mark what's already done
   - Mark what's pending

3. **Provide implementation guide**
   - Suggest order of implementation
   - Identify dependencies (what must be done first)
   - Estimate time for each component

4. **Offer to start**
   - "Ready to start with [component]?"
   - Create plan if user agrees

## Output Format

```markdown
## Tier Upgrade Progress

**Current Tier**: [Bronze/Silver/Gold/Platinum] ([X]%)
**Next Target**: [Next tier name]

### What's Complete
- ✅ [Component 1]
- ✅ [Component 2]

### What's Needed for [Next Tier]
- [ ] [Component 1] - [brief description]
- [ ] [Component 2] - [brief description]
- [ ] [Component 3] - [brief description]

### Suggested Order
1. **[Component 1]** ([estimate time])
   - [Step 1]
   - [Step 2]

2. **[Component 2]** ([estimate time])
   - [Step 1]
   - [Step 2]

### Ready to Start?
Type "start [component]" to begin, or ask for more details.
```

## Gold Tier Implementation Guide

### WhatsApp Watcher (2-3 hours)
```bash
# Install Playwright
pip install playwright
playwright install chromium

# Create scripts/whatsapp_watcher.py
# - Uses WhatsApp Web (headless)
# - Monitors for keywords: urgent, invoice, payment, help
# - Creates action files in Needs_Action/
```

### LinkedIn Auto-Post (3-4 hours)
```bash
# Create LinkedIn MCP server
# - Uses LinkedIn API or Playwright automation
# - Posts scheduled content from Needs_Action/
# - Requires approval before posting
```

### Ralph Wiggum Loop (2 hours)
```bash
# Already have scripts/ralph_wiggum.py
# - Integrate with exec-plan skill
# - Configure stop hook in Claude Code settings
```

### CEO Briefing (2-3 hours)
```bash
# Enhance generate-briefing skill
# - Read Business_Goals.md
# - Scan Accounting/ for revenue data
# - Analyze Done/ for completed tasks
# - Generate executive summary
```

## Platinum Tier Implementation Guide

### Cloud VM Setup (4-6 hours)
```bash
# 1. Create Oracle Cloud Free Tier VM
# 2. Install: Python, Node.js, Claude Code API
# 3. Set up watchers on cloud
# 4. Configure git sync for vault
```

### Cloud/Local Sync (3-4 hours)
```bash
# 1. Set up git repo for vault
# 2. Cloud pushes to /Updates/ branch
# 3. Local merges into main vault
# 4. Use claim-by-move for task ownership
```

## Token Efficiency

- Single skill invocation (~500 tokens)
- Avoids reading entire hackathon document
- Provides actionable next steps

## Related Skills

- `create-plan`: Create plan for tier component
- `exec-plan`: Execute tier upgrade plan
- `ai-status`: Quick status check
