---
name: t3mt-generic-plugin-adapter
description: Use this skill to inspect unknown or third-party T3MT/T3FAP plugins, infer their roles and capabilities, read related provider contracts or task templates, and produce an executable adaptation profile.
---

# T3MT Generic Plugin Adapter

Use this skill when the plugin is not explicitly covered by the domain skills or when you need to understand a third-party plugin before mutating it.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Common commands

```bash
python scripts/t3mt-generic-plugin-adapter.py adapt plugin_id=drive.123pan
python scripts/t3mt-generic-plugin-adapter.py adapt plugin_id=task.short_video
python scripts/t3mt-generic-plugin-adapter.py adapt plugin_id=search.live.remote
python scripts/t3mt-generic-plugin-adapter.py playbook plugin_id=drive.123pan
```

## What it does

- Reads plugin detail, health, and config snapshot.
- Infers roles from `category`, `provider_types`, and `capabilities`.
- Pulls provider-specific metadata:
  - drive provider contract and account form
  - task templates for matching plugin_id
  - matching catalog/search source entry
- Produces an adaptation profile with:
  - inferred role
  - supported actions
  - config redlines
  - exact follow-up command shortlist
  - likely follow-up domain skill
  - execution playbook for next-step automation

## Guidance

- Use this before mutating a third-party plugin you have not seen before.
- If the plugin exposes task or drive capability, read its provider contract before trying writes.
- If the plugin looks resource-oriented, inspect matching sources and prefer resource actions over handcrafted payloads.
- After producing the adaptation profile, hand off to the most specific domain skill instead of staying in generic mode.
- Structure the final output so another agent can directly continue:
  - `Role`
  - `Supported Actions`
  - `Config Redlines`
  - `Command Shortlist`
  - `Next Skill`
  - `Playbook`
