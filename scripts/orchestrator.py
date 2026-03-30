"""
orchestrator.py — Master process for the Personal AI Employee.

This is the "glue" that:
1. Watches folders for changes (Inbox, Approved)
2. Triggers Claude Code when new items appear in /Needs_Action/
3. Monitors /Approved/ and executes approved actions via MCP
4. Runs scheduled tasks (daily briefing, weekly audit)
5. Manages process health

Usage:
    python orchestrator.py [--dry-run] [--once]

    --dry-run   Log intended actions without executing them
    --once      Process once and exit (useful for cron jobs)

Environment variables (.env):
    VAULT_PATH=/path/to/AI_Employee_Vault
    DRY_RUN=false
    CLAUDE_BIN=claude        (path to Claude Code binary)
    MAX_CLAUDE_SESSIONS=3    (max concurrent Claude sessions)
"""

import os
import sys
import json
import time
import signal
import argparse
import subprocess
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread, Event

# ─── Load .env if present ──────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # python-dotenv not installed; use system env vars

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = Path(os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
CLAUDE_BIN = os.getenv("CLAUDE_BIN", "claude")
MAX_CLAUDE_SESSIONS = int(os.getenv("MAX_CLAUDE_SESSIONS", "3"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))  # seconds

# ─── Logging ───────────────────────────────────────────────────────────────────

def setup_logging() -> logging.Logger:
    log_dir = VAULT_PATH / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("Orchestrator")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.handlers.RotatingFileHandler(
        log_dir / "orchestrator.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | ORCHESTRATOR | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = setup_logging()

# ─── Audit Logging ─────────────────────────────────────────────────────────────

def audit_log(action_type: str, details: dict, result: str = "success"):
    """Append an entry to today's audit log (JSON Lines format)."""
    log_dir = VAULT_PATH / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": "orchestrator",
        "dry_run": DRY_RUN,
        "result": result,
        **details,
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ─── Claude Code Trigger ───────────────────────────────────────────────────────

def trigger_claude(prompt: str, timeout: int = 300) -> bool:
    """
    Invoke Claude Code with a prompt pointed at the vault.
    Returns True on success, False on failure.
    """
    if DRY_RUN:
        logger.info(f"[DRY RUN] Would trigger Claude with: {prompt[:80]}...")
        return True

    cmd = [
        CLAUDE_BIN,
        "--print",           # Non-interactive mode
        "--cwd", str(VAULT_PATH),
        prompt
    ]

    logger.info(f"Triggering Claude Code: {prompt[:60]}...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(VAULT_PATH),
        )

        if result.returncode == 0:
            logger.info("Claude completed successfully ✅")
            audit_log("claude_trigger", {"prompt_preview": prompt[:100]}, "success")
            return True
        else:
            logger.error(f"Claude exited with code {result.returncode}")
            logger.error(f"stderr: {result.stderr[:500]}")
            audit_log("claude_trigger", {"prompt_preview": prompt[:100], "error": result.stderr[:200]}, "error")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"Claude timed out after {timeout}s")
        audit_log("claude_trigger", {"prompt_preview": prompt[:100]}, "timeout")
        return False
    except FileNotFoundError:
        logger.error(
            f"Claude Code binary not found at '{CLAUDE_BIN}'. "
            "Install it: npm install -g @anthropic/claude-code"
        )
        return False


# ─── Folder Monitors ──────────────────────────────────────────────────────────

def get_pending_items(folder: str) -> list[Path]:
    """Return all .md files in a vault subfolder."""
    target = VAULT_PATH / folder
    if not target.exists():
        return []
    return sorted(target.glob("*.md"))


def move_to_done(file_path: Path):
    """Move a processed file to /Done/."""
    done_dir = VAULT_PATH / "Done"
    done_dir.mkdir(parents=True, exist_ok=True)
    dest = done_dir / file_path.name
    if not dest.exists():
        file_path.rename(dest)
    else:
        # Avoid collision by adding timestamp
        ts = datetime.now().strftime("%H%M%S")
        dest = done_dir / f"{file_path.stem}_{ts}{file_path.suffix}"
        file_path.rename(dest)
    logger.debug(f"Moved {file_path.name} → /Done/")


# ─── Core Orchestration Tasks ──────────────────────────────────────────────────

def process_needs_action():
    """Check /Needs_Action/ and trigger Claude if items exist."""
    items = get_pending_items("Needs_Action")
    if not items:
        return

    logger.info(f"Found {len(items)} item(s) in /Needs_Action/")

    prompt = (
        "You are my Personal AI Employee. "
        f"There are {len(items)} new item(s) in /Needs_Action/ waiting for your attention. "
        "Please: "
        "1. Read Dashboard.md and Company_Handbook.md for context. "
        "2. Process each item in /Needs_Action/ one by one. "
        "3. For simple tasks: take the appropriate action or draft a response. "
        "4. For complex tasks: create a Plan.md file with checkboxes. "
        "5. For sensitive actions (payments, emails to new contacts, social posts): "
        "   create an approval file in /Pending_Approval/ instead of acting directly. "
        "6. Update Dashboard.md with what you found and did. "
        "7. Move processed files to /Done/. "
        "8. Append all actions to today's log in /Logs/. "
        "Output <promise>TASK_COMPLETE</promise> when all items are processed."
    )

    trigger_claude(prompt)


def process_approved_actions():
    """Check /Approved/ and execute approved actions via MCP."""
    items = get_pending_items("Approved")
    if not items:
        return

    logger.info(f"Found {len(items)} approved action(s) to execute")

    for item in items:
        content = item.read_text(encoding="utf-8")

        # Read the action type from the frontmatter
        action_type = "unknown"
        for line in content.splitlines():
            if line.startswith("action:"):
                action_type = line.split(":", 1)[1].strip()
                break

        logger.info(f"Executing approved action: {action_type} ({item.name})")

        prompt = (
            f"A human has approved the following action. Please execute it now using the appropriate MCP tool. "
            f"The approval file is: /Approved/{item.name}\n\n"
            f"Read the file, execute the action, log the result to /Logs/, "
            f"and move the file to /Done/ when complete. "
            f"If execution fails, move the file to /Needs_Action/ with an error note."
        )

        success = trigger_claude(prompt)
        audit_log(
            "execute_approved_action",
            {"file": item.name, "action_type": action_type},
            "success" if success else "error"
        )


def update_dashboard():
    """Ask Claude to refresh Dashboard.md."""
    prompt = (
        "Please update Dashboard.md with the current status: "
        "count items in Needs_Action/, Pending_Approval/, Approved/, and Done/ (today's files only). "
        "Update the 'Last Updated' timestamp. "
        "Keep the format exactly as it is — only update the values."
    )
    trigger_claude(prompt)


def generate_daily_briefing():
    """Generate the daily summary (runs at 8 AM)."""
    today = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"Generating daily briefing for {today}")

    prompt = (
        f"Please generate the Monday Morning CEO Briefing for {today}. "
        "Read Business_Goals.md, Accounting/Current_Month.md, and all files in /Done/ "
        "from the past 7 days. "
        "Use the template in /Briefings/TEMPLATE_Monday_Briefing.md. "
        f"Save the output as /Briefings/{today}_Daily_Briefing.md. "
        "Then update Dashboard.md with the key metrics from the briefing."
    )
    trigger_claude(prompt)
    audit_log("daily_briefing", {"date": today})


