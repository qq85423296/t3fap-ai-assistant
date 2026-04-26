#!/usr/bin/env python3
"""Workflow helper for common T3MT/T3FAP flows."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"
CORE_PLUGIN_IDS = [
    "drive.cloud189",
    "drive.139yun",
    "drive.115",
    "drive.quark",
    "drive.quark_tv",
    "task.transfer",
    "task.drive_download",
    "task.video_download",
    "task.strm",
    "search.pansou",
]


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


def ensure_plugin(plugin_id: str) -> dict[str, object]:
    try:
        plugin = run_cli("plugin", f"plugin_id={plugin_id}")
    except SystemExit:
        plugin = None
    if not plugin:
        run_cli(
            "install-plugin",
            "source_type=bundled",
            f"source_ref={plugin_id}",
            "enable_after_install=true",
        )
    run_cli("enable-plugin", f"plugin_id={plugin_id}")
    result = run_cli("plugin", f"plugin_id={plugin_id}")
    if not isinstance(result, dict):
        fail(f"Error: unexpected plugin payload for '{plugin_id}'.")
    return result


def pick_item(items: list[dict[str, object]], index: int) -> dict[str, object]:
    if not items:
        fail("Error: no resource items were returned.")
    if index < 1 or index > len(items):
        fail(f"Error: index {index} is out of range. total={len(items)}")
    return items[index - 1]


def search_then_create_task(query_command: str, action_key: str, args: dict[str, str]) -> dict[str, object]:
    resource_plugin = str(args.get("search_plugin") or args.get("catalog_plugin") or "").strip()
    keyword = str(args.get("keyword") or "").strip()
    if not resource_plugin:
        fail("Error: search_plugin or catalog_plugin is required.")
    if query_command == "search-query" and not keyword:
        fail("Error: keyword is required for search workflows.")

    limit = str(args.get("limit") or "5").strip()
    index = int(str(args.get("index") or "1").strip())
    auto_run = str(args.get("auto_run") or "true").strip().lower() in {"1", "true", "yes", "on"}

    query_args = [query_command, f"plugin_id={resource_plugin}", f"limit={limit}"]
    if query_command == "search-query":
        query_args.append(f"keyword={keyword}")
    if query_command == "catalog-query" and keyword:
        query_args.append(f"filters_json={json.dumps({'keyword': keyword}, ensure_ascii=False)}")

    query_payload = run_cli(*query_args)
    items = query_payload.get("items", []) if isinstance(query_payload, dict) else []
    selected = pick_item([item for item in items if isinstance(item, dict)], index)
    resource_id = str(selected.get("id") or "").strip()
    if not resource_id:
        fail("Error: selected resource has no id.")

    action_result = run_cli(
        "run-resource-action",
        f"resource_id={resource_id}",
        f"action_key={action_key}",
        "payload_json={}",
    )
    if not isinstance(action_result, dict):
        fail("Error: unexpected action result.")
    if action_result.get("result_type") != "task_draft":
        fail(f"Error: resource action '{action_key}' did not return a task draft.")

    draft = dict(action_result.get("data") or {})
    created = run_cli("create-task", f"body_json={json.dumps(draft, ensure_ascii=False)}")
    task_item = created.get("item", {}) if isinstance(created, dict) else {}
    task_id = str(task_item.get("task_id") or "").strip()
    if auto_run and task_id:
        run_result = run_cli("run-task", f"task_id={task_id}", "wait_for_completion=false")
    else:
        run_result = {"skipped": True}
    return {
        "selected_resource": selected,
        "action_result": action_result,
        "created_task": created,
        "run_result": run_result,
    }


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: t3mt-workflow-ops.py <ensure-core|search-and-transfer|search-and-download|search-and-strm> [key=value ...]")

    command = sys.argv[1]
    args = parse_pairs(sys.argv[2:])

    if command == "ensure-core":
        ensured = [ensure_plugin(plugin_id) for plugin_id in CORE_PLUGIN_IDS]
        print(json.dumps({"items": ensured}, ensure_ascii=False, indent=2))
        return

    if command == "search-and-transfer":
        print(json.dumps(search_then_create_task("search-query", "task.transfer.create", args), ensure_ascii=False, indent=2))
        return

    if command == "search-and-download":
        print(json.dumps(search_then_create_task("catalog-query", "task.video_download.create", args), ensure_ascii=False, indent=2))
        return

    if command == "search-and-strm":
        print(json.dumps(search_then_create_task("catalog-query", "task.strm.create", args), ensure_ascii=False, indent=2))
        return

    fail(f"Error: unsupported workflow '{command}'.")


if __name__ == "__main__":
    main()
