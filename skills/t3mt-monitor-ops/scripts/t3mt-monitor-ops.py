#!/usr/bin/env python3
"""Monitor-focused assistant helper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    mapping = {
        "dashboard": "monitor",
        "overview": "monitor-overview",
        "schedules": "monitor-schedules",
        "executions": "monitor-executions",
        "plugin-health": "monitor-plugin-health",
        "system-realtime": "monitor-system-realtime",
    }
    target = mapping.get(command)
    if not target:
        print("Usage: t3mt-monitor-ops.py <dashboard|overview|schedules|executions|plugin-health|system-realtime> [key=value ...]", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(
        subprocess.run([sys.executable, str(CLI_PATH), target, *sys.argv[2:]], check=False).returncode
    )


if __name__ == "__main__":
    main()
