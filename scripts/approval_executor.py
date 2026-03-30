"""
approval_executor.py — Watches /Approved/ folder and executes approved actions.

This is the "Hands" of the AI Employee — it takes human-approved actions
and actually executes them via MCP or direct API calls.

Usage:
    python approval_executor.py

Security:
    - ONLY processes files in /Approved/
    - NEVER auto-approves anything
    - Logs every action taken
    - Respects DRY_RUN mode
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
)
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            Path(__file__).parent.parent / "AI_Employee_Vault" / "Logs" / "approval_executor.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ApprovalExecutor")

# ─── Action Executors ────────────────────────────────────────────────────────────


def execute_email_approval(approval_file: Path, dry_run: bool = True):
    """
    Execute an approved email action.

    In Silver Tier, this creates a draft or logs the action.
    Full email sending requires Email MCP server.
    """
    content = approval_file.read_text(encoding="utf-8")

    # Extract details from frontmatter
    to = ""
    subject = ""
    body = ""

    for line in content.split("\n"):
        if line.startswith("to:") or line.startswith("recipient:"):
            to = line.split(":", 1)[1].strip()
        elif line.startswith("subject:") or line.startswith("subject / reference:"):
            subject = line.split(":", 1)[1].strip()
        elif "details" in line.lower():
            # Body starts after this
            idx = content.index("## Details")
            body_section = content[idx:].split("##")[1]
            body = body_section.strip()

    action_log = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "email_sent",
        "recipient": to,
        "subject": subject,
        "dry_run": dry_run,
        "result": "drafted" if dry_run else "sent"
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would send email to: {to}")
        logger.info(f"[DRY RUN] Subject: {subject}")
        logger.info(f"[DRY RUN] Email NOT sent (DRY_RUN=true)")
        action_log["status"] = "dry_run"
    else:
        logger.info(f"[PRODUCTION] Sending email to: {to}")
        logger.info(f"[PRODUCTION] Subject: {subject}")
        # TODO: Call Email MCP here
        logger.warning("[PRODUCTION] Email MCP not configured - would send email")
        action_log["status"] = "mcp_not_configured"

    return action_log


def execute_payment_approval(approval_file: Path, dry_run: bool = True):
    """
    Execute an approved payment action.

    ALWAYS requires approval - this is a safety function.
    """
    content = approval_file.read_text(encoding="utf-8")

    amount = ""
    recipient = ""

    for line in content.split("\n"):
        if "amount:" in line.lower():
            amount = line.split(":", 1)[1].strip()
        elif "recipient:" in line.lower():
            recipient = line.split(":", 1)[1].strip()

    action_log = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "payment_made",
        "recipient": recipient,
        "amount": amount,
        "dry_run": dry_run,
        "result": "drafted" if dry_run else "paid"
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would make payment to: {recipient}")
        logger.info(f"[DRY RUN] Amount: {amount}")
        logger.info(f"[DRY RUN] Payment NOT made (DRY_RUN=true)")
        action_log["status"] = "dry_run"
    else:
        logger.info(f"[PRODUCTION] Processing payment to: {recipient}")
        logger.info(f"[PRODUCTION] Amount: {amount}")
        # TODO: Call Payment MCP here
        logger.warning("[PRODUCTION] Payment MCP not configured - would process payment")
        action_log["status"] = "mcp_not_configured"

    return action_log


def execute_social_post_approval(approval_file: Path, dry_run: bool = True):
    """
    Execute an approved social media post.
    """
    content = approval_file.read_text(encoding="utf-8")

    platform = ""
    post_content = ""

    for line in content.split("\n"):
        if "platform:" in line.lower():
            platform = line.split(":", 1)[1].strip()

    # Extract the post content
    if "## Details" in content:
        idx = content.index("## Details")
        post_content = content[idx:].split("##")[1].strip()

    action_log = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "social_post",
        "platform": platform,
        "dry_run": dry_run,
        "result": "drafted" if dry_run else "posted"
    }

    if dry_run:
        logger.info(f"[DRY RUN] Would post to {platform}")
        logger.info(f"[DRY RUN] Content: {post_content[:100]}...")
        logger.info(f"[DRY RUN] Post NOT made (DRY_RUN=true)")
        action_log["status"] = "dry_run"
    else:
        logger.info(f"[PRODUCTION] Posting to {platform}")
        # TODO: Call Social MCP here
        logger.warning(f"[PRODUCTION] Social MCP not configured for {platform}")
        action_log["status"] = "mcp_not_configured"

    return action_log


# ─── Main Executor Loop ─────────────────────────────────────────────────────────

ACTION_EXECUTORS = {
    "email": execute_email_approval,
    "payment": execute_payment_approval,
    "social_post": execute_social_post_approval,
}


def determine_action_type(approval_file: Path) -> str:
    """Determine the action type from the filename or content."""
    filename = approval_file.name.lower()

    if filename.startswith("email_"):
        return "email"
    elif filename.startswith("payment_"):
        return "payment"
    elif filename.startswith("social_"):
        return "social_post"
    elif filename.startswith("post_"):
        return "social_post"

    # Check content for action type
    try:
        content = approval_file.read_text(encoding="utf-8")
        if "action: email" in content.lower():
            return "email"
        elif "action: payment" in content.lower():
            return "payment"
        elif "action: social" in content.lower():
            return "social_post"
    except:
        pass

    return "unknown"


def execute_approved_action(approval_file: Path) -> dict:
    """Execute an approved action and return the result."""
    action_type = determine_action_type(approval_file)

    logger.info(f"Processing approved action: {approval_file.name}")
    logger.info(f"Action type: {action_type}")

    executor = ACTION_EXECUTORS.get(action_type)

    if not executor:
        logger.warning(f"No executor for action type: {action_type}")
        return {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "status": "no_executor",
            "file": str(approval_file)
        }

    try:
        result = executor(approval_file, dry_run=DRY_RUN)
        result["file"] = str(approval_file)
        return result
    except Exception as e:
        logger.error(f"Error executing action: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "status": "error",
            "error": str(e),
            "file": str(approval_file)
        }


def move_to_done(approval_file: Path, result: dict):
    """Move the approval file to /Done/ with execution result."""
    done_folder = Path(VAULT_PATH) / "Done"
    done_folder.mkdir(parents=True, exist_ok=True)

    # Create done filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    done_filename = f"DONE_{timestamp}_{approval_file.name}"
    done_path = done_folder / done_filename

    # Append execution result to the file
    content = approval_file.read_text(encoding="utf-8")
    result_section = f"""

