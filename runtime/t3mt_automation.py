#!/usr/bin/env python3
"""Automation mode helpers for the T3FAP assistant."""

from __future__ import annotations

MODE_READ_ONLY = "read-only"
MODE_WHITELIST = "whitelist"
MODE_FULL_ACCESS = "full-access"
DEFAULT_CONFIRM_REDLINE_ACTIONS = True

SUPPORTED_AUTOMATION_MODES = {
    MODE_READ_ONLY,
    MODE_WHITELIST,
    MODE_FULL_ACCESS,
}

REDLINE_ACTION_PREFIXES = (
    "api-key.generate",
    "api-key.reset",
    "auth.secret.export",
    "settings.full-overwrite",
    "settings.market-sources.update",
    "plugin.bulk-uninstall",
    "plugin.uninstall-all",
    "task.bulk-delete",
    "resource.bulk-delete",
    "drive.account.delete",
    "drive.account.bulk-delete",
    "drive.items.bulk-delete",
)


def parse_bool(value: str | None, default: bool = False) -> bool:
    raw = str(value or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def normalize_automation_mode(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    if raw in SUPPORTED_AUTOMATION_MODES:
        return raw
    return MODE_WHITELIST


def is_read_only(mode: str) -> bool:
    return normalize_automation_mode(mode) == MODE_READ_ONLY


def is_full_access(mode: str) -> bool:
    return normalize_automation_mode(mode) == MODE_FULL_ACCESS


def is_redline_action(action_key: str, *, bulk: bool = False, destructive: bool = False) -> bool:
    normalized = str(action_key or "").strip().lower()
    if not normalized:
        return bulk or destructive
    if bulk or destructive and any(
        token in normalized
        for token in ("delete", "reset", "export", "overwrite", "unbind", "uninstall")
    ):
        return True
    return normalized.startswith(REDLINE_ACTION_PREFIXES)


def action_requires_confirmation(
    mode: str,
    action_key: str,
    *,
    bulk: bool = False,
    destructive: bool = False,
    confirm_redline_actions: bool = DEFAULT_CONFIRM_REDLINE_ACTIONS,
) -> bool:
    normalized_mode = normalize_automation_mode(mode)
    if normalized_mode == MODE_READ_ONLY:
        return True
    if is_redline_action(action_key, bulk=bulk, destructive=destructive):
        return bool(confirm_redline_actions)
    return normalized_mode != MODE_FULL_ACCESS
