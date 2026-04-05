"""
AURA Module: Smart To-Do List
Add, show, complete, and delete tasks. Tasks are saved to a JSON file.
"""

import json
import os
import datetime
from pathlib import Path


TASKS_FILE = Path(__file__).parent.parent / "data" / "tasks.json"


class TodoManager:
    def __init__(self):
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: list[dict] = []
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self):
        if TASKS_FILE.exists():
            try:
                with open(TASKS_FILE, "r") as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tasks = []
        else:
            self.tasks = []

    def _save(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=2)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------
    def add_task(self, task_text: str) -> str:
        if not task_text.strip():
            return "Please provide a task description."
        task = {
            "id": len(self.tasks) + 1,
            "text": task_text.strip().capitalize(),
            "done": False,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "completed_at": None,
        }
        self.tasks.append(task)
        self._save()
        return f"Task added: '{task['text']}'"

    def show_tasks(self) -> str:
        if not self.tasks:
            return "Your task list is empty. Say 'add task' to get started."
        pending = [t for t in self.tasks if not t["done"]]
        done    = [t for t in self.tasks if t["done"]]
        lines = []
        if pending:
            lines.append(f"Pending ({len(pending)}):")
            for t in pending:
                lines.append(f"  [{t['id']}] {t['text']}")
        if done:
            lines.append(f"Completed ({len(done)}):")
            for t in done:
                lines.append(f"  [✓] {t['text']}")
        return "\n".join(lines)

    def complete_task(self, identifier) -> str:
        """Mark a task done by ID number or partial text match."""
        target = None
        # Try numeric ID first
        try:
            task_id = int(str(identifier))
            for t in self.tasks:
                if t["id"] == task_id:
                    target = t
                    break
        except (ValueError, TypeError):
            pass
        # Fallback: text match
        if target is None:
            query = str(identifier).lower()
            for t in self.tasks:
                if query in t["text"].lower():
                    target = t
                    break
        if target is None:
            return f"No task found matching '{identifier}'."
        if target["done"]:
            return f"Task '{target['text']}' is already completed."
        target["done"] = True
        target["completed_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self._save()
        return f"Great job! Task completed: '{target['text']}'"

    def delete_task(self, identifier) -> str:
        try:
            task_id = int(str(identifier))
            before = len(self.tasks)
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            if len(self.tasks) < before:
                self._save()
                return f"Task {task_id} deleted."
        except (ValueError, TypeError):
            pass
        return f"Task '{identifier}' not found."

    def productivity_report(self) -> str:
        total  = len(self.tasks)
        done   = sum(1 for t in self.tasks if t["done"])
        pending = total - done
        pct = int((done / total * 100)) if total else 0
        today = datetime.date.today().strftime("%Y-%m-%d")
        today_done = sum(
            1 for t in self.tasks
            if t["done"] and t.get("completed_at", "").startswith(today)
        )
        report = (
            f"Productivity Report:\n"
            f"  Total tasks   : {total}\n"
            f"  Completed     : {done} ({pct}%)\n"
            f"  Pending       : {pending}\n"
            f"  Done today    : {today_done}"
        )
        spoken = (
            f"You have {total} tasks in total. "
            f"{done} are completed and {pending} are still pending. "
            f"Today you completed {today_done} tasks. Keep it up!"
        )
        return report, spoken

    # ------------------------------------------------------------------
    # Raw access for GUI
    # ------------------------------------------------------------------
    def get_all(self) -> list[dict]:
        return self.tasks
