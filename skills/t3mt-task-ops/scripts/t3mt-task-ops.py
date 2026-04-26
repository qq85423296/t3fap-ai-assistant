#!/usr/bin/env python3
"""Task-focused assistant helper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    mapping = {
        "templates": "task-templates",
        "tasks": "tasks",
        "task": "task",
        "create": "create-task",
        "update": "update-task",
        "run": "run-task",
        "toggle": "toggle-task",
        "delete": "delete-task",
        "execution": "execution",
        "terminate": "terminate-execution",
        "subscription": "create-subscription",
    }
    target = mapping.get(command)
    if not target:
        print("Usage: t3mt-task-ops.py <templates|tasks|task|create|update|run|toggle|delete|execution|terminate|subscription> [key=value ...]", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(
        subprocess.run(
            [sys.executable, str(CLI_PATH), target, *sys.argv[2:]],
            check=False,
        ).returncode
    )


if __name__ == "__main__":
    main()
