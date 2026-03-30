"""
watchdog.py — Health monitor for the Personal AI Employee.

Monitors critical processes and restarts them if they crash.
This is the "always-on" guardian that keeps your AI Employee alive.

Usage:
    python watchdog.py

Keep this running in a separate terminal (or via PM2/systemd).
It will automatically restart any crashed watcher or orchestrator.
"""

import os
import sys
import time
import signal
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# ─── Load .env if present ──────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = Path(os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
))
SCRIPTS_DIR = Path(__file__).parent
CHECK_INTERVAL = 60  # seconds

# Processes to monitor: name -> command
# Customize this based on which watchers you've configured
MONITORED_PROCESSES = {
    "filesystem_watcher": f"python {SCRIPTS_DIR / 'filesystem_watcher.py'}",
    "orchestrator": f"python {SCRIPTS_DIR / 'orchestrator.py'}",
    # Uncomment when configured:
    # "gmail_watcher": f"python {SCRIPTS_DIR / 'gmail_watcher.py'}",
}

# ─── Logging ───────────────────────────────────────────────────────────────────

log_dir = VAULT_PATH / "Logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | WATCHDOG | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_dir / "watchdog.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("Watchdog")

# ─── Process Management ────────────────────────────────────────────────────────

# Active process handles: name -> subprocess.Popen
_processes: dict[str, subprocess.Popen] = {}


def is_running(proc: subprocess.Popen) -> bool:
    """Check if a subprocess is still alive."""
    return proc is not None and proc.poll() is None


def start_process(name: str, cmd: str) -> subprocess.Popen:
    """Start a process and return its handle."""
    logger.info(f"▶️  Starting {name}...")
    log_file = log_dir / f"{name}_stdout.log"

    with open(log_file, "a", encoding="utf-8") as f:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=str(SCRIPTS_DIR),
        )

    logger.info(f"   PID: {proc.pid}")
    _write_pid_file(name, proc.pid)
    return proc


def stop_process(name: str, proc: subprocess.Popen):
    """Gracefully stop a process."""
    if proc and is_running(proc):
        logger.info(f"⏹️  Stopping {name} (PID: {proc.pid})...")
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
        _remove_pid_file(name)


def _write_pid_file(name: str, pid: int):
    pid_file = VAULT_PATH / "Logs" / f"{name}.pid"
    pid_file.write_text(str(pid), encoding="utf-8")


def _remove_pid_file(name: str):
    pid_file = VAULT_PATH / "Logs" / f"{name}.pid"
    if pid_file.exists():
        pid_file.unlink()


def notify_human(message: str):
    """
    Write a notification file to /Needs_Action/ for the human to see.
    Claude will also pick this up and surface it in the Dashboard.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    notify_path = VAULT_PATH / "Needs_Action" / f"WATCHDOG_ALERT_{timestamp}.md"
    notify_path.write_text(
        f"""---
type: system_alert
source: watchdog
priority: high
created: {datetime.now().isoformat()}
---

## ⚠️ Watchdog Alert

{message}

**Action required**: Review the system health in Dashboard.md.
Check the logs in /Logs/ for details.
""",
        encoding="utf-8",
    )
    logger.warning(f"Human notification created: {notify_path.name}")


# ─── Main Loop ────────────────────────────────────────────────────────────────

def main():
    logger.info("🐕 Watchdog starting...")
    logger.info(f"   Monitoring {len(MONITORED_PROCESSES)} process(es)")
    logger.info(f"   Check interval: {CHECK_INTERVAL}s")
    logger.info(f"   Vault: {VAULT_PATH}")

    # Start all processes initially
    for name, cmd in MONITORED_PROCESSES.items():
        _processes[name] = start_process(name, cmd)

    time.sleep(5)  # Give them a moment to start

    # Handle shutdown
    running = [True]

    def handle_signal(sig, frame):
        logger.info("Watchdog shutting down...")
        running[0] = False
        for name, proc in _processes.items():
            stop_process(name, proc)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    restart_counts: dict[str, int] = {name: 0 for name in MONITORED_PROCESSES}

    while running[0]:
        for name, cmd in MONITORED_PROCESSES.items():
            proc = _processes.get(name)

            if not is_running(proc):
                exit_code = proc.returncode if proc else None
                restart_counts[name] += 1

                logger.warning(
                    f"🔴 {name} is not running "
                    f"(exit code: {exit_code}, restart #{restart_counts[name]})"
                )

                # Alert human if this keeps crashing
                if restart_counts[name] % 5 == 1:
                    notify_human(
                        f"**{name}** has crashed {restart_counts[name]} time(s). "
                        f"Last exit code: {exit_code}. "
                        f"Check /Logs/{name}_stdout.log for details."
                    )

                # Restart with exponential backoff for rapid crashers
                if restart_counts[name] > 3:
                    backoff = min(restart_counts[name] * 10, 300)
                    logger.info(f"   Waiting {backoff}s before restarting (rapid crash backoff)...")
                    time.sleep(backoff)

                _processes[name] = start_process(name, cmd)

            else:
                # Process is healthy
                pass

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
