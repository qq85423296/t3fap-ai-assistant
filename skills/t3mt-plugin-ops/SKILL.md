---
name: t3mt-plugin-ops
description: Use this skill to inspect, classify, install, enable, disable, configure, and verify T3MT/T3FAP plugins, including third-party plugins, from the assistant sidecar.
---

# T3MT Plugin Ops

Operate plugins through the T3MT/T3FAP API at `http://t3fap:8521`.

## Use this skill for

- Listing installed or market plugins.
- Reading plugin health, config schema, allowed actions, and capability declarations.
- Installing missing bundled or market plugins.
- Enabling or disabling plugins automatically in `full-access` mode.
- Classifying third-party plugins into drive, task, resource, search, catalog, automation, assistant, parser, download, or media roles.

## Preferred commands

```bash
python scripts/t3mt-plugin-ops.py summary
python scripts/t3mt-plugin-ops.py inspect plugin_id=task.transfer
python scripts/t3mt-plugin-ops.py ensure plugin_id=search.pansou source_type=bundled enable_after_install=true
python scripts/t3mt-plugin-ops.py classify plugin_id=drive.115
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py plugins
python ../t3mt-cli/scripts/t3mt-cli.py plugin plugin_id=task.transfer
python ../t3mt-cli/scripts/t3mt-cli.py plugin-config plugin_id=task.transfer
python ../t3mt-cli/scripts/t3mt-cli.py update-plugin-config plugin_id=task.transfer values_json='{"default_exclude_keywords":"sample"}'
```

## Automation rules

- In `full-access`, install, enable, disable, and targeted config updates may run automatically.
- Ask before uninstalling many plugins, wiping market sources, or overwriting broad config sets.
- When a plugin is unknown, inspect its category, capabilities, dependencies, config schema, and allowed actions before mutating it.
