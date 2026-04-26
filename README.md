# T3FAP AI Assistant

T3FAP AI Assistant is a custom sidecar image that bundles PicoClaw with T3MT/T3FAP project skills.

It is designed to run next to the T3FAP app in Docker and operate the app through REST APIs only.

## What Is Included

- PicoClaw gateway + launcher binary, built during the Docker image build.
- Runtime bootstrap in `runtime/t3fap_assistant_runtime.py`.
- Bundled skills:
  - `t3mt-api`
  - `t3mt-cli`
  - `t3mt-command-dispatch`
  - `t3mt-sidecar-automation`
  - `t3mt-plugin-ops`
  - `t3mt-drive-ops`
  - `t3mt-resource-ops`
  - `t3mt-task-ops`
  - `t3mt-workflow-ops`
  - `t3mt-monitor-ops`
  - `t3mt-settings-ops`
  - `t3mt-generic-plugin-adapter`
- Default sidecar API target: `http://t3fap:8521`.
- Default automation mode: `full-access`.

## Runtime Behavior

On container start, the runtime:

1. Generates `/data/picoclaw/config.json`.
2. Creates `/data/picoclaw/workspace`.
3. Copies bundled `t3mt-*` skills into the PicoClaw workspace.
4. Writes a default `AGENT.md` if one does not already exist.
5. Starts `picoclaw-launcher -console -public -no-browser`.

The assistant uses `T3MT_API_KEY` as `X-API-Key` and never needs direct database access.

## Required Settings

Edit the compose file directly and fill:

```bash
T3MT_API_KEY=<key from T3FAP API key UI>
OPENAI_API_KEY=<model key>
```

Optional values you can change in compose:

```bash
T3MT_HOST=http://t3fap:8521
T3MT_AUTOMATION_MODE=full-access|whitelist|read-only
T3MT_CONFIRM_REDLINE_ACTIONS=true
T3FAP_ASSISTANT_MODEL_NAME=gpt-5.4
T3FAP_ASSISTANT_MODEL=openai/gpt-5.4
T3FAP_ASSISTANT_API_BASE=https://api.openai.com/v1
T3FAP_ASSISTANT_PICO_TOKEN=<optional pico channel token>
```

## Local Verification

```bash
python -m unittest discover -s tests
python -m py_compile runtime/t3fap_assistant_runtime.py skills/t3mt-api/scripts/t3mt-api.py skills/t3mt-cli/scripts/t3mt-cli.py
```

Validate skills:

```bash
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-api
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-cli
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-command-dispatch
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-sidecar-automation
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-plugin-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-drive-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-resource-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-task-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-workflow-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-monitor-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-settings-ops
python C:/Users/Administrator/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/t3mt-generic-plugin-adapter
```

## Build

```bash
docker build -t t3fap-ai-assistant:local .
```

To pin PicoClaw:

```bash
docker build --build-arg PICOCLAW_REF=<tag-or-commit> -t t3fap-ai-assistant:local .
```

## Remote Image Build

This repo includes `.github/workflows/docker-image.yml`.

- Pull requests build the image without pushing.
- Pushes to `main` publish `ghcr.io/<owner>/<repo>:main`, `:sha-<commit>`, and `:latest`.
- Version tags like `v0.1.0` publish the matching tag.
- Manual workflow runs can override `PICOCLAW_REF`.

First push:

```bash
git init
git add .
git commit -m "Initial T3FAP AI assistant image"
git branch -M main
git remote add origin <REMOTE_URL>
git push -u origin main
```

## Compose Example

```bash
docker compose -f compose.example.yaml up --build
```

The compose file exposes the PicoClaw web console on `18800` and the gateway on `18790`.

## Automation Policy

Whitelisted actions run automatically:

- Read auth/account metadata.
- List and inspect plugins, tasks, resources, drives, and monitor data.
- Install known bundled plugins.
- Enable or disable plugins.
- Create tasks from clear user intent.
- Run a named task.
- Query resource catalog/search providers.

`full-access` additionally allows:

- Installing and enabling missing plugins automatically.
- Updating targeted plugin config values.
- Creating or updating drive accounts and refreshing them.
- Creating, updating, toggling, running, and deleting one clearly targeted task.
- Turning resource actions into task drafts and creating tasks from them.
- Running built-in workflows such as search -> transfer/download/STRM.
- Reading monitor dashboard, executions, schedules, plugin health, and realtime system metrics.
- Updating task template center settings with a precise payload.

The assistant asks before destructive or sensitive actions:

- Delete tasks/resources.
- Uninstall plugins.
- Reset or expose API keys.
- Overwrite broad settings.
- Run bulk changes.
- Execute commands outside the bundled `t3mt-*` tools.

## Phase 1 Skills

The first expanded skill pack focuses on plugins, drives, resources, tasks, and workflows:

- `t3mt-plugin-ops`: inspect, classify, install, enable, disable, and configure plugins.
- `t3mt-drive-ops`: manage cloud providers, accounts, scan login, files, folders, shares, and download links.
- `t3mt-resource-ops`: query search/catalog providers, inspect resources, and trigger task-oriented actions.
- `t3mt-task-ops`: create, update, run, terminate, and subscribe task flows.
- `t3mt-workflow-ops`: execute high-level flows such as search -> transfer, search -> download, and search -> STRM.

## Phase 2 Skills

- `t3mt-monitor-ops`: inspect dashboard, execution history, schedules, plugin health, and realtime host metrics.
- `t3mt-settings-ops`: read and update task template center settings with precise JSON payloads.

## Phase 3 Skills

- `t3mt-generic-plugin-adapter`: inspect unknown plugins, infer roles and provider types, pull related contracts or templates, and produce an executable adaptation profile.
