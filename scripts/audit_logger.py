"""
audit_logger.py — Centralized audit logging for all AI Employee actions.

Import this in any script that takes actions on behalf of the AI Employee.

Usage:
    from audit_logger import log_action

    log_action(
        action_type="email_send",
        target="client@example.com",
        parameters={"subject": "Invoice #123"},
        approval_status="approved",
        approved_by="human",
        result="success"
    )
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path(os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
))

logger = logging.getLogger("AuditLogger")


def log_action(
    action_type: str,
    target: str = "",
    parameters: dict = None,
    approval_status: str = "auto",
    approved_by: str = "system",
    result: str = "success",
    error_message: str = "",
    actor: str = "claude_code",
) -> dict:
    """
    Append a structured audit log entry to today's JSONL log file.

    Args:
        action_type:     Type of action (email_send, payment, file_create, etc.)
        target:          What was acted upon (email address, file path, etc.)
        parameters:      Dict of action-specific parameters
        approval_status: 'approved', 'auto', 'pending', 'rejected'
        approved_by:     'human', 'system', 'auto'
        result:          'success', 'error', 'skipped', 'dry_run'
        error_message:   Error details if result is 'error'
        actor:           Who performed the action

    Returns:
        The log entry dict
    """
    log_dir = VAULT_PATH / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "actor": actor,
        "target": target,
        "parameters": parameters or {},
        "approval_status": approval_status,
        "approved_by": approved_by,
        "result": result,
    }

    if error_message:
        entry["error"] = error_message

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    # Also log to Python logger
    log_level = logging.INFO if result == "success" else logging.WARNING
    logger.log(log_level, f"[AUDIT] {action_type} → {result} | target: {target}")

    return entry


def get_today_log() -> list[dict]:
    """Read today's audit log entries."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = VAULT_PATH / "Logs" / f"{today}.jsonl"

    if not log_file.exists():
        return []

    entries = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    return entries


def get_action_summary(date: str = None) -> dict:
    """Summarize actions for a given date (default: today)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    log_file = VAULT_PATH / "Logs" / f"{date}.jsonl"

    if not log_file.exists():
        return {"date": date, "total": 0, "by_type": {}, "errors": 0}

    entries = []
    for line in log_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    by_type = {}
    errors = 0
    for entry in entries:
        t = entry.get("action_type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        if entry.get("result") == "error":
            errors += 1

    return {
        "date": date,
        "total": len(entries),
        "by_type": by_type,
        "errors": errors,
        "success_rate": f"{((len(entries) - errors) / max(len(entries), 1)) * 100:.1f}%",
    }


if __name__ == "__main__":
    # Test the audit logger
    entry = log_action(
        action_type="test",
        target="audit_logger.py",
        parameters={"test": True},
        result="success",
        approved_by="developer",
    )
    print(f"✅ Test log entry created: {entry}")
    print(f"📊 Today's summary: {get_action_summary()}")
