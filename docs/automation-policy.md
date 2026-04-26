# Automation Policy

The assistant runs as a T3MT/T3FAP sidecar and must use the public REST API only.

## Default Mode

`T3MT_AUTOMATION_MODE=whitelist`

Whitelisted actions may run automatically after the assistant has read the current state.

## Whitelisted Actions

- Read account/API-key metadata.
- List and inspect plugins, tasks, resources, drives, and monitor data.
- Install known bundled plugins.
- Enable or disable plugins.
- Create tasks from clear user intent.
- Run a named task.
- Query catalog and search providers.
- Read settings and task template settings.

## Confirmation Required

The assistant must ask the operator before:

- Deleting tasks or resources.
- Uninstalling plugins.
- Resetting, rotating, exporting, or printing API keys.
- Overwriting broad settings.
- Running bulk changes.
- Executing commands outside bundled `t3mt-*` tools.
- Performing any action that can remove user data, credentials, media, or account bindings.

## Secret Handling

Never print real values for `T3MT_API_KEY`, model API keys, cookies, tokens, or reset secrets. Use `<redacted>` in logs and summaries.
