#!/usr/bin/env python3
"""Common T3MT/T3FAP command wrapper."""

from __future__ import annotations

import json
import os
from pathlib import Path
import ssl
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request


SCRIPT_NAME = os.path.basename(sys.argv[0]) if sys.argv else "t3mt-cli.py"
CONFIG_DIR = Path.home() / ".config" / "t3mt_cli"
CONFIG_FILE = CONFIG_DIR / "config"
DEFAULT_HOST = "http://t3fap:8521"

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

COMMANDS = {
    "plugins": ("plugins", "List installed and discovered plugins"),
    "market": ("market [force_refresh=true]", "List remote plugin market catalog"),
    "plugin": ("plugin plugin_id=<id>", "Show one plugin by plugin_id"),
    "install-plugin": ("install-plugin source_type=bundled source_ref=<id> [enable_after_install=true]", "Install a plugin"),
    "enable-plugin": ("enable-plugin plugin_id=<id>", "Enable a plugin"),
    "disable-plugin": ("disable-plugin plugin_id=<id>", "Disable a plugin"),
    "tasks": ("tasks", "List task definitions"),
    "task-templates": ("task-templates", "List available task templates"),
    "task": ("task task_id=<id>", "Show one task by task_id"),
    "run-task": ("run-task task_id=<id> [wait_for_completion=true]", "Run one task definition"),
    "catalog-sources": ("catalog-sources", "List resource catalog providers"),
    "search-sources": ("search-sources", "List resource search providers"),
    "catalog-query": ("catalog-query plugin_id=<id> [filters_json={}] [limit=24]", "Query catalog resources"),
    "search-query": ("search-query plugin_id=<id> keyword=<text> [filters_json={}] [limit=24]", "Search resources by keyword"),
    "drive-providers": ("drive-providers", "List drive providers"),
    "drive-accounts": ("drive-accounts", "List drive accounts"),
    "monitor": ("monitor", "Read monitor dashboard data"),
    "monitor-schedules": ("monitor-schedules", "List scheduled jobs"),
    "task-template-settings": ("task-template-settings", "Read task template center settings"),
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def read_config() -> tuple[str, str]:
    host = ""
    api_key = ""
    if not CONFIG_FILE.exists():
        return host, api_key
    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "T3MT_HOST":
            host = value.strip()
        elif key.strip() == "T3MT_API_KEY":
            api_key = value.strip()
    return host, api_key


def save_config(host: str, api_key: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(f"T3MT_HOST={host}\nT3MT_API_KEY={api_key}\n", encoding="utf-8")
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)


def resolve_config(cli_host: str = "", cli_key: str = "") -> tuple[str, str]:
    file_host, file_key = read_config()
    host = cli_host or os.environ.get("T3MT_HOST", "") or file_host or DEFAULT_HOST
    api_key = cli_key or os.environ.get("T3MT_API_KEY", "") or file_key
    return host.rstrip("/"), api_key


def parse_arg_pairs(items: list[str]) -> dict[str, str]:
    args: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            fail(f"Error: argument must be key=value, got '{item}'")
        key, _, value = item.partition("=")
        args[key] = value
    return args


def required(args: dict[str, str], name: str) -> str:
    value = args.get(name, "").strip()
    if not value:
        fail(f"Error: missing required argument '{name}'")
    return value


def to_bool(value: str | None) -> bool:
    return str(value or "").lower() in {"1", "true", "yes", "on"}


def parse_json(value: str | None, fallback: object | None) -> object | None:
    if value is None or value == "":
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        fail(f"Error: invalid JSON argument: {exc}")


def pick(args: dict[str, str], names: list[str]) -> dict[str, str]:
    return {name: args[name] for name in names if args.get(name, "") != ""}


def build_command_request(
    command_name: str,
    args: dict[str, str],
    json_override: str | None,
) -> dict[str, object]:
    request: dict[str, object]

    if command_name == "plugins":
        request = {"method": "GET", "path": "/api/plugins"}
    elif command_name == "market":
        request = {"method": "GET", "path": "/api/plugins/market/catalog", "query": pick(args, ["force_refresh"])}
    elif command_name == "plugin":
        request = {"method": "GET", "path": f"/api/plugins/{required(args, 'plugin_id')}"}
    elif command_name == "install-plugin":
        request = {
            "method": "POST",
            "path": "/api/plugins/install",
            "body": {
                "source_type": required(args, "source_type"),
                "source_ref": required(args, "source_ref"),
                "market_source_url": args.get("market_source_url") or None,
                "enable_after_install": to_bool(args.get("enable_after_install")),
                "config_values": parse_json(args.get("config_values_json"), None),
            },
        }
    elif command_name == "enable-plugin":
        request = {"method": "POST", "path": f"/api/plugins/{required(args, 'plugin_id')}/enable", "body": {}}
    elif command_name == "disable-plugin":
        request = {"method": "POST", "path": f"/api/plugins/{required(args, 'plugin_id')}/disable", "body": {}}
    elif command_name == "tasks":
        request = {"method": "GET", "path": "/api/tasks"}
    elif command_name == "task-templates":
        request = {"method": "GET", "path": "/api/tasks/templates"}
    elif command_name == "task":
        request = {"method": "GET", "path": f"/api/tasks/{required(args, 'task_id')}"}
    elif command_name == "run-task":
        request = {
            "method": "POST",
            "path": f"/api/tasks/{required(args, 'task_id')}/run",
            "body": {"wait_for_completion": to_bool(args.get("wait_for_completion"))},
        }
    elif command_name == "catalog-sources":
        request = {"method": "GET", "path": "/api/resources/catalog/sources"}
    elif command_name == "search-sources":
        request = {"method": "GET", "path": "/api/resources/search/sources"}
    elif command_name == "catalog-query":
        request = {
            "method": "POST",
            "path": "/api/resources/catalog/query",
            "body": {
                "plugin_id": required(args, "plugin_id"),
                "filters": parse_json(args.get("filters_json"), {}),
                "limit": int(args.get("limit") or 24),
            },
        }
    elif command_name == "search-query":
        request = {
            "method": "POST",
            "path": "/api/resources/search/query",
            "body": {
                "plugin_id": required(args, "plugin_id"),
                "keyword": required(args, "keyword"),
                "filters": parse_json(args.get("filters_json"), {}),
                "limit": int(args.get("limit") or 24),
            },
        }
    elif command_name == "drive-providers":
        request = {"method": "GET", "path": "/api/drive/providers"}
    elif command_name == "drive-accounts":
        request = {"method": "GET", "path": "/api/drive/accounts"}
    elif command_name == "monitor":
        request = {"method": "GET", "path": "/api/monitor/dashboard"}
    elif command_name == "monitor-schedules":
        request = {"method": "GET", "path": "/api/monitor/schedules"}
    elif command_name == "task-template-settings":
        request = {"method": "GET", "path": "/api/settings/task-templates"}
    else:
        fail(f"Error: unknown command '{command_name}'. Run '{SCRIPT_NAME} list'.")

    if json_override is not None:
        request["body"] = parse_json(json_override, {})
    return request


def build_api_request(args: list[str], json_override: str | None) -> dict[str, object]:
    if len(args) < 2:
        fail("Usage: api <METHOD> <PATH> [key=value ...] [--json BODY]")
    return {
        "method": args[0].upper(),
        "path": args[1],
        "query": parse_arg_pairs(args[2:]),
        "body": parse_json(json_override, None),
    }


def build_url(host: str, api_path: str, query: dict[str, str] | None) -> str:
    normalized_path = api_path if api_path.startswith("/") else f"/{api_path}"
    url = f"{host.rstrip('/')}{normalized_path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return url


def request(method: str, target_url: str, api_key: str, body: object | None, timeout: int = 120) -> tuple[int, str]:
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(target_url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, f"Connection error: {exc.reason}"


def print_value(raw: str) -> None:
    try:
        print(json.dumps(json.loads(raw), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(raw)


def print_usage() -> None:
    print(f"Usage: {SCRIPT_NAME} [--host HOST] [--apikey KEY] <command> [key=value ...] [--json BODY]\n")
    print("Configuration:")
    print(f"  {SCRIPT_NAME} configure --host {DEFAULT_HOST} --apikey <T3MT_API_KEY>")
    print("  or set T3MT_HOST and T3MT_API_KEY\n")
    print("Commands:")
    print("  list")
    print("  show <command>")
    print("  api <METHOD> <PATH> [key=value ...] [--json BODY]")
    for name, (_, description) in COMMANDS.items():
        print(f"  {name.ljust(24)} {description}")


def print_list() -> None:
    for name in sorted(COMMANDS):
        print(name)
    print("api")


def print_show(name: str) -> None:
    if name == "api":
        print("Command: api")
        print("Usage: api <METHOD> <PATH> [key=value ...] [--json BODY]")
        print("Description: Call any T3MT REST endpoint directly.")
        return
    usage_description = COMMANDS.get(name)
    if usage_description is None:
        fail(f"Error: command '{name}' was not found")
    usage, description = usage_description
    print(f"Command: {name}")
    print(f"Usage: {usage}")
    print(f"Description: {description}")


def parse_cli(argv: list[str]) -> tuple[str, str, str | None, list[str]]:
    host_opt = ""
    key_opt = ""
    json_body = None
    args: list[str] = []

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg in {"--help", "-?"}:
            print_usage()
            raise SystemExit(0)
        if arg == "--host":
            index += 1
            host_opt = argv[index] if index < len(argv) else ""
        elif arg == "--apikey":
            index += 1
            key_opt = argv[index] if index < len(argv) else ""
        elif arg == "--json":
            index += 1
            json_body = argv[index] if index < len(argv) else "{}"
        else:
            args.append(arg)
        index += 1

    return host_opt, key_opt, json_body, args


def main() -> None:
    host_opt, key_opt, json_body, args = parse_cli(sys.argv[1:])

    if not args:
        print_usage()
        return

    if args[0] == "configure":
        if not host_opt or not key_opt:
            fail("Error: configure requires --host and --apikey")
        save_config(host_opt.rstrip("/"), key_opt)
        print("Configuration saved.")
        return

    command_name = args[0]
    if command_name == "list":
        print_list()
        return
    if command_name == "show":
        print_show(args[1] if len(args) > 1 else "")
        return

    host, api_key = resolve_config(host_opt, key_opt)
    if not api_key:
        fail("Error: T3MT_API_KEY is not configured.")
    if host_opt or key_opt:
        save_config(host, api_key)

    if command_name == "api":
        request_spec = build_api_request(args[1:], json_body)
    else:
        request_spec = build_command_request(command_name, parse_arg_pairs(args[1:]), json_body)

    status, raw = request(
        str(request_spec["method"]),
        build_url(host, str(request_spec["path"]), request_spec.get("query") or None),
        api_key,
        request_spec.get("body"),
    )
    if status and status >= 400:
        print(f"HTTP {status}", file=sys.stderr)
    print_value(raw)
    if status and status >= 400:
        raise SystemExit(1)
    if status == 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
