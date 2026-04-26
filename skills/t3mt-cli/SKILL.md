---
name: t3mt-cli
description: Use this skill to operate a T3MT/T3FAP instance through common Python CLI commands from the assistant sidecar. Covers plugins, resources, tasks, drives, monitor data, settings, and raw API fallback calls.
---

# T3MT CLI

Use `scripts/t3mt-cli.py` for common T3MT/T3FAP operations.

## Setup

The sidecar runtime passes API settings automatically:

```bash
export T3MT_HOST=http://t3fap:8521
export T3MT_API_KEY=<T3MT_API_KEY>
```

Manual configuration is also supported:

```bash
python scripts/t3mt-cli.py configure --host http://t3fap:8521 --apikey <T3MT_API_KEY>
```

## Discovery

```bash
python scripts/t3mt-cli.py list
python scripts/t3mt-cli.py show plugins
python scripts/t3mt-cli.py show api
```

Run `show <command>` before a mutation if the exact parameters are unclear.

## Common Commands

```bash
python scripts/t3mt-cli.py plugins
python scripts/t3mt-cli.py market
python scripts/t3mt-cli.py plugin plugin_id=task.strm
python scripts/t3mt-cli.py enable-plugin plugin_id=task.strm
python scripts/t3mt-cli.py disable-plugin plugin_id=task.strm

python scripts/t3mt-cli.py task-templates
python scripts/t3mt-cli.py tasks
python scripts/t3mt-cli.py task task_id=<TASK_ID>
python scripts/t3mt-cli.py run-task task_id=<TASK_ID> wait_for_completion=true

python scripts/t3mt-cli.py catalog-sources
python scripts/t3mt-cli.py search-sources
python scripts/t3mt-cli.py search-query plugin_id=search.pansou keyword=test limit=10

python scripts/t3mt-cli.py drive-providers
python scripts/t3mt-cli.py drive-accounts

python scripts/t3mt-cli.py monitor
python scripts/t3mt-cli.py monitor-schedules
python scripts/t3mt-cli.py task-template-settings
```

## Raw API Fallback

```bash
python scripts/t3mt-cli.py api GET /api/plugins
python scripts/t3mt-cli.py api PUT /api/settings/task-templates --json '{"common_defaults":{},"template_overrides":{}}'
```

## Operating Rules

- Read before writing: inspect current plugins, tasks, drive accounts, and settings before mutating.
- Use `api` for endpoints not covered by aliases.
- Execute whitelisted safe actions automatically when `T3MT_AUTOMATION_MODE=whitelist`.
- Ask before `DELETE`, plugin uninstall, task deletion, API key reset, or full settings overwrite.
- Never print a real API key in chat output; refer to it as `<T3MT_API_KEY>`.
