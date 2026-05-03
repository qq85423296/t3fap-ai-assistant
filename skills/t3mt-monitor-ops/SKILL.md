---
name: t3mt-monitor-ops
description: Use this skill to inspect T3MT/T3FAP system health, task executions, schedules, plugin health, and runtime monitoring data, then summarize failures or recovery targets.
---

# T3MT Monitor Ops

Use this skill for health checks, execution review, failure triage, and operational snapshots.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Use this skill for

- Reading dashboard, overview, schedules, executions, and plugin health.
- Summarizing recent failures before choosing a remediation path.
- Building an operational snapshot without changing platform state.

## Do not use this skill when

- The user already knows the failing plugin or task and wants recovery actions. Use `t3mt-remediation-ops`.
- The user wants to mutate tasks, plugins, resources, or drive accounts directly. Use the matching domain skill.

## Common commands

```bash
python scripts/t3mt-monitor-ops.py dashboard
python scripts/t3mt-monitor-ops.py overview
python scripts/t3mt-monitor-ops.py executions limit=20 status=failed
python scripts/t3mt-monitor-ops.py plugin-health
python scripts/t3mt-monitor-ops.py system-realtime
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py monitor
python ../t3mt-cli/scripts/t3mt-cli.py monitor-overview
python ../t3mt-cli/scripts/t3mt-cli.py monitor-executions limit=20 status=failed
python ../t3mt-cli/scripts/t3mt-cli.py monitor-plugin-health
python ../t3mt-cli/scripts/t3mt-cli.py monitor-system-realtime
```

## Guidance

- Start with `overview` or `dashboard` when the failure scope is still broad.
- Use `executions status=failed` before jumping into plugin or task mutations.
- Hand off to `t3mt-remediation-ops` when the user wants diagnosis to turn into recovery.
