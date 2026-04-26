#!/usr/bin/env python3
"""Settings-focused assistant helper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    mapping = {
        "task-template-settings": "task-template-settings",
        "update-task-template-settings": "update-task-template-settings",
    }
    target = mapping.get(command)
    if not target:
        print("Usage: t3mt-settings-ops.py <task-template-settings|update-task-template-settings> [key=value ...]", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(
        subprocess.run([sys.executable, str(CLI_PATH), target, *sys.argv[2:]], check=False).returncode
    )


if __name__ == "__main__":
    main()
