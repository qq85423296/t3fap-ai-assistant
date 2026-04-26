#!/usr/bin/env python3
"""Recovery helper for T3MT/T3FAP automation failures."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_pairs(items: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            fail(f"Error: expected key=value, got '{item}'")
        key, _, value = item.partition("=")
        data[key] = value
    return data


def run_cli(*args: str) -> object:
    completed = subprocess.run(
        [sys.executable, str(CLI_PATH), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr or completed.stdout)
        raise SystemExit(completed.returncode)
    raw = completed.stdout.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def as_items(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        raw = payload.get("items", payload.get("data", payload.get("rows", [])))
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
    return []


def normalize_status(value: object) -> str:
    return str(value or "").strip().lower()


def is_plugin_unhealthy(item: dict[str, Any]) -> bool:
    enabled = item.get("enabled")
    status = normalize_status(item.get("status") or item.get("health_status") or item.get("state"))
    healthy = item.get("healthy")
    if enabled is False:
        return True
    if healthy is False:
        return True
    return status in {"error", "failed", "unhealthy", "disabled", "offline", "degraded"}


def summarize_plugin_issue(item: dict[str, Any]) -> dict[str, Any]:
    plugin_id = str(item.get("plugin_id") or item.get("id") or "").strip()
    return {
        "kind": "plugin",
        "priority": "high",
        "plugin_id": plugin_id,
        "reason": item.get("message") or item.get("error") or item.get("last_error") or "plugin health is not good",
        "suggested_commands": [
            f"python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py inspect plugin_id={plugin_id}",
            f"python scripts/t3mt-remediation-ops.py plugin-recover plugin_id={plugin_id}",
        ],
    }


def is_failed_execution(item: dict[str, Any]) -> bool:
    status = normalize_status(item.get("status") or item.get("result") or item.get("state"))
    if status in {"failed", "error", "timeout", "cancelled"}:
        return True
    return bool(item.get("success") is False)


def summarize_execution_issue(item: dict[str, Any]) -> dict[str, Any]:
    execution_id = str(item.get("execution_id") or item.get("id") or "").strip()
    task_id = str(item.get("task_id") or item.get("task_definition_id") or "").strip()
    plugin_id = str(item.get("plugin_id") or "").strip()
    suggested = [f"python scripts/t3mt-remediation-ops.py execution-recover execution_id={execution_id} auto_run=true"]
    if task_id:
        suggested.append(f"python ../t3mt-task-ops/scripts/t3mt-task-ops.py inspect task_id={task_id}")
    if plugin_id:
        suggested.append(f"python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py inspect plugin_id={plugin_id}")
    return {
        "kind": "execution",
        "priority": "medium",
        "execution_id": execution_id,
        "task_id": task_id,
        "plugin_id": plugin_id,
        "reason": item.get("error_message") or item.get("message") or item.get("last_error") or "task execution failed",
        "suggested_commands": suggested,
    }


def build_analysis(limit: int = 20) -> dict[str, Any]:
    plugin_health = run_cli("monitor-plugin-health")
    executions = run_cli("monitor-executions", f"limit={limit}", "status=failed")

    plugin_items = as_items(plugin_health)
    execution_items = as_items(executions)

    issues: list[dict[str, Any]] = []
    issues.extend(summarize_plugin_issue(item) for item in plugin_items if is_plugin_unhealthy(item))
    issues.extend(summarize_execution_issue(item) for item in execution_items if is_failed_execution(item))

    return {
        "summary": {
            "plugin_health_items": len(plugin_items),
            "failed_execution_items": len(execution_items),
            "recovery_candidates": len(issues),
        },
        "issues": issues,
    }


def plugin_recover(plugin_id: str) -> dict[str, Any]:
    before = run_cli("plugin", f"plugin_id={plugin_id}")
    run_cli("enable-plugin", f"plugin_id={plugin_id}")
    after = run_cli("plugin", f"plugin_id={plugin_id}")
    health = run_cli("plugin-health", f"plugin_id={plugin_id}")
    return {
        "plugin_id": plugin_id,
        "before": before,
        "after": after,
        "health": health,
    }


def task_recover(task_id: str, auto_run: bool) -> dict[str, Any]:
    before = run_cli("task", f"task_id={task_id}")
    run_cli("toggle-task", f"task_id={task_id}", "enabled=true")
    run_result: object = {"skipped": True}
    if auto_run:
        run_result = run_cli("run-task", f"task_id={task_id}", "wait_for_completion=false")
    after = run_cli("task", f"task_id={task_id}")
    return {
        "task_id": task_id,
        "before": before,
        "after": after,
        "run_result": run_result,
    }


def execution_recover(execution_id: str, auto_run: bool) -> dict[str, Any]:
    execution = run_cli("execution", f"execution_id={execution_id}")
    if not isinstance(execution, dict):
        fail("Error: unexpected execution payload.")
    task_id = str(execution.get("task_id") or execution.get("task_definition_id") or "").strip()
    plugin_id = str(execution.get("plugin_id") or "").strip()
    result: dict[str, Any] = {
        "execution": execution,
        "task_recovery": None,
        "plugin_recovery": None,
    }
    if plugin_id:
        result["plugin_recovery"] = plugin_recover(plugin_id)
    if task_id:
        result["task_recovery"] = task_recover(task_id, auto_run=auto_run)
    return result


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: t3mt-remediation-ops.py <analyze|plugin-recover|task-recover|execution-recover> [key=value ...]")

    command = sys.argv[1]
    args = parse_pairs(sys.argv[2:])

    if command == "analyze":
        limit = int(str(args.get("limit") or "20").strip())
        print(json.dumps(build_analysis(limit=limit), ensure_ascii=False, indent=2))
        return

    if command == "plugin-recover":
        plugin_id = str(args.get("plugin_id") or "").strip()
        if not plugin_id:
            fail("Error: plugin_id is required.")
        print(json.dumps(plugin_recover(plugin_id), ensure_ascii=False, indent=2))
        return

    if command == "task-recover":
        task_id = str(args.get("task_id") or "").strip()
        if not task_id:
            fail("Error: task_id is required.")
        auto_run = str(args.get("auto_run") or "true").strip().lower() in {"1", "true", "yes", "on"}
        print(json.dumps(task_recover(task_id, auto_run=auto_run), ensure_ascii=False, indent=2))
        return

    if command == "execution-recover":
        execution_id = str(args.get("execution_id") or "").strip()
        if not execution_id:
            fail("Error: execution_id is required.")
        auto_run = str(args.get("auto_run") or "true").strip().lower() in {"1", "true", "yes", "on"}
        print(json.dumps(execution_recover(execution_id, auto_run=auto_run), ensure_ascii=False, indent=2))
        return

    fail(f"Error: unsupported command '{command}'.")


if __name__ == "__main__":
    main()
