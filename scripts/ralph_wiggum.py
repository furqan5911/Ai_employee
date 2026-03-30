"""
ralph_wiggum.py — The "Ralph Wiggum" Stop Hook for persistent task completion.

This script is called by Claude Code's Stop hook every time Claude tries to exit.
It implements the Ralph Wiggum loop pattern from the hackathon docs:

  1. Orchestrator writes a state file: /Vault/.ralph_state.json
  2. Claude works on the task
  3. Claude tries to exit → this Stop hook fires
  4. Hook checks: was TASK_COMPLETE promised? Is state file in /Done?
  5. YES → allow exit (return exit code 0)
  6. NO → block exit (return exit code 2 = rewake), re-inject the prompt

Exit codes:
  0  = allow Claude to exit normally
  2  = block exit and re-inject prompt (Claude Code rewake behavior)

State file format (/Vault/.ralph_state.json):
{
  "prompt": "The original task prompt",
  "max_iterations": 10,
  "current_iteration": 1,
  "task_id": "unique_task_identifier",
  "completion_promise": "TASK_COMPLETE",
  "created_at": "2026-03-21T10:00:00Z"
}

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = Path(os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
))
STATE_FILE = VAULT_PATH / ".ralph_state.json"
DONE_DIR = VAULT_PATH / "Done"

# ─── Read hook input from stdin ────────────────────────────────────────────────

def read_hook_input() -> dict:
    """Read the JSON payload Claude Code sends to the Stop hook via stdin."""
    try:
        raw = sys.stdin.read()
        if raw.strip():
            return json.loads(raw)
    except (json.JSONDecodeError, Exception):
        pass
    return {}


def check_task_complete_in_output(hook_input: dict) -> bool:
    """
    Check if Claude output the completion promise <promise>TASK_COMPLETE</promise>.
    Claude Code passes transcript/output info in the hook input.
    """
    # Check the stop_reason or any output fields
    output = str(hook_input)
    return "TASK_COMPLETE" in output


def load_state() -> dict | None:
    """Load the Ralph state file if it exists."""
    if not STATE_FILE.exists():
        return None
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, Exception):
        return None


def save_state(state: dict):
    """Save the updated Ralph state file."""
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def clear_state():
    """Remove the state file — task is complete."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def check_task_in_done(task_id: str) -> bool:
    """
    Check if the task has been moved to /Done/ (file-movement completion strategy).
    Looks for any file in /Done/ containing the task_id.
    """
    if not DONE_DIR.exists():
        return False
    for f in DONE_DIR.iterdir():
        if task_id in f.name:
            return True
    return False


def log_ralph_event(event: str, state: dict):
    """Log Ralph Wiggum events to the vault logs."""
    log_dir = VAULT_PATH / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{today}.jsonl"

    entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "ralph_wiggum",
        "actor": "stop_hook",
        "event": event,
        "task_id": state.get("task_id", "unknown"),
        "iteration": state.get("current_iteration", 0),
        "max_iterations": state.get("max_iterations", 10),
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


# ─── Main Logic ────────────────────────────────────────────────────────────────

def main():
    # Read what Claude Code sent us
    hook_input = read_hook_input()

    # Load Ralph state — if no state file, nothing to do, exit normally
    state = load_state()
    if state is None:
        # No active Ralph loop — allow exit
        sys.exit(0)

    task_id = state.get("task_id", "unknown")
    prompt = state.get("prompt", "")
    max_iterations = state.get("max_iterations", 10)
    current_iteration = state.get("current_iteration", 0)
    completion_promise = state.get("completion_promise", "TASK_COMPLETE")

    # ── Completion check 1: Promise-based ─────────────────────────────────────
    if check_task_complete_in_output(hook_input):
        log_ralph_event("task_complete_via_promise", state)
        clear_state()
        # Output a friendly message to the user
        result = {"systemMessage": f"✅ Ralph Wiggum: Task '{task_id}' complete after {current_iteration} iteration(s)!"}
        print(json.dumps(result))
        sys.exit(0)

    # ── Completion check 2: File-movement based ────────────────────────────────
    if check_task_in_done(task_id):
        log_ralph_event("task_complete_via_file_move", state)
        clear_state()
        result = {"systemMessage": f"✅ Ralph Wiggum: Task '{task_id}' found in /Done/ — complete!"}
        print(json.dumps(result))
        sys.exit(0)

    # ── Max iterations guard ───────────────────────────────────────────────────
    if current_iteration >= max_iterations:
        log_ralph_event("max_iterations_reached", state)
        clear_state()
        result = {
            "systemMessage": (
                f"⚠️ Ralph Wiggum: Task '{task_id}' reached max iterations ({max_iterations}). "
                f"Task may be incomplete. Check /Needs_Action/ and /Plans/ for status."
            )
        }
        print(json.dumps(result))
        sys.exit(0)

    # ── Task not complete — re-inject the prompt ───────────────────────────────
    current_iteration += 1
    state["current_iteration"] = current_iteration
    save_state(state)

    log_ralph_event(f"reinjecting_iteration_{current_iteration}", state)

    # Output the hookSpecificOutput to re-inject the prompt
    result = {
        "systemMessage": f"🔄 Ralph Wiggum: Iteration {current_iteration}/{max_iterations} — task not complete yet, continuing...",
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": (
                f"[Ralph Wiggum Loop — Iteration {current_iteration}/{max_iterations}]\n"
                f"Task ID: {task_id}\n"
                f"The task is NOT complete yet. The completion signal '{completion_promise}' was not detected "
                f"and no matching file was found in /Done/.\n\n"
                f"ORIGINAL TASK:\n{prompt}\n\n"
                f"Please continue working on the task. Check /Plans/ for your current plan and "
                f"resume from the first unchecked step. When fully done, output: "
                f"<promise>{completion_promise}</promise>"
            )
        }
    }
    print(json.dumps(result))

    # Exit code 2 = rewake (re-inject and continue)
    sys.exit(2)


if __name__ == "__main__":
    main()
