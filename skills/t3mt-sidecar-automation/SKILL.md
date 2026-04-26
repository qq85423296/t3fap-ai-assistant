---
name: t3mt-sidecar-automation
description: Use this skill for T3MT/T3FAP sidecar automation policy decisions. It defines which API actions may run automatically, which actions require operator confirmation, and how the assistant should log, audit, and protect secrets.
---

# T3MT Sidecar Automation

Operate as a T3MT/T3FAP sidecar assistant. Use the project API only.

## Boundaries

- Call T3MT through `T3MT_HOST`, default `http://t3fap:8521`.
- Authenticate with `T3MT_API_KEY` through the `X-API-Key` header.
- Never read, write, or migrate the application database directly.
- Never expose API keys, model keys, cookies, tokens, or reset secrets in chat output.
- Read current state before each mutation.

## Automatic Whitelist

When `T3MT_AUTOMATION_MODE=whitelist`, execute these without asking for extra confirmation:

| Area | Allowed actions |
| --- | --- |
| Auth | Read current account and key metadata |
| Plugins | List plugins, inspect plugin details, install known bundled plugins, enable plugins, disable plugins |
| Resources | List sources, query catalog/search providers, resolve media/resources |
| Tasks | List templates, list tasks, inspect tasks, create tasks from clear user intent, run a named task |
| Drive | List providers, list accounts, inspect account files |
| Monitor | Read overview, dashboard, schedules, executions, and logs |
| Settings | Read settings and task template settings |

## Confirmation Required

Ask the operator before:

- Deleting tasks or resources.
- Uninstalling plugins.
- Resetting, rotating, printing, or exporting API keys.
- Overwriting settings with broad or ambiguous changes.
- Running bulk changes across many tasks, plugins, accounts, files, or resources.
- Executing commands outside the bundled `t3mt-*` tools.
- Any action that could remove user data, credentials, media, or external account bindings.

## Audit Style

Before a mutation, state the target object and action briefly. After the command returns, summarize:

- Endpoint or CLI command used.
- Object ID or plugin/task affected.
- Result status.
- Any follow-up needed from the operator.

Keep logs concise and redact secrets as `<redacted>`.
