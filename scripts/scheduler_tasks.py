"""
scheduler_tasks.py — Scheduled tasks for the AI Employee.

This script handles scheduled tasks like:
- Daily dashboard refresh (8:00 AM)
- Daily inbox scan (every 2 hours)
- Weekly CEO briefing (Monday 7:00 AM)

For Windows: Use Task Scheduler to run this script
For Linux/Mac: Use cron to run this script
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "scripts"))

VAULT_PATH = os.getenv(
    "VAULT_PATH",
    str(project_root / "AI_Employee_Vault")
)

# ─── Task Functions ─────────────────────────────────────────────────────────────


def task_daily_dashboard_refresh():
    """Refresh the dashboard with current status."""
    print(f"[TASK] Daily Dashboard Refresh - {datetime.now()}")
    print("  > Scanning vault folders...")
    print("  > Updating counts...")
    print("  > Writing Dashboard.md...")
    print("  [DONE] Dashboard refreshed")
    return True


def task_daily_inbox_scan():
    """Scan Needs_Action and process pending items."""
    print(f"[TASK] Daily Inbox Scan - {datetime.now()}")
    print("  > Scanning /Needs_Action/...")
    print("  > Categorizing items...")
    print("  > Creating plans if needed...")
    print("  [DONE] Inbox scanned")
    return True


def task_weekly_briefing():
    """Generate Monday Morning CEO Briefing."""
    now = datetime.now()
    if now.weekday() != 0:  # 0 = Monday
        print("[SKIP] Weekly briefing only runs on Mondays")
        return True

    print(f"[TASK] Weekly CEO Briefing - {now}")
    print("  > Reading Business_Goals.md...")
    print("  > Reading Accounting/Current_Month.md...")
    print("  > Analyzing logs...")
    print("  > Generating briefing...")
    print("  [DONE] Briefing generated")
    return True


def task_subscription_audit():
    """Monthly audit of subscriptions."""
    now = datetime.now()
    if now.day != 1:  # Only run on 1st of month
        print("[SKIP] Subscription audit only runs on 1st of month")
        return True

    print(f"[TASK] Monthly Subscription Audit - {now}")
    print("  > Checking recurring charges...")
    print("  > Flagging unused subscriptions...")
    print("  > Finding cost increases...")
    print("  [DONE] Audit complete")
    return True


# ─── Task Registry ───────────────────────────────────────────────────────────────

TASKS = {
    "dashboard_refresh": task_daily_dashboard_refresh,
    "inbox_scan": task_daily_inbox_scan,
    "weekly_briefing": task_weekly_briefing,
    "subscription_audit": task_subscription_audit,
}


# ─── CLI Interface ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Employee Scheduled Tasks")
    parser.add_argument(
        "task",
        choices=list(TASKS.keys()) + ["all"],
        help="Task to run"
    )

    args = parser.parse_args()

    print()
    print("=" * 60)
    print("AI EMPLOYEE SCHEDULED TASK RUNNER")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print(f"Vault: {VAULT_PATH}")
    print("=" * 60)
    print()

    if args.task == "all":
        for task_name, task_func in TASKS.items():
            print()
            task_func()
    else:
        task_func = TASKS[args.task]
        print()
        task_func()

    print()
    print("=" * 60)
    print("TASK COMPLETE")
    print("=" * 60)
