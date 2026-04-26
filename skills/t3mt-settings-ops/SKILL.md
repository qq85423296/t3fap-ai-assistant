---
name: t3mt-settings-ops
description: Use this skill to inspect and update T3MT/T3FAP task template center settings with precise JSON payloads and config diff awareness.
---

# T3MT Settings Ops

Use this skill for task template center settings and other narrowly scoped settings updates.

## Common commands

```bash
python scripts/t3mt-settings-ops.py task-template-settings
python scripts/t3mt-settings-ops.py update-task-template-settings body_json='{"common_defaults":{},"template_overrides":{}}'
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py task-template-settings
python ../t3mt-cli/scripts/t3mt-cli.py update-task-template-settings body_json='{"common_defaults":{},"template_overrides":{}}'
```
