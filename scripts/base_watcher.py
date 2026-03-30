"""
base_watcher.py — Abstract base class for all Watcher scripts.

All Watchers (Gmail, WhatsApp, FileSystem, Finance) inherit from this.
It handles the polling loop, logging, and error recovery automatically.
"""

import time
import logging
import logging.handlers
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


def setup_logging(name: str, log_dir: Path) -> logging.Logger:
    """Set up structured logging to both console and rotating file."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Rotating file handler (10MB, keep 7 days)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


class BaseWatcher(ABC):
    """
    Abstract base class for all Watcher scripts.

    Subclasses must implement:
        - check_for_updates() -> list
        - create_action_file(item) -> Path
    """

    def __init__(self, vault_path: str, check_interval: int = 60, watcher_name: str = None):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.check_interval = check_interval
        self.watcher_name = watcher_name or self.__class__.__name__

        # Ensure required directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        (self.vault_path / "Logs").mkdir(parents=True, exist_ok=True)

        # Set up logging
        self.logger = setup_logging(
            self.watcher_name,
            self.vault_path / "Logs"
        )

        self.logger.info(f"Initialized {self.watcher_name}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Poll the source for new items.
        Returns a list of items to process (format depends on subclass).
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md file in /Needs_Action/ for Claude to process.
        Returns the path to the created file.
        """
        pass

    def on_startup(self):
        """Optional hook called once before the main loop starts."""
        pass

    def on_error(self, error: Exception) -> bool:
        """
        Called when check_for_updates() or create_action_file() raises.
        Return True to continue, False to stop the watcher.
        Default: log the error and continue.
        """
        self.logger.error(f"Error in {self.watcher_name}: {error}", exc_info=True)
        return True  # continue running

    def write_update_signal(self, message: str):
        """Write a signal file to /Updates/ so the orchestrator knows we found something."""
        updates_dir = self.vault_path / "Updates"
        updates_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        signal_file = updates_dir / f"SIGNAL_{self.watcher_name}_{timestamp}.md"
        signal_file.write_text(
            f"---\nwatcher: {self.watcher_name}\ntimestamp: {datetime.now().isoformat()}\n---\n\n{message}\n",
            encoding="utf-8",
        )

    def run(self):
        """
        Main polling loop. Runs indefinitely.
        Use PM2 or supervisord to manage this process in production.
        """
        self.logger.info(f"[START] Starting {self.watcher_name}...")
        self.on_startup()

        consecutive_errors = 0
        max_consecutive_errors = 5

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    self.logger.info(f"Found {len(items)} new item(s) to process")
                    for item in items:
                        try:
                            path = self.create_action_file(item)
                            self.logger.info(f"Created action file: {path.name}")
                        except Exception as e:
                            self.logger.error(f"Failed to create action file: {e}", exc_info=True)

                    # Signal orchestrator
                    self.write_update_signal(f"Found {len(items)} new item(s)")

                consecutive_errors = 0  # Reset on success

            except Exception as e:
                consecutive_errors += 1
                should_continue = self.on_error(e)

                if not should_continue:
                    self.logger.critical("Watcher stopping due to unrecoverable error.")
                    break

                if consecutive_errors >= max_consecutive_errors:
                    self.logger.critical(
                        f"Too many consecutive errors ({consecutive_errors}). "
                        f"Sleeping for 5 minutes before retrying."
                    )
                    time.sleep(300)
                    consecutive_errors = 0

            time.sleep(self.check_interval)
