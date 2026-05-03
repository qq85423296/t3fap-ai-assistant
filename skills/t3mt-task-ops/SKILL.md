---
name: t3mt-task-ops
description: Use this skill to inspect task templates, create and update tasks, run or terminate executions, and manage subscription, transfer, download, and STRM task flows in T3MT/T3FAP.
---

# T3MT Task Ops

Use this skill for `task.transfer`, `task.drive_download`, `task.video_download`, `task.strm`, and related task templates.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Use this skill for

- Listing task templates, tasks, and execution state.
- Creating tasks from explicit payloads or drafts returned by resource actions.
- Running, retrying, toggling, terminating, and inspecting single-task flows.
- Managing subscription, transfer, download, and STRM task operations once the desired task is known.

## Do not use this skill when

- The user still needs to discover the right resource or action target first. Use `t3mt-resource-ops`.
- The request is a high-level multi-step flow from search to task creation. Use `t3mt-workflow-ops`.
- The user only wants plugin lifecycle or plugin config inspection. Use `t3mt-plugin-ops`.

## Common commands

```bash
python scripts/t3mt-task-ops.py templates
python scripts/t3mt-task-ops.py tasks
python scripts/t3mt-task-ops.py create body_json='{"plugin_id":"task.transfer","template_key":"quark_transfer"}'
python scripts/t3mt-task-ops.py run task_id=<TASK_ID> wait_for_completion=true
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py task-templates
python ../t3mt-cli/scripts/t3mt-cli.py tasks
python ../t3mt-cli/scripts/t3mt-cli.py create-task body_json='{"plugin_id":"task.strm","template_key":"default"}'
python ../t3mt-cli/scripts/t3mt-cli.py terminate-execution execution_id=<EXECUTION_ID>
```

## Guidance

- Prefer task drafts returned from resource actions over hand-building complex `input_payload`.
- In `full-access`, create, update, run, retry, toggle, and single-task delete may run automatically.
- Ask before bulk deletion, broad settings overwrites, or destructive multi-task rewrites.
