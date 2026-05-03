---
name: t3mt-settings-ops
description: Use this skill to inspect and update T3MT/T3FAP task template center settings with precise JSON payloads and config diff awareness.
---

# T3MT Settings Ops

Use this skill for task template center settings and other narrowly scoped settings updates.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Use this skill for

- Reading task template center settings.
- Applying precise, narrow JSON settings updates with clear intent.
- Comparing existing settings state before overwriting it.

## Do not use this skill when

- The user wants plugin config changes. Use `t3mt-plugin-ops`.
- The user wants broad workflow orchestration rather than a settings mutation. Use `t3mt-workflow-ops`.
- The payload is ambiguous or would overwrite a large settings surface without a precise diff.

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

## Guidance

- Read settings first and summarize the current shape before writing.
- Prefer minimal JSON payloads over full-document replacement.
- Ask before broad settings rewrites even in `full-access`.
