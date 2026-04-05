"""
AURA Module: History Manager
Stores every command AURA hears, with timestamp, and lets user review it.
"""

import json
import datetime
from pathlib import Path


HISTORY_FILE = Path(__file__).parent.parent / "data" / "history.json"
MAX_HISTORY = 500          # keep last 500 entries


class HistoryManager:
    def __init__(self):
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.entries: list[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self):
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r") as f:
                    self.entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.entries = []

    def _save(self):
        # Trim to MAX_HISTORY
        self.entries = self.entries[-MAX_HISTORY:]
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.entries, f, indent=2)

    # ------------------------------------------------------------------
    # Log a command
    # ------------------------------------------------------------------
    def log(self, command: str, response: str = ""):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command.strip(),
            "response": response.strip(),
        }
        self.entries.append(entry)
        self._save()

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------
    def get_recent(self, count: int = 10) -> list[dict]:
        return self.entries[-count:][::-1]   # newest first

    def show_history(self, count: int = 10) -> tuple[str, str]:
        recent = self.get_recent(count)
        if not recent:
            display = "No history yet. Start talking to AURA!"
            spoken  = "You have no command history yet."
            return display, spoken

        lines = [f"Last {len(recent)} commands:"]
        for e in recent:
            lines.append(f"  [{e['timestamp']}]  You: {e['command']}")
        display = "\n".join(lines)
        spoken  = f"Here are your last {len(recent)} commands."
        return display, spoken

    def search_history(self, keyword: str) -> str:
        keyword = keyword.lower()
        matches = [
            e for e in self.entries
            if keyword in e["command"].lower()
        ]
        if not matches:
            return f"No history found matching '{keyword}'."
        lines = [f"History matching '{keyword}':"]
        for e in matches[-5:]:
            lines.append(f"  [{e['timestamp']}]  You: {e['command']}")
        return "\n".join(lines)

    def clear_history(self) -> str:
        self.entries = []
        self._save()
        return "Command history cleared."

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def stats(self) -> str:
        total = len(self.entries)
        today = datetime.date.today().strftime("%Y-%m-%d")
        today_count = sum(1 for e in self.entries if e["timestamp"].startswith(today))
        return f"Total commands: {total} | Today: {today_count}"
