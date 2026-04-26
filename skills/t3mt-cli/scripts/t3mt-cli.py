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
    "market-sources": ("market-sources", "Read market source URLs"),
    "update-market-sources": ("update-market-sources sources_json=<json-array>", "Update market source URLs"),
    "plugin": ("plugin plugin_id=<id>", "Show one plugin by plugin_id"),
    "plugin-health": ("plugin-health plugin_id=<id>", "Read one plugin health report"),
    "plugin-config": ("plugin-config plugin_id=<id>", "Read one plugin runtime config"),
    "update-plugin-config": ("update-plugin-config plugin_id=<id> values_json=<json-object>", "Update one plugin runtime config"),
    "install-plugin": ("install-plugin source_type=bundled source_ref=<id> [enable_after_install=true]", "Install a plugin"),
    "enable-plugin": ("enable-plugin plugin_id=<id>", "Enable a plugin"),
    "disable-plugin": ("disable-plugin plugin_id=<id>", "Disable a plugin"),
    "uninstall-plugin": ("uninstall-plugin plugin_id=<id>", "Uninstall a plugin"),
    "tasks": ("tasks", "List task definitions"),
    "task-templates": ("task-templates", "List available task templates"),
    "task": ("task task_id=<id>", "Show one task by task_id"),
    "create-task": ("create-task body_json=<json-object>", "Create a task definition"),
    "update-task": ("update-task task_id=<id> body_json=<json-object>", "Update a task definition"),
    "delete-task": ("delete-task task_id=<id>", "Delete one task definition"),
    "toggle-task": ("toggle-task task_id=<id> [enabled=true]", "Enable or disable one task"),
    "run-task": ("run-task task_id=<id> [wait_for_completion=true]", "Run one task definition"),
    "run-template": ("run-template plugin_id=<id> [config_json={}] [input_json={}] [triggered_by=manual]", "Run one task template without creating a saved task"),
    "cron-preview": ("cron-preview cron_expr=<expr> [timezone=Asia/Shanghai] [count=10]", "Preview cron run times"),
    "create-subscription": ("create-subscription resource_id=<id> mode=<mode>", "Create subscription tasks from a resource"),
    "catalog-batch-strm": ("catalog-batch-strm body_json=<json-object>", "Create a catalog batch STRM task"),
    "live-catalog-batch-strm": ("live-catalog-batch-strm body_json=<json-object>", "Create a live catalog batch STRM task"),
    "execution": ("execution execution_id=<id>", "Read one task execution"),
    "terminate-execution": ("terminate-execution execution_id=<id>", "Terminate one running execution"),
    "catalog-sources": ("catalog-sources", "List resource catalog providers"),
    "search-sources": ("search-sources", "List resource search providers"),
    "catalog-query": ("catalog-query plugin_id=<id> [filters_json={}] [limit=24]", "Query catalog resources"),
    "search-query": ("search-query plugin_id=<id> keyword=<text> [filters_json={}] [limit=24]", "Search resources by keyword"),
    "resource": ("resource resource_id=<id>", "Read one resource detail"),
    "resource-actions": ("resource-actions resource_id=<id>", "Read resource actions"),
    "run-resource-action": ("run-resource-action resource_id=<id> action_key=<key> [payload_json={}]", "Execute one resource action"),
    "drive-providers": ("drive-providers", "List drive providers"),
    "drive-provider": ("drive-provider plugin_id=<id>", "Show one drive provider contract"),
    "drive-account-form": ("drive-account-form plugin_id=<id>", "Read one drive provider account form"),
    "test-drive-account": ("test-drive-account plugin_id=<id> payload_json=<json-object>", "Validate drive account payload"),
    "create-drive-account": ("create-drive-account plugin_id=<id> payload_json=<json-object>", "Create one drive account"),
    "start-drive-scan": ("start-drive-scan plugin_id=<id> [options_json={}]", "Start scan login for a drive provider"),
    "drive-scan-status": ("drive-scan-status plugin_id=<id> scan_id=<id>", "Read scan login status"),
    "cancel-drive-scan": ("cancel-drive-scan plugin_id=<id> scan_id=<id>", "Cancel scan login"),
    "drive-accounts": ("drive-accounts [plugin_id=<id>]", "List drive accounts"),
    "drive-account": ("drive-account account_id=<id>", "Read one drive account"),
    "update-drive-account": ("update-drive-account account_id=<id> payload_json=<json-object>", "Update one drive account"),
    "refresh-drive-account": ("refresh-drive-account account_id=<id>", "Refresh one drive account"),
    "set-main-drive-account": ("set-main-drive-account account_id=<id>", "Set one drive account as main"),
    "delete-drive-account": ("delete-drive-account account_id=<id>", "Delete one drive account"),
    "drive-files": ("drive-files account_id=<id> [parent_id=0] [page=1] [page_size=100]", "List drive files"),
    "drive-path": ("drive-path account_id=<id> [item_id=0]", "Resolve one drive item path"),
    "drive-folders": ("drive-folders account_id=<id> [parent_id=0]", "List drive folders"),
    "create-drive-folder": ("create-drive-folder account_id=<id> name=<name> [parent_id=0]", "Create one drive folder"),
    "delete-drive-items": ("delete-drive-items account_id=<id> item_ids_json=<json-array>", "Delete drive items"),
    "drive-item": ("drive-item account_id=<id> item_id=<id>", "Read one drive item"),
    "read-drive-text": ("read-drive-text account_id=<id> item_id=<id>", "Read text content from a drive item"),
    "write-drive-text": ("write-drive-text account_id=<id> item_id=<id> content=<text> [encoding=utf-8]", "Write text content to a drive item"),
    "create-drive-share": ("create-drive-share account_id=<id> item_ids_json=<json-array> [options_json={}]", "Create drive share"),
    "parse-drive-share": ("parse-drive-share account_id=<id> share_ref_json=<json-object>", "Parse drive share reference"),
    "browse-drive-share": ("browse-drive-share account_id=<id> share_ref_json=<json-object> [parent_id=]", "Browse drive share"),
    "save-drive-share": ("save-drive-share account_id=<id> share_ref_json=<json-object> [target_parent_id=0] [selected_items_json=[]]", "Save drive share into an account"),
    "drive-download-link": ("drive-download-link account_id=<id> item_id=<id>", "Build drive download link"),
    "monitor": ("monitor", "Read monitor dashboard data"),
    "monitor-overview": ("monitor-overview", "Read monitor overview"),
    "monitor-system-realtime": ("monitor-system-realtime", "Read host/system realtime metrics"),
    "monitor-schedules": ("monitor-schedules", "List scheduled jobs"),
    "monitor-executions": ("monitor-executions [limit=100] [status=failed] [trigger_source=manual]", "List recent task executions"),
    "monitor-plugin-health": ("monitor-plugin-health", "Read plugin health summary"),
    "task-template-settings": ("task-template-settings", "Read task template center settings"),
    "update-task-template-settings": ("update-task-template-settings body_json=<json-object>", "Update task template center settings"),
    "api-key": ("api-key", "Read API key metadata"),
    "reset-api-key": ("reset-api-key", "Reset API key"),
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


