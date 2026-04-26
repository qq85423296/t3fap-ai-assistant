#!/usr/bin/env python3
"""Runtime bootstrap for the T3FAP PicoClaw assistant image."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Mapping, MutableMapping, Sequence

# When this file is launched via an absolute script path inside Docker,
# Python adds `/opt/t3fap-ai-assistant/runtime` to sys.path instead of the
# project root. Make sure the top-level `runtime` package stays importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime.t3mt_automation import (
    DEFAULT_CONFIRM_REDLINE_ACTIONS,
    normalize_automation_mode,
    parse_bool,
)

DEFAULT_T3MT_HOST = "http://t3fap:8521"
DEFAULT_MODEL_NAME = "gpt-5.4"
DEFAULT_MODEL = "openai/gpt-5.4"
DEFAULT_MODEL_API_BASE = "https://api.openai.com/v1"
DEFAULT_PICOCLAW_HOME = Path.home() / ".picoclaw"
DEFAULT_GATEWAY_HOST = "0.0.0.0"
DEFAULT_GATEWAY_PORT = 18790
DEFAULT_LOG_LEVEL = "info"
DEFAULT_AUTOMATION_MODE = "full-access"


class RuntimeConfig:
    def __init__(
        self,
        *,
        picoclaw_home: Path,
        config_path: Path,
        workspace_dir: Path,
        t3mt_host: str,
        t3mt_api_key: str,
        automation_mode: str,
        model_name: str,
        model: str,
        model_api_key: str,
        model_api_base: str,
        pico_token: str,
        gateway_host: str,
        gateway_port: int,
        log_level: str,
        confirm_redline_actions: bool,
    ) -> None:
        self.picoclaw_home = picoclaw_home
        self.config_path = config_path
        self.workspace_dir = workspace_dir
        self.t3mt_host = t3mt_host
        self.t3mt_api_key = t3mt_api_key
        self.automation_mode = automation_mode
        self.model_name = model_name
        self.model = model
        self.model_api_key = model_api_key
        self.model_api_base = model_api_base
        self.pico_token = pico_token
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        self.log_level = log_level
        self.confirm_redline_actions = confirm_redline_actions


def _clean(value: str | None, default: str = "") -> str:
    if value is None:
        return default
    value = value.strip()
    return value if value else default


def _path_from_env(value: str | None, default: Path) -> Path:
    raw = _clean(value)
    if not raw:
        return default
    return Path(raw).expanduser()


def _int_from_env(value: str | None, default: int) -> int:
    raw = _clean(value)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def build_runtime_config(env: Mapping[str, str]) -> RuntimeConfig:
    picoclaw_home = _path_from_env(env.get("PICOCLAW_HOME"), DEFAULT_PICOCLAW_HOME)
    config_path = _path_from_env(env.get("PICOCLAW_CONFIG"), picoclaw_home / "config.json")
    workspace_dir = _path_from_env(
        env.get("T3FAP_ASSISTANT_WORKSPACE") or env.get("PICOCLAW_WORKSPACE"),
        picoclaw_home / "workspace",
    )

    model_name = _clean(env.get("T3FAP_ASSISTANT_MODEL_NAME"), DEFAULT_MODEL_NAME)
    model = _clean(env.get("T3FAP_ASSISTANT_MODEL"), DEFAULT_MODEL if model_name == DEFAULT_MODEL_NAME else f"openai/{model_name}")
    model_api_key = _clean(env.get("T3FAP_ASSISTANT_API_KEY") or env.get("OPENAI_API_KEY"))

    return RuntimeConfig(
        picoclaw_home=picoclaw_home,
        config_path=config_path,
        workspace_dir=workspace_dir,
        t3mt_host=_clean(env.get("T3MT_HOST"), DEFAULT_T3MT_HOST).rstrip("/"),
        t3mt_api_key=_clean(env.get("T3MT_API_KEY")),
        automation_mode=normalize_automation_mode(_clean(env.get("T3MT_AUTOMATION_MODE"), DEFAULT_AUTOMATION_MODE)),
        model_name=model_name,
        model=model,
        model_api_key=model_api_key,
        model_api_base=_clean(env.get("T3FAP_ASSISTANT_API_BASE"), DEFAULT_MODEL_API_BASE),
        pico_token=_clean(env.get("T3FAP_ASSISTANT_PICO_TOKEN") or env.get("PICOCLAW_CHANNELS_PICO_TOKEN")),
        gateway_host=_clean(env.get("PICOCLAW_GATEWAY_HOST"), DEFAULT_GATEWAY_HOST),
        gateway_port=_int_from_env(env.get("PICOCLAW_GATEWAY_PORT"), DEFAULT_GATEWAY_PORT),
        log_level=_clean(env.get("PICOCLAW_LOG_LEVEL"), DEFAULT_LOG_LEVEL),
        confirm_redline_actions=parse_bool(
            env.get("T3MT_CONFIRM_REDLINE_ACTIONS"),
            DEFAULT_CONFIRM_REDLINE_ACTIONS,
        ),
    )


def sync_t3mt_skills(source: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for existing in target.glob("t3mt-*"):
        if existing.is_dir():
            shutil.rmtree(existing)

    if not source.exists():
        return

    for skill_dir in sorted(source.iterdir()):
        if not skill_dir.is_dir() or not skill_dir.name.startswith("t3mt-"):
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        shutil.copytree(
            skill_dir,
            target / skill_dir.name,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )


def _write_agent_bootstrap(config: RuntimeConfig) -> None:
    agent_file = config.workspace_dir / "AGENT.md"
    if agent_file.exists():
        return
    automation_line = {
        "read-only": "- Stay read-only: inspect state and explain what would change, but do not mutate application state.",
        "full-access": "- Execute most write operations automatically after reading current state first.",
    }.get(
        config.automation_mode,
        "- Execute actions covered by the T3MT whitelist policy automatically.",
    )
    redline_line = (
        "- Ask the operator before redline actions such as API key reset/export, bulk deletion, or broad settings overwrite."
        if config.confirm_redline_actions
        else "- Redline confirmations are disabled; still summarize destructive actions clearly before execution."
    )
    agent_file.write_text(
        "\n".join(
            [
                "# T3FAP AI Assistant",
                "",
                "Operate as a sidecar automation assistant for the T3MT/T3FAP application.",
                f"- Use the T3MT REST API at `{config.t3mt_host}` through the bundled skills.",
                "- Do not connect to or mutate the application database directly.",
                "- Read current application state before changing plugins, tasks, resources, drives, or settings.",
                automation_line,
                redline_line,
                "- Never reveal `T3MT_API_KEY` or model API keys in chat output.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def build_picoclaw_config_payload(config: RuntimeConfig) -> dict[str, object]:
    return {
        "agents": {
            "defaults": {
                "workspace": str(config.workspace_dir),
                "restrict_to_workspace": True,
                "model_name": config.model_name,
                "max_tokens": 8192,
                "context_window": 131072,
                "temperature": 0.2,
                "max_tool_iterations": 30,
                "summarize_message_threshold": 20,
                "summarize_token_percent": 75,
                "tool_feedback": {
                    "enabled": True,
                    "max_args_length": 500,
                    "separate_messages": False,
                },
            }
        },
        "model_list": [
            {
                "model_name": config.model_name,
                "model": config.model,
                "api_key": config.model_api_key,
                "api_base": config.model_api_base,
            }
        ],
        "channels": {
            "pico": {
                "enabled": True,
                "token": config.pico_token,
                "allow_token_query": False,
                "allow_origins": ["*"],
                "ping_interval": 30,
                "read_timeout": 60,
                "max_connections": 100,
                "allow_from": [],
            }
        },
        "tools": {
            "filter_sensitive_data": True,
            "filter_min_length": 8,
            "web": {
                "enabled": True,
                "prefer_native": True,
                "provider": "auto",
                "format": "plaintext",
                "fetch_limit_bytes": 10485760,
                "sogou": {"enabled": True, "max_results": 5},
                "duckduckgo": {"enabled": False, "max_results": 5},
                "tavily": {"enabled": False, "max_results": 5},
                "brave": {"enabled": False, "max_results": 5},
                "private_host_whitelist": ["t3fap", "localhost", "127.0.0.1"],
            },
            "cron": {"enabled": True, "exec_timeout_minutes": 5, "allow_command": True},
            "exec": {
                "enabled": True,
                "enable_deny_patterns": True,
                "allow_remote": True,
                "timeout_seconds": 120,
                "custom_allow_patterns": [
                    r"\bpython3?\s+.*skills/t3mt-[^ ]+/scripts/t3mt-[^ ]+\.py\b",
                    r"\bpython3?\s+.*runtime/t3fap_assistant_runtime\.py\b",
                ],
            },
            "skills": {
                "enabled": True,
                "registries": {
                    "clawhub": {"enabled": False, "base_url": "https://clawhub.ai"},
                    "github": {"enabled": False, "base_url": "https://github.com"},
                },
                "max_concurrent_searches": 2,
                "search_cache": {"max_size": 50, "ttl_seconds": 300},
            },
            "append_file": {"enabled": True},
            "edit_file": {"enabled": True},
            "find_skills": {"enabled": True},
            "install_skill": {"enabled": False},
            "list_dir": {"enabled": True},
            "message": {"enabled": True},
            "read_file": {"enabled": True, "mode": "bytes", "max_read_file_size": 65536},
            "spawn": {"enabled": True},
            "subagent": {"enabled": True},
            "web_fetch": {"enabled": True},
            "write_file": {"enabled": True},
        },
        "heartbeat": {"enabled": True, "interval": 30},
        "devices": {"enabled": False, "monitor_usb": False},
        "hooks": {
            "enabled": True,
            "defaults": {
                "observer_timeout_ms": 500,
                "interceptor_timeout_ms": 5000,
                "approval_timeout_ms": 60000,
            },
        },
        "gateway": {
            "host": config.gateway_host,
            "port": config.gateway_port,
            "hot_reload": False,
            "log_level": config.log_level,
        },
    }


def prepare_runtime(config: RuntimeConfig, bundled_skills_dir: Path) -> None:
    config.picoclaw_home.mkdir(parents=True, exist_ok=True)
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    config.workspace_dir.mkdir(parents=True, exist_ok=True)
    sync_t3mt_skills(bundled_skills_dir, config.workspace_dir / "skills")
    _write_agent_bootstrap(config)
    config.config_path.write_text(
        json.dumps(build_picoclaw_config_payload(config), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    try:
        config.config_path.chmod(0o600)
    except OSError:
        pass


def build_child_environment(
    config: RuntimeConfig,
    base_env: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    child_env = dict(base_env if base_env is not None else os.environ)
    child_env["PICOCLAW_HOME"] = config.picoclaw_home.as_posix()
    child_env["PICOCLAW_CONFIG"] = config.config_path.as_posix()
    child_env["T3MT_HOST"] = config.t3mt_host
    child_env["T3MT_API_KEY"] = config.t3mt_api_key
    child_env["T3MT_AUTOMATION_MODE"] = config.automation_mode
    child_env["T3MT_CONFIRM_REDLINE_ACTIONS"] = "true" if config.confirm_redline_actions else "false"
    child_env["T3FAP_ASSISTANT_MODEL_NAME"] = config.model_name
    child_env["T3FAP_ASSISTANT_MODEL"] = config.model
    child_env["T3FAP_ASSISTANT_API_BASE"] = config.model_api_base
    if config.model_api_key:
        child_env["T3FAP_ASSISTANT_API_KEY"] = config.model_api_key
    if config.pico_token:
        child_env["T3FAP_ASSISTANT_PICO_TOKEN"] = config.pico_token
    return child_env


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    config = build_runtime_config(os.environ)
    prepare_runtime(config, bundled_skills_dir=_repo_root() / "skills")
    child_env = build_child_environment(config)

    if args == ["print-config"]:
        print(config.config_path)
        return 0

    command = args or ["picoclaw-launcher", "-console", "-public", "-no-browser"]
    if os.name == "posix":
        os.execvpe(command[0], command, child_env)
        return 127

    completed = subprocess.run(command, env=child_env, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
