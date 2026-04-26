#!/usr/bin/env python3
"""Plugin-focused assistant helper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


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


def classify_plugin(item: dict[str, object]) -> dict[str, object]:
    capabilities = {str(value) for value in item.get("capabilities") or []}
    category = str(item.get("category") or "").strip()
    inferred_roles: list[str] = []
    if category:
        inferred_roles.append(category)
    if any(cap.startswith("drive.") for cap in capabilities):
        inferred_roles.append("drive")
    if any(cap.startswith("task.") for cap in capabilities):
        inferred_roles.append("task")
    if any(cap.startswith("resource.search") for cap in capabilities):
        inferred_roles.append("search")
    if any(cap.startswith("resource.catalog") for cap in capabilities):
        inferred_roles.append("catalog")
    if any(cap.startswith("resource.") for cap in capabilities):
        inferred_roles.append("resource")
    if any(cap.startswith("assistant.") for cap in capabilities):
        inferred_roles.append("assistant")
    if any(cap.startswith("automation.") for cap in capabilities):
        inferred_roles.append("automation")
    return {
        "plugin_id": item.get("plugin_id") or item.get("id"),
        "name": item.get("name"),
        "category": category,
        "capabilities": sorted(capabilities),
        "roles": sorted(set(role for role in inferred_roles if role)),
        "dependencies": item.get("dependencies") or [],
        "allowed_actions": item.get("allowed_actions") or [],
    }


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: t3mt-plugin-ops.py <summary|inspect|classify|ensure> [key=value ...]")

    command = sys.argv[1]
    args = parse_pairs(sys.argv[2:])

    if command == "summary":
        payload = run_cli("plugins")
        items = payload.get("items", []) if isinstance(payload, dict) else []
        print(json.dumps([classify_plugin(item) for item in items if isinstance(item, dict)], ensure_ascii=False, indent=2))
        return

    plugin_id = str(args.get("plugin_id") or "").strip()
    if command in {"inspect", "classify", "ensure"} and not plugin_id:
        fail("Error: plugin_id is required.")

    if command == "inspect":
        plugin = run_cli("plugin", f"plugin_id={plugin_id}")
        config = run_cli("plugin-config", f"plugin_id={plugin_id}")
        health = run_cli("plugin-health", f"plugin_id={plugin_id}")
        print(
            json.dumps(
                {"plugin": plugin, "config": config, "health": health},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if command == "classify":
        plugin = run_cli("plugin", f"plugin_id={plugin_id}")
        if not isinstance(plugin, dict):
            fail("Error: unexpected plugin payload.")
        print(json.dumps(classify_plugin(plugin), ensure_ascii=False, indent=2))
        return

    if command == "ensure":
        source_type = str(args.get("source_type") or "bundled").strip()
        source_ref = str(args.get("source_ref") or plugin_id).strip()
        enable_after_install = str(args.get("enable_after_install") or "true").strip().lower()
        config_values_json = str(args.get("config_values_json") or "").strip()
        try:
            existing = run_cli("plugin", f"plugin_id={plugin_id}")
        except SystemExit:
            existing = None
        if not existing:
            install_args = [
                "install-plugin",
                f"source_type={source_type}",
                f"source_ref={source_ref}",
                f"enable_after_install={enable_after_install}",
            ]
            if config_values_json:
                install_args.append(f"config_values_json={config_values_json}")
            run_cli(*install_args)
        run_cli("enable-plugin", f"plugin_id={plugin_id}")
        print(json.dumps(run_cli("plugin", f"plugin_id={plugin_id}"), ensure_ascii=False, indent=2))
        return

    fail(f"Error: unsupported command '{command}'")


if __name__ == "__main__":
    main()
