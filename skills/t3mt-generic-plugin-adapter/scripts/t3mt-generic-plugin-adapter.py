#!/usr/bin/env python3
"""Generic adapter for unknown or third-party T3MT/T3FAP plugins."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


CLI_PATH = Path(__file__).resolve().parents[2] / "t3mt-cli" / "scripts" / "t3mt-cli.py"


ROLE_TO_SKILL = {
    "drive": "t3mt-drive-ops",
    "task": "t3mt-task-ops",
    "search": "t3mt-resource-ops",
    "catalog": "t3mt-resource-ops",
    "resource": "t3mt-resource-ops",
    "automation": "t3mt-plugin-ops",
    "assistant": "t3mt-plugin-ops",
    "parser": "t3mt-plugin-ops",
    "download": "t3mt-plugin-ops",
    "media": "t3mt-plugin-ops",
}


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


def infer_roles(plugin: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    category = str(plugin.get("category") or "").strip().lower()
    if category:
        roles.append(category)
    for role in plugin.get("provider_types") or []:
        role_text = str(role or "").strip().lower()
        if role_text:
            roles.append(role_text)
    capabilities = {str(value or "").strip().lower() for value in plugin.get("capabilities") or []}
    if any(cap.startswith("drive.") for cap in capabilities):
        roles.append("drive")
    if any(cap.startswith("task.") for cap in capabilities):
        roles.append("task")
    if any(cap.startswith("resource.search") for cap in capabilities):
        roles.append("search")
    if any(cap.startswith("resource.catalog") for cap in capabilities):
        roles.append("catalog")
    if any(cap.startswith("resource.") for cap in capabilities):
        roles.append("resource")
    if any(cap.startswith("automation.") for cap in capabilities):
        roles.append("automation")
    if any(cap.startswith("assistant.") for cap in capabilities):
        roles.append("assistant")
    return sorted(set(role for role in roles if role))


def pick_domain_skill(roles: list[str]) -> str:
    for role in roles:
        skill = ROLE_TO_SKILL.get(role)
        if skill:
            return skill
    return "t3mt-plugin-ops"


def filter_task_templates(plugin_id: str, payload: object) -> list[dict[str, Any]]:
    items = payload.get("items", []) if isinstance(payload, dict) else []
    return [
        item
        for item in items
        if isinstance(item, dict) and str(item.get("plugin_id") or "").strip() == plugin_id
    ]


def match_resource_source(plugin_id: str, payload: object) -> dict[str, Any] | None:
    items = payload if isinstance(payload, list) else payload.get("items", []) if isinstance(payload, dict) else []
    for item in items:
        if isinstance(item, dict) and str(item.get("plugin_id") or "").strip() == plugin_id:
            return item
    return None


def build_suggested_commands(plugin_id: str, roles: list[str]) -> list[str]:
    commands = [
        f"python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py inspect plugin_id={plugin_id}",
    ]
    if "drive" in roles:
        commands.extend(
            [
                f"python ../t3mt-drive-ops/scripts/t3mt-drive-ops.py provider plugin_id={plugin_id}",
                f"python ../t3mt-drive-ops/scripts/t3mt-drive-ops.py account-form plugin_id={plugin_id}",
            ]
        )
    if "task" in roles:
        commands.append("python ../t3mt-task-ops/scripts/t3mt-task-ops.py templates")
    if "search" in roles:
        commands.append("python ../t3mt-resource-ops/scripts/t3mt-resource-ops.py search-sources")
    if "catalog" in roles:
        commands.append("python ../t3mt-resource-ops/scripts/t3mt-resource-ops.py catalog-sources")
    return commands


def build_redline_hints(plugin: dict[str, Any], roles: list[str]) -> list[str]:
    hints: list[str] = []
    allowed_actions = {str(value or "").strip().lower() for value in plugin.get("allowed_actions") or []}
    if "uninstall" in allowed_actions:
        hints.append("uninstall requires care because it can remove plugin state")
    if "drive" in roles:
        hints.append("account deletion or secret overwrite is redline-sensitive")
    if "task" in roles:
        hints.append("bulk task rewrites or broad config changes should be reviewed carefully")
    if any(field.get("secret") for field in (plugin.get("config", {}) or {}).get("schema", []) if isinstance(field, dict)):
        hints.append("plugin config contains secret fields")
    return hints


def build_playbook(plugin_id: str, roles: list[str], plugin: dict[str, Any]) -> dict[str, Any]:
    preflight_checks = [
        f"python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py inspect plugin_id={plugin_id}",
    ]
    activation_steps = [f"python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py ensure plugin_id={plugin_id}"]
    next_actions: list[str] = []

    if "drive" in roles:
        preflight_checks.extend(
            [
                f"python ../t3mt-drive-ops/scripts/t3mt-drive-ops.py provider plugin_id={plugin_id}",
                f"python ../t3mt-drive-ops/scripts/t3mt-drive-ops.py account-form plugin_id={plugin_id}",
            ]
        )
        next_actions.append("create or refresh one drive account, then verify file listing")
    if "task" in roles:
        preflight_checks.append("python ../t3mt-task-ops/scripts/t3mt-task-ops.py templates")
        next_actions.append("inspect template contract, then create one focused task draft")
    if "search" in roles:
        preflight_checks.append("python ../t3mt-resource-ops/scripts/t3mt-resource-ops.py search-sources")
        next_actions.append("run a keyword search before attempting downstream task creation")
    if "catalog" in roles:
        preflight_checks.append("python ../t3mt-resource-ops/scripts/t3mt-resource-ops.py catalog-sources")
        next_actions.append("query one catalog page and inspect resource actions before automation")
    if not next_actions:
        next_actions.append("inspect config schema and allowed actions before applying targeted config values")

    return {
        "plugin_id": plugin_id,
        "plugin_name": plugin.get("name"),
        "roles": roles,
        "preflight_checks": preflight_checks,
        "activation_steps": activation_steps,
        "next_actions": next_actions,
    }


def adapt_plugin(plugin_id: str) -> dict[str, Any]:
    plugin = run_cli("plugin", f"plugin_id={plugin_id}")
    if not isinstance(plugin, dict):
        fail("Error: unexpected plugin payload.")

    roles = infer_roles(plugin)
    profile: dict[str, Any] = {
        "plugin": plugin,
        "roles": roles,
        "recommended_skill": pick_domain_skill(roles),
        "suggested_commands": build_suggested_commands(plugin_id, roles),
    }

    if "drive" in roles:
        profile["drive_provider"] = run_cli("drive-provider", f"plugin_id={plugin_id}")
        profile["drive_account_form"] = run_cli("drive-account-form", f"plugin_id={plugin_id}")

    if "task" in roles:
        profile["task_templates"] = filter_task_templates(plugin_id, run_cli("task-templates"))

    if "search" in roles:
        profile["search_source"] = match_resource_source(plugin_id, run_cli("search-sources"))

    if "catalog" in roles:
        profile["catalog_source"] = match_resource_source(plugin_id, run_cli("catalog-sources"))

    profile["redline_hints"] = build_redline_hints(plugin, roles)
    profile["playbook"] = build_playbook(plugin_id, roles, plugin)
    return profile


def main() -> None:
    if len(sys.argv) < 2:
        fail("Usage: t3mt-generic-plugin-adapter.py <adapt|playbook> plugin_id=<PLUGIN_ID>")

    command = sys.argv[1]
    args = parse_pairs(sys.argv[2:])

    if command not in {"adapt", "playbook"}:
        fail(f"Error: unsupported command '{command}'.")

    plugin_id = str(args.get("plugin_id") or "").strip()
    if not plugin_id:
        fail("Error: plugin_id is required.")

    profile = adapt_plugin(plugin_id)
    if command == "playbook":
        print(json.dumps(profile.get("playbook"), ensure_ascii=False, indent=2))
        return
    print(json.dumps(profile, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
