# T3FAP AI Assistant

T3FAP AI Assistant is a custom sidecar image that bundles PicoClaw with T3MT/T3FAP project skills.

It is designed to run next to the T3FAP app in Docker and operate the app through REST APIs only.

## What Is Included

- PicoClaw gateway binary, built during the Docker image build.
- Runtime bootstrap in `runtime/t3fap_assistant_runtime.py`.
- Bundled skills:
  - `t3mt-api`
  - `t3mt-cli`
  - `t3mt-command-dispatch`
  - `t3mt-sidecar-automation`
- Default sidecar API target: `http://t3fap:8521`.
- Default automation mode: `whitelist`.

## Runtime Behavior

On container start, the runtime:

1. Generates `/data/picoclaw/config.json`.
2. Creates `/data/picoclaw/workspace`.
3. Copies bundled `t3mt-*` skills into the PicoClaw workspace.
4. Writes a default `AGENT.md` if one does not already exist.
5. Starts `picoclaw gateway`.

The assistant uses `T3MT_API_KEY` as `X-API-Key` and never needs direct database access.

## Environment

Copy `.env.example` and fill secrets:

```bash
T3MT_API_KEY=<key from T3FAP API key UI>
OPENAI_API_KEY=<model key>
```

Useful overrides:

```bash
T3MT_HOST=http://t3fap:8521
T3MT_AUTOMATION_MODE=whitelist
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
docker compose -f compose.example.yaml --env-file .env up --build
```

The compose file exposes PicoClaw gateway on port `18790` and expects the T3FAP service to be reachable as `http://t3fap:8521`.

## Automation Policy

Whitelisted actions run automatically:

- Read auth/account metadata.
- List and inspect plugins, tasks, resources, drives, and monitor data.
- Install known bundled plugins.
- Enable or disable plugins.
- Create tasks from clear user intent.
- Run a named task.
- Query resource catalog/search providers.

The assistant asks before destructive or sensitive actions:

- Delete tasks/resources.
- Uninstall plugins.
- Reset or expose API keys.
- Overwrite broad settings.
- Run bulk changes.
- Execute commands outside the bundled `t3mt-*` tools.