def body_from_arg(args: dict[str, str], key: str) -> object:
    value = args.get(key, "")
    parsed = parse_json(value, None)
    if parsed is None:
        fail(f"Error: missing required JSON argument '{key}'")
    return parsed


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
    elif command_name == "market-sources":
        request = {"method": "GET", "path": "/api/plugins/market/sources"}
    elif command_name == "update-market-sources":
        request = {"method": "PUT", "path": "/api/plugins/market/sources", "body": {"sources": body_from_arg(args, "sources_json")}}
    elif command_name == "plugin":
        request = {"method": "GET", "path": f"/api/plugins/{required(args, 'plugin_id')}"}
    elif command_name == "plugin-health":
        request = {"method": "GET", "path": f"/api/plugins/{required(args, 'plugin_id')}/health"}
    elif command_name == "plugin-config":
        request = {"method": "GET", "path": f"/api/plugins/{required(args, 'plugin_id')}/config"}
    elif command_name == "update-plugin-config":
        request = {
            "method": "PUT",
            "path": f"/api/plugins/{required(args, 'plugin_id')}/config",
            "body": {"values": body_from_arg(args, "values_json")},
        }
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
    elif command_name == "uninstall-plugin":
        request = {"method": "DELETE", "path": f"/api/plugins/{required(args, 'plugin_id')}"}
    elif command_name == "tasks":
        request = {"method": "GET", "path": "/api/tasks"}
    elif command_name == "task-templates":
        request = {"method": "GET", "path": "/api/tasks/templates"}
    elif command_name == "task":
        request = {"method": "GET", "path": f"/api/tasks/{required(args, 'task_id')}"}
    elif command_name == "create-task":
        request = {"method": "POST", "path": "/api/tasks", "body": body_from_arg(args, "body_json")}
    elif command_name == "update-task":
        request = {"method": "PUT", "path": f"/api/tasks/{required(args, 'task_id')}", "body": body_from_arg(args, "body_json")}
    elif command_name == "delete-task":
        request = {"method": "DELETE", "path": f"/api/tasks/{required(args, 'task_id')}"}
    elif command_name == "toggle-task":
        request = {
            "method": "POST",
            "path": f"/api/tasks/{required(args, 'task_id')}/toggle",
            "body": {"enabled": to_bool(args.get("enabled") or "true")},
        }
    elif command_name == "run-task":
        request = {
            "method": "POST",
            "path": f"/api/tasks/{required(args, 'task_id')}/run",
            "body": {"wait_for_completion": to_bool(args.get("wait_for_completion"))},
        }
    elif command_name == "run-template":
        request = {
            "method": "POST",
            "path": f"/api/tasks/run/{required(args, 'plugin_id')}",
            "body": {
                "config": parse_json(args.get("config_json"), {}) or {},
                "input_data": parse_json(args.get("input_json"), {}) or {},
                "triggered_by": args.get("triggered_by") or "manual",
            },
        }
    elif command_name == "cron-preview":
        request = {
            "method": "POST",
            "path": "/api/tasks/cron/preview",
            "body": {
                "cron_expr": required(args, "cron_expr"),
                "timezone": args.get("timezone") or "Asia/Shanghai",
                "count": int(args.get("count") or 10),
            },
        }
    elif command_name == "create-subscription":
        request = {
            "method": "POST",
            "path": "/api/tasks/subscriptions",
            "body": {"resource_id": required(args, "resource_id"), "mode": required(args, "mode")},
        }
    elif command_name == "catalog-batch-strm":
        request = {"method": "POST", "path": "/api/tasks/catalog-batch-strm", "body": body_from_arg(args, "body_json")}
    elif command_name == "live-catalog-batch-strm":
        request = {"method": "POST", "path": "/api/tasks/live-catalog-batch-strm", "body": body_from_arg(args, "body_json")}
    elif command_name == "execution":
        request = {"method": "GET", "path": f"/api/tasks/executions/{required(args, 'execution_id')}"}
    elif command_name == "terminate-execution":
        request = {"method": "POST", "path": f"/api/tasks/executions/{required(args, 'execution_id')}/terminate", "body": {}}
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
                "filters": parse_json(args.get("filters_json"), {}) or {},
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
                "filters": parse_json(args.get("filters_json"), {}) or {},
                "limit": int(args.get("limit") or 24),
            },
        }
    elif command_name == "resource":
        request = {"method": "GET", "path": f"/api/resources/{required(args, 'resource_id')}"}
    elif command_name == "resource-actions":
        request = {"method": "GET", "path": f"/api/resources/{required(args, 'resource_id')}/actions"}
    elif command_name == "run-resource-action":
        request = {
            "method": "POST",
            "path": f"/api/resources/{required(args, 'resource_id')}/actions/{required(args, 'action_key')}",
            "body": {"payload": parse_json(args.get("payload_json"), {}) or {}},
        }
    elif command_name == "drive-providers":
        request = {"method": "GET", "path": "/api/drive/providers"}
    elif command_name == "drive-provider":
        request = {"method": "GET", "path": f"/api/drive/providers/{required(args, 'plugin_id')}"}
    elif command_name == "drive-account-form":
        request = {"method": "GET", "path": f"/api/drive/providers/{required(args, 'plugin_id')}/account-form"}
    elif command_name == "test-drive-account":
        request = {
            "method": "POST",
            "path": f"/api/drive/providers/{required(args, 'plugin_id')}/accounts/test",
            "body": {"payload": body_from_arg(args, "payload_json")},
        }
    elif command_name == "create-drive-account":
        request = {
            "method": "POST",
            "path": f"/api/drive/providers/{required(args, 'plugin_id')}/accounts",
            "body": {"payload": body_from_arg(args, "payload_json")},
        }
    elif command_name == "start-drive-scan":
        request = {
            "method": "POST",
            "path": f"/api/drive/providers/{required(args, 'plugin_id')}/scan/start",
            "body": {"options": parse_json(args.get("options_json"), {}) or {}},
        }
    elif command_name == "drive-scan-status":
        request = {"method": "GET", "path": f"/api/drive/providers/{required(args, 'plugin_id')}/scan/{required(args, 'scan_id')}"}
    elif command_name == "cancel-drive-scan":
        request = {"method": "DELETE", "path": f"/api/drive/providers/{required(args, 'plugin_id')}/scan/{required(args, 'scan_id')}"}
    elif command_name == "drive-accounts":
        request = {"method": "GET", "path": "/api/drive/accounts", "query": pick(args, ["plugin_id"])}
    elif command_name == "drive-account":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}"}
    elif command_name == "update-drive-account":
        request = {
            "method": "PUT",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}",
            "body": {"payload": body_from_arg(args, "payload_json")},
        }
    elif command_name == "refresh-drive-account":
        request = {"method": "POST", "path": f"/api/drive/accounts/{required(args, 'account_id')}/refresh", "body": {}}
    elif command_name == "set-main-drive-account":
        request = {"method": "POST", "path": f"/api/drive/accounts/{required(args, 'account_id')}/set-main", "body": {}}
    elif command_name == "delete-drive-account":
        request = {"method": "DELETE", "path": f"/api/drive/accounts/{required(args, 'account_id')}"}
    elif command_name == "drive-files":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/files", "query": pick(args, ["parent_id", "page", "page_size"])}
    elif command_name == "drive-path":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/resolve-path", "query": pick(args, ["item_id"])}
    elif command_name == "drive-folders":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/folders", "query": pick(args, ["parent_id"])}
    elif command_name == "create-drive-folder":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/folders",
            "body": {"parent_id": args.get("parent_id") or "0", "name": required(args, "name")},
        }
    elif command_name == "delete-drive-items":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/delete",
            "body": {"item_ids": body_from_arg(args, "item_ids_json")},
        }
    elif command_name == "drive-item":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/items/{required(args, 'item_id')}"}
    elif command_name == "read-drive-text":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/items/{required(args, 'item_id')}/text"}
    elif command_name == "write-drive-text":
        request = {
            "method": "PUT",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/items/{required(args, 'item_id')}/text",
            "body": {"content": required(args, "content"), "encoding": args.get("encoding") or None},
        }
    elif command_name == "create-drive-share":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/share/create",
            "body": {"item_ids": body_from_arg(args, "item_ids_json"), "options": parse_json(args.get("options_json"), {}) or {}},
        }
    elif command_name == "parse-drive-share":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/share/parse",
            "body": {"share_ref": body_from_arg(args, "share_ref_json")},
        }
    elif command_name == "browse-drive-share":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/share/browse",
            "body": {"share_ref": body_from_arg(args, "share_ref_json"), "parent_id": args.get("parent_id") or None},
        }
    elif command_name == "save-drive-share":
        request = {
            "method": "POST",
            "path": f"/api/drive/accounts/{required(args, 'account_id')}/share/save",
            "body": {
                "share_ref": body_from_arg(args, "share_ref_json"),
                "target_parent_id": args.get("target_parent_id") or "0",
                "selected_items": parse_json(args.get("selected_items_json"), None),
            },
        }
    elif command_name == "drive-download-link":
        request = {"method": "GET", "path": f"/api/drive/accounts/{required(args, 'account_id')}/download/{required(args, 'item_id')}"}
    elif command_name == "monitor":
        request = {"method": "GET", "path": "/api/monitor/dashboard"}
    elif command_name == "monitor-overview":
        request = {"method": "GET", "path": "/api/monitor/overview"}
    elif command_name == "monitor-system-realtime":
        request = {"method": "GET", "path": "/api/monitor/system/realtime"}
    elif command_name == "monitor-schedules":
        request = {"method": "GET", "path": "/api/monitor/schedules"}
    elif command_name == "monitor-executions":
        request = {
            "method": "GET",
            "path": "/api/monitor/executions",
            "query": pick(args, ["limit", "status", "trigger_source"]),
        }
    elif command_name == "monitor-plugin-health":
        request = {"method": "GET", "path": "/api/monitor/plugin-health"}
    elif command_name == "task-template-settings":
        request = {"method": "GET", "path": "/api/settings/task-templates"}
    elif command_name == "update-task-template-settings":
        request = {"method": "PUT", "path": "/api/settings/task-templates", "body": body_from_arg(args, "body_json")}
    elif command_name == "api-key":
        request = {"method": "GET", "path": "/api/auth/api-key"}
    elif command_name == "reset-api-key":
        request = {"method": "POST", "path": "/api/auth/api-key/reset", "body": {}}
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
        print(f"  {name.ljust(28)} {description}")


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
