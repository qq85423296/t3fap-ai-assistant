---
name: t3mt-command-dispatch
description: Use this skill when a user asks an AI assistant to operate a T3MT/T3FAP instance in natural language. It maps intent to t3mt-cli commands or raw t3mt-api endpoint calls under the sidecar whitelist policy.
---

# T3MT Command Dispatch

Translate natural-language management requests into T3MT CLI/API calls.

## Workflow

1. Identify the target area: plugins, resources, tasks, drives, monitor, settings, media, or auth.
2. Read current state before mutating.
3. Prefer `t3mt-cli` aliases for common operations.
4. Use `t3mt-api` or `t3mt-cli api` for endpoints not covered by aliases.
5. Follow `t3mt-sidecar-automation` for whitelist and escalation rules.

## Intent Map

| User intent | Command |
| --- | --- |
| Show plugins | `python scripts/t3mt-cli.py plugins` |
| Install plugin | `python scripts/t3mt-cli.py install-plugin source_type=bundled source_ref=<PLUGIN_ID> enable_after_install=true` |
| Enable plugin | `python scripts/t3mt-cli.py enable-plugin plugin_id=<PLUGIN_ID>` |
| Disable plugin | `python scripts/t3mt-cli.py disable-plugin plugin_id=<PLUGIN_ID>` |
| Show tasks | `python scripts/t3mt-cli.py tasks` |
| Run a task | `python scripts/t3mt-cli.py run-task task_id=<TASK_ID> wait_for_completion=true` |
| Search resources | `python scripts/t3mt-cli.py search-query plugin_id=<SEARCH_PLUGIN> keyword=<KEYWORD> limit=10` |
| Show drive accounts | `python scripts/t3mt-cli.py drive-accounts` |
| Show system status | `python scripts/t3mt-cli.py monitor` |
| Read template settings | `python scripts/t3mt-cli.py task-template-settings` |

## Raw API Patterns

```bash
python scripts/t3mt-cli.py api GET /api/auth/me
python scripts/t3mt-cli.py api GET /api/resources/catalog/sources
python scripts/t3mt-cli.py api POST /api/resources/catalog/query --json '{"plugin_id":"catalog.360","filters":{},"limit":24}'
python scripts/t3mt-cli.py api POST /api/tasks/<TASK_ID>/run --json '{"wait_for_completion":true}'
```

## Safety

- Use the T3MT/T3FAP API at `http://t3fap:8521`; do not connect to the database directly.
- Do not reveal `T3MT_API_KEY` in chat logs.
- Treat reset keys as one-time secrets.
- Ask before `DELETE`, plugin uninstall, task deletion, API key reset, or full settings overwrite.
- If a command returns 401, report that the key may be missing, reset, or copied incorrectly.
