---
name: t3mt-workflow-ops
description: Use this skill to execute high-level T3MT/T3FAP workflows such as ensuring core plugins, turning search results into transfer or download tasks, and creating STRM flows automatically.
---

# T3MT Workflow Ops

This skill is for end-to-end flows, not single API calls.

## Built-in workflows

```bash
python scripts/t3mt-workflow-ops.py ensure-core
python scripts/t3mt-workflow-ops.py search-and-transfer keyword=example search_plugin=search.pansou
python scripts/t3mt-workflow-ops.py search-and-download keyword=example catalog_plugin=catalog.tencent
python scripts/t3mt-workflow-ops.py search-and-strm keyword=example catalog_plugin=catalog.bilibili
```

## What it does

- Ensures required plugins are installed and enabled.
- Queries a resource source.
- Picks one result by index.
- Executes a task-oriented resource action.
- Creates a task from the returned draft.
- Optionally runs the task immediately.

## Guidance

- Default to `full-access` behavior when the environment mode allows it.
- Before a workflow mutation, summarize the selected plugin, resource, and target action.
- Ask only for redline actions such as bulk deletion, secret reset/export, or broad settings overwrite.
