#!/usr/bin/env python3
"""
scripts/update_memory.py

Automated updater and context provider for MEMORY.md in StockFlow.
Can be used via CLI or imported into tests, git hooks, or agent workflows.
"""

from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
from typing import Optional


DEFAULT_MEMORY_FILE = Path(__file__).resolve().parent.parent / "MEMORY.md"


class MemoryManager:
    """Manages reading, updating, and formatting MEMORY.md."""

    def __init__(self, file_path: Path | str = DEFAULT_MEMORY_FILE):
        self.file_path = Path(file_path).resolve()
        if not self.file_path.exists():
            raise FileNotFoundError(f"Memory file not found at: {self.file_path}")
        self.content = self.file_path.read_text(encoding="utf-8")

    def reload(self) -> None:
        """Reload memory file from disk."""
        self.content = self.file_path.read_text(encoding="utf-8")

    def save(self) -> None:
        """Persist current state back to disk."""
        self.file_path.write_text(self.content, encoding="utf-8")

    def get_prompt_context(self) -> str:
        """Returns the full memory formatted as a system prompt block."""
        return f"""=== STOCKFLOW PROJECT MEMORY ===\n{self.content.strip()}\n================================"""

    def _replace_field(self, field_label: str, new_value: str) -> bool:
        """Replaces a bullet line of format '- **field_label**: <value>'."""
        pattern = rf"(- \*\*{re.escape(field_label)}\*\*: ).*"
        if re.search(pattern, self.content):
            self.content = re.sub(pattern, rf"\g<1>{new_value}", self.content)
            return True
        return False

    def update_phase(self, phase_name: str) -> None:
        """Update Active Phase."""
        self._replace_field("Active Phase", phase_name)

    def update_current_task(self, task_name: str) -> None:
        """Update Current Task."""
        self._replace_field("Current Task", task_name)

    def update_completed_task(self, task_name: str) -> None:
        """Update Last Completed Task with timestamp."""
        timestamp = datetime.now().strftime("%d %b %Y, %H:%M")
        self._replace_field("Last Completed Task", f"{task_name} (on {timestamp})")

    def update_test_status(self, status: str) -> None:
        """Update Last Test Status."""
        self._replace_field("Last Test Status", status)

    def sync_from_git(self) -> Optional[str]:
        """Inspects latest git commit and logs it under completed tasks."""
        try:
            repo_dir = self.file_path.parent
            res = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%h - %s"],
                cwd=repo_dir,
                capture_output=True,
                text=True,
                check=True
            )
            commit_info = res.stdout.strip()
            if commit_info:
                self.update_completed_task(f"Git {commit_info}")
                return commit_info
        except Exception:
            return None
        return None

    def get_status_summary(self) -> dict[str, str]:
        """Extracts key values from Section 4."""
        summary = {}
        for key in ["Active Phase", "Current Task", "Last Completed Task", "Last Test Status"]:
            match = re.search(rf"- \*\*{re.escape(key)}\*\*: (.*)", self.content)
            summary[key] = match.group(1).strip() if match else "Not found"
        return summary


def main():
    parser = argparse.ArgumentParser(
        description="Inspect or update the StockFlow MEMORY.md file."
    )
    parser.add_argument(
        "--file",
        "-f",
        default=str(DEFAULT_MEMORY_FILE),
        help="Path to MEMORY.md (defaults to project root MEMORY.md)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Display the current project state from MEMORY.md",
    )
    parser.add_argument(
        "--dump-prompt",
        action="store_true",
        help="Dump formatted memory block suitable for injecting into an AI agent prompt",
    )
    parser.add_argument(
        "--phase",
        type=str,
        help="Update the active phase (e.g. 'Phase 1: Data Structures')",
    )
    parser.add_argument(
        "--task",
        "--next",
        dest="task",
        type=str,
        help="Update the current in-progress / next task (e.g. 'Task 1.1 Linked List')",
    )
    parser.add_argument(
        "--complete",
        "--finish",
        dest="complete",
        type=str,
        help="Record a completed task (e.g. 'Task 0.1 Layout complete')",
    )
    parser.add_argument(
        "--tests",
        type=str,
        help="Record latest test status (e.g. 'All 14 tests passing')",
    )
    parser.add_argument(
        "--git-sync",
        action="store_true",
        help="Automatically sync last completed task from the latest Git commit",
    )

    args = parser.parse_args()

    try:
        mgr = MemoryManager(args.file)
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    changed = False

    if args.phase:
        mgr.update_phase(args.phase)
        changed = True
        print(f"[Memory Updated] Active Phase -> {args.phase}")

    if args.task:
        mgr.update_current_task(args.task)
        changed = True
        print(f"[Memory Updated] Current Task -> {args.task}")

    if args.complete:
        mgr.update_completed_task(args.complete)
        changed = True
        print(f"[Memory Updated] Last Completed Task -> {args.complete}")

    if args.tests:
        mgr.update_test_status(args.tests)
        changed = True
        print(f"[Memory Updated] Test Status -> {args.tests}")

    if args.git_sync:
        commit = mgr.sync_from_git()
        if commit:
            changed = True
            print(f"[Memory Synced with Git] -> {commit}")
        else:
            print("[Warning] Git repository not found or no commits yet.")

    if changed:
        mgr.save()

    if args.dump_prompt:
        print(mgr.get_prompt_context())
    elif args.status or not changed:
        summary = mgr.get_status_summary()
        print("\n--- STOCKFLOW CURRENT MEMORY STATUS ---")
        for k, v in summary.items():
            print(f"{k:20}: {v}")
        print("---------------------------------------\n")


if __name__ == "__main__":
    main()

