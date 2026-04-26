---
name: t3mt-monitor-ops
description: Use this skill to inspect T3MT/T3FAP system health, task executions, schedules, plugin health, and runtime monitoring data, then summarize failures or recovery targets.
---

# T3MT Monitor Ops

Use this skill for health checks, execution review, failure triage, and operational snapshots.

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