---

## Execution Result

**Executed at**: {datetime.now().isoformat()}
**Status**: {result.get('status', 'unknown')}
**Dry Run**: {DRY_RUN}

```json
{json.dumps(result, indent=2)}
```
"""

    done_path.write_text(content + result_section, encoding="utf-8")

    # Delete original and move to done
    approval_file.unlink()
    logger.info(f"Moved to /Done/: {done_filename}")


def write_audit_log(result: dict):
    """Append execution result to today's audit log."""
    logs_dir = Path(VAULT_PATH) / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{today}.jsonl"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(result) + "\n")


def run():
    """Main loop: watch /Approved/ and execute actions."""
    approved_folder = Path(VAULT_PATH) / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("APPROVAL EXECUTOR STARTED")
    logger.info("=" * 60)
    logger.info(f"Vault: {VAULT_PATH}")
    logger.info(f"Watch folder: {approved_folder}")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    logger.info(f"DRY_RUN: {DRY_RUN}")
    logger.info("=" * 60)
    logger.info("Watching for approved actions...")

    processed_hashes = set()

    while True:
        try:
            # List all files in /Approved/
            approval_files = [
                f for f in approved_folder.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ]

            if approval_files:
                logger.info(f"Found {len(approval_files)} approved action(s)")

                for approval_file in approval_files:
                    # Use file hash to avoid double-processing
                    file_hash = f"{approval_file.name}_{approval_file.stat().st_mtime}"
                    if file_hash in processed_hashes:
                        continue

                    try:
                        # Execute the action
                        result = execute_approved_action(approval_file)

                        # Write audit log
                        write_audit_log(result)

                        # Move to Done
                        move_to_done(approval_file, result)

                        processed_hashes.add(file_hash)

                    except Exception as e:
                        logger.error(f"Error processing {approval_file.name}: {e}")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Stopping...")
            logger.info("=" * 60)
            logger.info("APPROVAL EXECUTOR STOPPED")
            logger.info("=" * 60)
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            time.sleep(10)


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("[APPROVAL EXECUTOR]")
    print(f"  Vault: {VAULT_PATH}")
    print(f"  Watch folder: {Path(VAULT_PATH) / 'Approved'}")
    print(f"  DRY_RUN: {DRY_RUN}")
    print(f"  Check interval: {CHECK_INTERVAL}s")
    print(f"  Press Ctrl+C to stop")
    print()
    print("Waiting for approved actions...")
    print()

    run()