# ─── Scheduler ────────────────────────────────────────────────────────────────

class SimpleScheduler:
    """Minimal scheduler — checks if tasks are due and runs them."""

    def __init__(self):
        self._last_briefing: datetime | None = None
        self._last_dashboard_update: datetime | None = None

    def tick(self):
        now = datetime.now()

        # Daily briefing at 8:00 AM
        if (
            now.hour == 8 and now.minute < 5
            and (self._last_briefing is None or self._last_briefing.date() < now.date())
        ):
            logger.info("⏰ Scheduled: Daily Briefing")
            self._last_briefing = now
            Thread(target=generate_daily_briefing, daemon=True).start()

        # Dashboard update every 30 minutes
        if (
            self._last_dashboard_update is None
            or now - self._last_dashboard_update > timedelta(minutes=30)
        ):
            self._last_dashboard_update = now
            Thread(target=update_dashboard, daemon=True).start()


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main(dry_run: bool = False, once: bool = False):
    global DRY_RUN
    DRY_RUN = dry_run

    if DRY_RUN:
        logger.warning("⚠️  DRY RUN MODE — No real actions will be taken")

    logger.info("🤖 Personal AI Employee Orchestrator starting...")
    logger.info(f"   Vault: {VAULT_PATH}")
    logger.info(f"   Claude binary: {CLAUDE_BIN}")
    logger.info(f"   Check interval: {CHECK_INTERVAL}s")

    scheduler = SimpleScheduler()

    # Handle Ctrl+C gracefully
    stop_event = Event()

    def handle_signal(sig, frame):
        logger.info("Shutdown signal received. Stopping gracefully...")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while not stop_event.is_set():
        try:
            # Core tasks
            process_needs_action()
            process_approved_actions()

            # Scheduled tasks
            scheduler.tick()

        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)

        if once:
            logger.info("--once flag set. Exiting after single run.")
            break

        stop_event.wait(CHECK_INTERVAL)

    logger.info("🛑 Orchestrator stopped.")


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Personal AI Employee — Master Orchestrator"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log actions without executing them",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (useful for cron/Task Scheduler)",
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run, once=args.once)
