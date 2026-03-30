"""
setup_gmail.py — One-time Gmail authentication helper.

Run this once to authenticate with Gmail and create token.json.
After successful authentication, you can run gmail_watcher.py normally.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the Gmail watcher
from gmail_watcher import GmailWatcher, VAULT_PATH, CREDENTIALS_PATH, TOKEN_PATH

if __name__ == "__main__":
    print("=" * 60)
    print("GMAIL AUTHENTICATION SETUP")
    print("=" * 60)
    print()
    print("This will:")
    print("  1. Open a browser window to Google sign-in")
    print("  2. Ask you to authorize AI Employee to read your Gmail")
    print("  3. Create token.json for future automatic access")
    print()
    print("CREDENTIALS:", CREDENTIALS_PATH)
    print("VAULT:", VAULT_PATH)
    print("TOKEN WILL BE SAVED TO:", TOKEN_PATH)
    print()
    print("Press Ctrl+C after you see 'Authentication successful'")
    print()
    print("=" * 60)
    print()

    input("Press Enter to open browser for authentication...")

    # Create watcher (this will trigger authentication)
    watcher = GmailWatcher(
        vault_path=VAULT_PATH,
        credentials_path=CREDENTIALS_PATH,
        token_path=TOKEN_PATH,
    )

    # Check if authentication worked
    if watcher.service:
        print()
        print("=" * 60)
        print("[SUCCESS] Gmail authentication completed!")
        print(f"[SUCCESS] Token saved to: {TOKEN_PATH}")
        print("=" * 60)
        print()
        print("You can now run: python scripts/gmail_watcher.py")
        print()
    else:
        print()
        print("[ERROR] Authentication failed. Please check the error above.")
