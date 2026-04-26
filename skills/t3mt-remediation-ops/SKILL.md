---
name: t3mt-remediation-ops
description: Use this skill to analyze recent T3MT/T3FAP failures, propose recovery actions, and execute focused remediations for unhealthy plugins, failed tasks, and blocked automations.
---

# T3MT Remediation Ops

Use this skill when the user wants the assistant to diagnose failures and move toward recovery instead of only reporting monitor data.

## Common commands

```bash
python scripts/t3mt-remediation-ops.py analyze limit=20
python scripts/t3mt-remediation-ops.py plugin-recover plugin_id=task.transfer
python scripts/t3mt-remediation-ops.py task-recover task_id=task-demo auto_run=true
python scripts/t3mt-remediation-ops.py execution-recover execution_id=exec-demo auto_run=true
```

## What it does

- Reads plugin health and recent executions.
- Produces prioritized recovery candidates with suggested commands.
- Can re-enable a plugin, re-run a task, or recover from a failed execution.
- Keeps recovery focused on one plugin or one task at a time.

## Guidance

- Use `analyze` first when the failure source is still unclear.
- Prefer `plugin-recover` for disabled or unhealthy plugins.
- Prefer `execution-recover` when you have a specific failed execution and want the assistant to trace it back to the owning task.
- In `full-access`, single-target recovery actions may run automatically after the current state is read.
