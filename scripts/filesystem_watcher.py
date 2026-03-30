"""
filesystem_watcher.py — Watches a drop folder for new files.

Usage:
    python filesystem_watcher.py

Drop any file into the /Inbox/ folder inside your vault.
The watcher will detect it and create a .md action file in /Needs_Action/.
Claude will then pick it up and process it.

Bronze Tier: This is the primary watcher for the foundation setup.
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# ─── Configuration ─────────────────────────────────────────────────────────────

VAULT_PATH = os.getenv(
    "VAULT_PATH",
    str(Path(__file__).parent.parent / "AI_Employee_Vault")
)

# ─── Watcher Implementation ────────────────────────────────────────────────────


class FileSystemWatcher(BaseWatcher):
    """
    Monitors the /Inbox/ folder for newly dropped files.

    When a file appears:
    1. Copies it to /Needs_Action/ with a FILE_ prefix
    2. Creates a companion .md metadata file for Claude
    3. Signals the orchestrator

    Supported: Any file type. Claude will inspect and categorize.
    """

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=10, watcher_name="FileSystemWatcher")

        self.inbox = self.vault_path / "Inbox"
        self.inbox.mkdir(parents=True, exist_ok=True)

        # Track already-processed files by their hash to avoid duplicates
        self._processed_hashes: set[str] = set()
        self._load_processed_hashes()

    def _load_processed_hashes(self):
        """Load previously processed file hashes from the log."""
        hash_log = self.vault_path / "Logs" / "processed_files.txt"
        if hash_log.exists():
            for line in hash_log.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    self._processed_hashes.add(line)
        self.logger.debug(f"Loaded {len(self._processed_hashes)} processed file hashes")

    def _save_hash(self, file_hash: str):
        """Persist a processed file hash."""
        hash_log = self.vault_path / "Logs" / "processed_files.txt"
        with open(hash_log, "a", encoding="utf-8") as f:
            f.write(file_hash + "\n")
        self._processed_hashes.add(file_hash)

    def _file_hash(self, path: Path) -> str:
        """Compute MD5 hash of a file for deduplication."""
        md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def check_for_updates(self) -> list:
        """Scan /Inbox/ for new files not yet processed."""
        new_files = []

        for item in self.inbox.iterdir():
            # Skip hidden files, directories, and .md files (metadata)
            if item.is_dir() or item.name.startswith(".") or item.suffix == ".md":
                continue

            # Skip if we've already processed this exact file content
            try:
                file_hash = self._file_hash(item)
                if file_hash not in self._processed_hashes:
                    new_files.append({"path": item, "hash": file_hash})
            except PermissionError:
                # File may still be being written — skip this cycle
                self.logger.debug(f"Skipping {item.name} (permission error — file may still be writing)")

        return new_files

    def create_action_file(self, item: dict) -> Path:
        """
        For each new file:
        1. Copy to /Needs_Action/ with FILE_ prefix
        2. Create .md metadata file for Claude
        3. Mark as processed
        """
        source: Path = item["path"]
        file_hash: str = item["hash"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = source.name.replace(" ", "_")
        dest_filename = f"FILE_{timestamp}_{safe_name}"
        dest = self.needs_action / dest_filename

        # Copy the actual file
        shutil.copy2(source, dest)

        # Determine file type category
        category = self._categorize_file(source)

        # Create companion .md for Claude
        md_path = self.needs_action / f"FILE_{timestamp}_{source.stem}.md"
        md_content = f"""---
type: file_drop
category: {category}
original_name: {source.name}
original_path: {source}
stored_as: {dest_filename}
size_bytes: {source.stat().st_size}
size_human: {self._human_size(source.stat().st_size)}
dropped_at: {datetime.now().isoformat()}
hash_md5: {file_hash}
priority: medium
status: pending
---

## File Drop Detected

A new file has been dropped into the Inbox and is ready for processing.

**File**: `{source.name}`
**Type**: {category}
**Size**: {self._human_size(source.stat().st_size)}
**Stored at**: `/Needs_Action/{dest_filename}`

## Suggested Actions

- [ ] Inspect file content and determine purpose
- [ ] Categorize and file appropriately
- [ ] Extract any action items
- [ ] Archive original to appropriate vault folder
- [ ] Update Dashboard.md with summary

## Claude Instructions

1. Read or inspect the file at `/Needs_Action/{dest_filename}`
2. Determine what action is required
3. Create a Plan.md if the task has multiple steps
4. Move this .md file and the data file to `/Done/` when complete
"""
        md_path.write_text(md_content, encoding="utf-8")

        # Mark as processed
        self._save_hash(file_hash)

        # Optionally move original from Inbox to Done (keep Inbox clean)
        done_original = self.vault_path / "Done" / f"INBOX_ORIGINAL_{timestamp}_{safe_name}"
        try:
            shutil.move(str(source), str(done_original))
            self.logger.debug(f"Moved original from Inbox to Done: {done_original.name}")
        except Exception as e:
            self.logger.warning(f"Could not move original file: {e}")

        return md_path

    def _categorize_file(self, path: Path) -> str:
        """Guess a category based on file extension."""
        ext = path.suffix.lower()
        categories = {
            ".pdf": "Document/PDF",
            ".docx": "Document/Word",
            ".xlsx": "Spreadsheet/Excel",
            ".csv": "Spreadsheet/CSV",
            ".txt": "Text/Plain",
            ".md": "Text/Markdown",
            ".jpg": "Image/JPEG",
            ".jpeg": "Image/JPEG",
            ".png": "Image/PNG",
            ".mp3": "Audio/MP3",
            ".mp4": "Video/MP4",
            ".zip": "Archive/ZIP",
            ".json": "Data/JSON",
            ".xml": "Data/XML",
        }
        return categories.get(ext, f"Unknown/{ext or 'no-extension'}")

    def _human_size(self, size_bytes: int) -> str:
        """Convert bytes to human-readable size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"[FILE WATCHER] Starting...")
    print(f"   Vault: {VAULT_PATH}")
    print(f"   Drop files into: {VAULT_PATH}/Inbox/")
    print(f"   Action files go to: {VAULT_PATH}/Needs_Action/")
    print(f"   Press Ctrl+C to stop.")
    print()

    watcher = FileSystemWatcher(vault_path=VAULT_PATH)
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\n⛔ File System Watcher stopped.")
