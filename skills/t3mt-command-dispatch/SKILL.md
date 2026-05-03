---
name: t3mt-command-dispatch
description: Use this skill when a user asks an AI assistant to operate a T3MT/T3FAP instance in natural language. It acts as the routing layer that maps intent to the best domain skill first, then to `t3mt-cli`, and finally to raw `t3mt-api` calls when needed.
---

# T3MT Command Dispatch

Translate natural-language management requests into T3MT CLI/API calls.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Workflow

1. Identify the target area: plugins, resources, tasks, drives, monitor, settings, media, or auth.
2. Read current state before mutating.
3. Prefer the best-fitting domain skill:
   - `t3mt-plugin-ops`
   - `t3mt-drive-ops`
   - `t3mt-resource-ops`
   - `t3mt-task-ops`
   - `t3mt-workflow-ops`
   - `t3mt-monitor-ops`
   - `t3mt-remediation-ops`
   - `t3mt-settings-ops`
   - `t3mt-generic-plugin-adapter`
4. If no domain skill fits cleanly, prefer `t3mt-cli`.
5. Use `t3mt-api` or `t3mt-cli api` only when CLI/domain coverage is incomplete or the request needs exact raw endpoint control.

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
| Ensure plugin ready | `python ../t3mt-plugin-ops/scripts/t3mt-plugin-ops.py ensure plugin_id=<PLUGIN_ID>` |
| Build search->transfer workflow | `python ../t3mt-workflow-ops/scripts/t3mt-workflow-ops.py search-and-transfer keyword=<KEYWORD> search_plugin=search.pansou` |
| Review recent failures | `python ../t3mt-monitor-ops/scripts/t3mt-monitor-ops.py executions limit=20 status=failed` |
| Analyze and recover failures | `python ../t3mt-remediation-ops/scripts/t3mt-remediation-ops.py analyze limit=20` |
| Read template center settings | `python ../t3mt-settings-ops/scripts/t3mt-settings-ops.py task-template-settings` |
| Adapt an unknown plugin | `python ../t3mt-generic-plugin-adapter/scripts/t3mt-generic-plugin-adapter.py adapt plugin_id=<PLUGIN_ID>` |
| Build a third-party plugin playbook | `python ../t3mt-generic-plugin-adapter/scripts/t3mt-generic-plugin-adapter.py playbook plugin_id=<PLUGIN_ID>` |

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
- If a command returns 401, report that the key may be missing, reset, or copied incorrectly.
