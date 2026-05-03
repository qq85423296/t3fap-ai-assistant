---
name: t3mt-api
description: Use this skill when Codex needs raw T3MT/T3FAP REST API access from the sidecar assistant with an API key, especially for endpoints or payloads not cleanly covered by the higher-level CLI and domain skills. Covers plugin, resource, task, drive, monitor, media, settings, and account endpoints.
---

# T3MT REST API

Use `scripts/t3mt-api.py` to call T3MT/T3FAP HTTP endpoints from the assistant sidecar.

## Positioning

- Prefer `t3mt-cli` for common day-to-day operations.
- Prefer domain skills such as `t3mt-plugin-ops`, `t3mt-resource-ops`, `t3mt-task-ops`, and `t3mt-workflow-ops` when they fit.
- Use `t3mt-api` when:
  - an endpoint is not exposed cleanly through `t3mt-cli`
  - a domain skill does not cover the target operation
  - you need exact HTTP control over method, path, or JSON payload
- Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Setup

The Docker image passes these values into the assistant runtime:

```bash
export T3MT_HOST=http://t3fap:8521
export T3MT_API_KEY=<T3MT_API_KEY>
```

You can also configure them explicitly:

```bash
python scripts/t3mt-api.py configure --host http://t3fap:8521 --apikey <T3MT_API_KEY>
```

The script sends the key as `X-API-Key` and stores local config at `~/.config/t3mt_api/config` when configured manually.

## Syntax

```bash
python scripts/t3mt-api.py <METHOD> <PATH> [key=value ...] [--json '<body>']
```

All paths include the `/api` prefix.

## Core Endpoints

| Area | Examples |
| --- | --- |
| Auth | `GET /api/auth/me`, `GET /api/auth/api-key` |
| Plugins | `GET /api/plugins`, `POST /api/plugins/install`, `POST /api/plugins/{plugin_id}/enable`, `POST /api/plugins/{plugin_id}/disable` |
| Resources | `GET /api/resources/catalog/sources`, `POST /api/resources/catalog/query`, `POST /api/resources/search/query`, `GET /api/resources/{resource_id}` |
| Tasks | `GET /api/tasks/templates`, `GET /api/tasks`, `POST /api/tasks`, `POST /api/tasks/{task_id}/run`, `PUT /api/tasks/{task_id}`, `DELETE /api/tasks/{task_id}` |
| Drive | `GET /api/drive/providers`, `GET /api/drive/accounts`, `POST /api/drive/providers/{plugin_id}/accounts`, `GET /api/drive/accounts/{account_id}/files` |
| Monitor | `GET /api/monitor/overview`, `GET /api/monitor/dashboard`, `GET /api/monitor/schedules`, `GET /api/monitor/executions` |
| Settings | `GET /api/settings/task-templates`, `PUT /api/settings/task-templates` |
| Media | `GET /api/media/providers`, `POST /api/media/resolve` |

## Examples

```bash
python scripts/t3mt-api.py GET /api/plugins
python scripts/t3mt-api.py GET /api/tasks
python scripts/t3mt-api.py POST /api/tasks/example-task/run --json '{"wait_for_completion":true}'
python scripts/t3mt-api.py POST /api/resources/search/query --json '{"plugin_id":"search.pansou","keyword":"test","filters":{},"limit":10}'
```

## Operating Rules

- Read current state before mutating plugins, tasks, drives, resources, or settings.
- Prefer raw API calls only when they materially improve precision or coverage over `t3mt-cli`.
- Never print a real API key in chat output.
