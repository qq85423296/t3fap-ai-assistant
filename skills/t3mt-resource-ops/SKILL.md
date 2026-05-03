---
name: t3mt-resource-ops
description: Use this skill to discover catalog and search providers, query resources, inspect resource details, and trigger task-oriented resource actions for T3MT/T3FAP.
---

# T3MT Resource Ops

Use this skill for resource discovery across `search.pansou`, `search.360`, and `catalog.*` plugins.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Critical session rule

- Keep the query and follow-up action flow in the same running application session whenever possible.
- Search results and resource-action execution can depend on cached resource identifiers and in-memory runtime context.
- If you query in one session and execute an action in another, treat stale resource IDs and missing cache as a likely cause.

## Common commands

```bash
python scripts/t3mt-resource-ops.py search plugin_id=search.pansou keyword=example
python scripts/t3mt-resource-ops.py catalog plugin_id=catalog.tencent
python scripts/t3mt-resource-ops.py detail resource_id=<RESOURCE_ID>
python scripts/t3mt-resource-ops.py action resource_id=<RESOURCE_ID> action_key=task.transfer.create
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py search-sources
python ../t3mt-cli/scripts/t3mt-cli.py catalog-sources
python ../t3mt-cli/scripts/t3mt-cli.py search-query plugin_id=search.pansou keyword=test limit=10
python ../t3mt-cli/scripts/t3mt-cli.py resource resource_id=<RESOURCE_ID>
python ../t3mt-cli/scripts/t3mt-cli.py run-resource-action resource_id=<RESOURCE_ID> action_key=task.transfer.create payload_json='{}'
```

## Guidance

- Prefer query + inspect over guessing task inputs.
- Reuse resource action keys such as `task.transfer.create`, `task.video_download.create`, and `task.strm.create` whenever available.
- For search results, keep the query and action flow in the same running application session so cached resources remain executable.
