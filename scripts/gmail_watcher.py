"""
gmail_watcher.py — Monitors Gmail for important unread emails.

Setup:
    1. Go to https://console.cloud.google.com/
    2. Create a project → Enable Gmail API
    3. Create OAuth 2.0 credentials → Download as credentials.json
    4. Put credentials.json in the project root (NOT in the vault)
    5. Run this script once — it will open a browser to authorize
    6. After authorization, token.json is created automatically

Requirements:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

Environment variables (.env):
    VAULT_PATH=/path/to/AI_Employee_Vault
    GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
    GMAIL_TOKEN_PATH=/path/to/token.json
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
)
CREDENTIALS_PATH = os.getenv(
    "GMAIL_CREDENTIALS_PATH",
    str(Path(__file__).parent.parent / "credentials.json")
)
TOKEN_PATH = os.getenv(
    "GMAIL_TOKEN_PATH",
    str(Path(__file__).parent.parent / "token.json")
)

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Keywords that trigger HIGH priority
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "invoice", "payment", "overdue",
    "legal", "contract", "lawsuit", "emergency", "immediate"
]

# ─── Watcher Implementation ────────────────────────────────────────────────────


class GmailWatcher(BaseWatcher):
    """
    Polls Gmail for unread important emails every 2 minutes.
    Creates action files in /Needs_Action/ for Claude to process.

    NOTE: This only reads email — it never sends or modifies.
    Sending requires an approved MCP action.
    """

    def __init__(self, vault_path: str, credentials_path: str, token_path: str):
        super().__init__(vault_path, check_interval=120, watcher_name="GmailWatcher")
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self._processed_ids: set[str] = set()
        self._load_processed_ids()

    def on_startup(self):
        """Authenticate and build Gmail service on startup."""
        try:
            self.service = self._build_gmail_service()
            self.logger.info("[OK] Gmail authentication successful")
        except Exception as e:
            self.logger.error(f"Gmail authentication failed: {e}")
            raise

    def _build_gmail_service(self):
        """Authenticate with Gmail API using OAuth2."""
        # Lazy import to avoid error if not installed
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError:
            raise RuntimeError(
                "Gmail libraries not installed. Run:\n"
                "  pip install google-auth google-auth-oauthlib google-api-python-client"
            )

        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.token_path), GMAIL_SCOPES
            )

        # Refresh or re-authorize if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}\n"
                        "Download it from Google Cloud Console → APIs & Services → Credentials"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for next run
            self.token_path.write_text(creds.to_json(), encoding="utf-8")
            self.logger.info(f"Saved Gmail token to {self.token_path}")

        return build("gmail", "v1", credentials=creds)

    def _load_processed_ids(self):
        """Load previously processed message IDs."""
        processed_file = self.vault_path / "Logs" / "gmail_processed.txt"
        if processed_file.exists():
            for line in processed_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    self._processed_ids.add(line)
        self.logger.debug(f"Loaded {len(self._processed_ids)} processed Gmail message IDs")

    def _save_processed_id(self, message_id: str):
        """Persist a processed message ID."""
        processed_file = self.vault_path / "Logs" / "gmail_processed.txt"
        with open(processed_file, "a", encoding="utf-8") as f:
            f.write(message_id + "\n")
        self._processed_ids.add(message_id)

    def check_for_updates(self) -> list:
        """Fetch unread important messages not yet processed."""
        if not self.service:
            self.logger.warning("Gmail service not initialized. Skipping check.")
            return []

        results = self.service.users().messages().list(
            userId="me",
            q="is:unread (is:important OR label:inbox)",
            maxResults=20
        ).execute()

        messages = results.get("messages", [])
        new_messages = [m for m in messages if m["id"] not in self._processed_ids]

        if new_messages:
            self.logger.info(f"Found {len(new_messages)} new unread message(s)")

        return new_messages

    def create_action_file(self, message: dict) -> Path:
        """Create a Needs_Action .md file for each new email."""
        msg_id = message["id"]

        # Fetch full message
        full_msg = self.service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        # Extract headers
        headers = {}
        for h in full_msg.get("payload", {}).get("headers", []):
            headers[h["name"]] = h["value"]

        sender = headers.get("From", "Unknown Sender")
        subject = headers.get("Subject", "No Subject")
        date = headers.get("Date", datetime.now().isoformat())
        snippet = full_msg.get("snippet", "")

        # Determine priority
        text_lower = (subject + " " + snippet).lower()
        priority = "high" if any(kw in text_lower for kw in HIGH_PRIORITY_KEYWORDS) else "medium"

        # Clean up filename
        safe_subject = "".join(c if c.isalnum() or c in "_ -" else "_" for c in subject[:40])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.needs_action / filename

        content = f"""---
type: email
source: gmail
message_id: {msg_id}
from: {sender}
subject: {subject}
received: {date}
processed_at: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

## Email Received

**From**: {sender}
**Subject**: {subject}
**Received**: {date}
**Priority**: {'🔴 HIGH' if priority == 'high' else '🟡 MEDIUM'}

## Snippet

> {snippet}

## Claude Instructions

1. Determine if this requires action or is informational
2. Check Company_Handbook.md — is this sender in Known Contacts?
3. If action required: create a plan or draft a reply
4. If reply is needed: create an approval file in /Pending_Approval/
5. Mark as done and move to /Done/ when complete

## Suggested Actions

- [ ] Read full email (use Gmail MCP if available)
- [ ] Categorize: Client / Vendor / Admin / Spam
- [ ] Draft reply if needed
- [ ] Create approval request if sending reply
- [ ] Archive / Move to Done
"""

        filepath.write_text(content, encoding="utf-8")
        self._save_processed_id(msg_id)

        return filepath


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gmail Watcher for AI Employee")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for testing)")
    args = parser.parse_args()

    print("[GMAIL WATCHER] Starting...")
    print(f"   Vault: {VAULT_PATH}")
    print(f"   Credentials: {CREDENTIALS_PATH}")
    if args.once:
        print(f"   Mode: ONCE (testing)")
    else:
        print(f"   Polling every 2 minutes for unread important emails")
        print(f"   Press Ctrl+C to stop.")
    print()

    watcher = GmailWatcher(
        vault_path=VAULT_PATH,
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH,
    )

    if args.once:
        # Run once for testing
        print("[TEST] Running Gmail check once...")
        watcher.on_startup()
        items = watcher.check_for_updates()
        if items:
            print(f"[TEST] Found {len(items)} new emails")
            for item in items:
                try:
                    path = watcher.create_action_file(item)
                    print(f"[TEST] Created: {path.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to create action file: {e}")
        else:
            print("[TEST] No new emails found")
        print("[TEST] Gmail check complete")
    else:
        # Run continuously (production)
        try:
            watcher.run()
        except KeyboardInterrupt:
            print("\n[STOP] Gmail Watcher stopped.")
