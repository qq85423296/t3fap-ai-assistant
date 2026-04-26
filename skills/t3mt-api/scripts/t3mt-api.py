#!/usr/bin/env python3
"""T3MT/T3FAP REST API CLI."""

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


SCRIPT_NAME = os.path.basename(sys.argv[0]) if sys.argv else "t3mt-api.py"
CONFIG_DIR = Path.home() / ".config" / "t3mt_api"
CONFIG_FILE = CONFIG_DIR / "config"
DEFAULT_HOST = "http://t3fap:8521"

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


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


def build_url(host: str, path: str, query_params: dict[str, str] | None = None) -> str:
    if not path.startswith("/"):
        path = "/" + path
    url = host.rstrip("/") + path
    if query_params:
        url += "?" + urllib.parse.urlencode(query_params)
    return url


def http_request(
    method: str,
    url: str,
    api_key: str,
    body: object | None,
    timeout: int,
) -> tuple[int, str]:
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=SSL_CONTEXT) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 0, f"Connection error: {exc.reason}"


def print_json(value: object) -> None:
    if isinstance(value, str):
        print(value)
        return
    print(json.dumps(value, indent=2, ensure_ascii=False))


def parse_json_body(raw: str | None) -> object | None:
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON body: {exc}", file=sys.stderr)
        sys.exit(1)


def print_usage() -> None:
    print(
        f"""Usage:
  python {SCRIPT_NAME} configure --host <HOST> --apikey <KEY>
  python {SCRIPT_NAME} [--host HOST] [--apikey KEY] <METHOD> <PATH> [key=value ...] [--json '<body>']

Options:
  --host HOST       T3MT/T3FAP site origin, default {DEFAULT_HOST}
  --apikey KEY      API key copied from the user app API Access dialog
  --timeout SECS    Request timeout, default 120
  --json BODY       JSON request body for POST/PUT/PATCH
  --help            Show this help
"""
    )


def main() -> None:
    argv = sys.argv[1:]
    if not argv or "--help" in argv or "-h" in argv:
        print_usage()
        return

    cli_host = ""
    cli_key = ""
    timeout = 120
    json_body = None
    positional: list[str] = []

    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--host":
            index += 1
            cli_host = argv[index] if index < len(argv) else ""
        elif arg == "--apikey":
            index += 1
            cli_key = argv[index] if index < len(argv) else ""
        elif arg == "--timeout":
            index += 1
            timeout = int(argv[index]) if index < len(argv) else 120
        elif arg == "--json":
            index += 1
            json_body = argv[index] if index < len(argv) else "{}"
        else:
            positional.append(arg)
        index += 1

    if positional and positional[0].lower() == "configure":
        if not cli_host or not cli_key:
            print("Error: configure requires --host and --apikey", file=sys.stderr)
            sys.exit(1)
        save_config(cli_host.rstrip("/"), cli_key)
        print("Configuration saved.")
        return

    if len(positional) < 2:
        print("Error: expected <METHOD> <PATH>", file=sys.stderr)
        print_usage()
        sys.exit(1)

    method = positional[0].upper()
    path = positional[1]
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        print(f"Error: unsupported method: {method}", file=sys.stderr)
        sys.exit(1)

    query_params: dict[str, str] = {}
    for item in positional[2:]:
        if "=" not in item:
            print(f"Warning: ignoring argument without '=': {item}", file=sys.stderr)
            continue
        key, _, value = item.partition("=")
        query_params[key] = value

    host, api_key = resolve_config(cli_host, cli_key)
    if not api_key:
        print("Error: T3MT_API_KEY is not configured.", file=sys.stderr)
        sys.exit(1)
    if cli_host or cli_key:
        save_config(host, api_key)

    status, raw = http_request(
        method=method,
        url=build_url(host, path, query_params or None),
        api_key=api_key,
        body=parse_json_body(json_body),
        timeout=timeout,
    )
    if status and status >= 400:
        print(f"HTTP {status}", file=sys.stderr)

    try:
        payload: object = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw
    print_json(payload)
    if status and status >= 400:
        sys.exit(1)
    if status == 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
