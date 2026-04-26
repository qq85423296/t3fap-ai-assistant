# Automation Policy

The assistant runs as a T3MT/T3FAP sidecar and must use the public REST API only.

## Modes

- `read-only`: inspect only, no mutations.
- `whitelist`: safe defaults may run automatically after reading current state.
- `full-access`: most writes may run automatically after reading current state first.

## Whitelisted Actions

- Read account/API-key metadata.
- List and inspect plugins, tasks, resources, drives, and monitor data.
- Install known bundled plugins.
- Enable or disable plugins.
- Create tasks from clear user intent.
- Run a named task.
- Query catalog and search providers.
- Read settings and task template settings.

## Full Access

In `T3MT_AUTOMATION_MODE=full-access`, the assistant may also:

- Install, enable, disable, and narrowly configure plugins.
- Create, update, toggle, run, terminate, and delete one clearly targeted task.
- Create or update drive accounts, refresh them, set the main account, and save shares.
- Execute resource actions that produce task drafts or validation results.
- Run bundled workflows such as search -> transfer/download/STRM.
- Read monitor dashboard, schedules, executions, plugin health, and system realtime metrics.
- Update task template center settings with a narrow, explicit payload.
- Inspect unknown plugins and infer safe follow-up operations before mutating them.

## Confirmation Required

The assistant must ask the operator before:

- Deleting tasks or resources.
- Uninstalling plugins.
- Resetting, rotating, exporting, or printing API keys.
- Overwriting broad settings.
- Running bulk changes.
- Executing commands outside bundled `t3mt-*` tools.
- Performing any action that can remove user data, credentials, media, or account bindings.

If `T3MT_CONFIRM_REDLINE_ACTIONS=true`, redline actions still require confirmation even in `full-access`.

## Secret Handling

Never print real values for `T3MT_API_KEY`, model API keys, cookies, tokens, or reset secrets. Use `<redacted>` in logs and summaries.
