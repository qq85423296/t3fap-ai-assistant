---
name: t3mt-drive-ops
description: Use this skill to manage drive providers, accounts, scan login flows, files, shares, and transfer/download prerequisites across T3MT/T3FAP cloud plugins.
---

# T3MT Drive Ops

Use this skill for `drive.115`, `drive.139yun`, `drive.cloud189`, `drive.quark`, `drive.quark_tv`, and compatible third-party drive plugins.

Follow `t3mt-sidecar-automation` for mutation, confirmation, audit, and secret-handling rules.

## Use this skill for

- Listing drive providers and account inventory.
- Inspecting provider contracts, account forms, and account state before mutations.
- Creating, refreshing, and setting main accounts when the user intent is clear.
- Browsing files, folder structure, and share-save prerequisites.

## Do not use this skill when

- The user only needs plugin lifecycle or plugin config work. Use `t3mt-plugin-ops`.
- The user is primarily working with resource query/action flows. Use `t3mt-resource-ops`.
- The user wants an end-to-end search-to-task orchestration. Use `t3mt-workflow-ops`.

## Common commands

```bash
python scripts/t3mt-drive-ops.py providers
python scripts/t3mt-drive-ops.py accounts
python scripts/t3mt-drive-ops.py files account_id=<ACCOUNT_ID> parent_id=0
python scripts/t3mt-drive-ops.py refresh account_id=<ACCOUNT_ID>
python scripts/t3mt-drive-ops.py create-account plugin_id=drive.quark payload_json='{"cookie":"..."}'
```

## Raw fallbacks

```bash
python ../t3mt-cli/scripts/t3mt-cli.py drive-providers
python ../t3mt-cli/scripts/t3mt-cli.py drive-provider plugin_id=drive.115
python ../t3mt-cli/scripts/t3mt-cli.py drive-accounts
python ../t3mt-cli/scripts/t3mt-cli.py drive-files account_id=<ACCOUNT_ID> parent_id=0
python ../t3mt-cli/scripts/t3mt-cli.py refresh-drive-account account_id=<ACCOUNT_ID>
```

## Guidance

- Read provider schema or account form before creating or updating accounts.
- Prefer inspecting the provider contract before attempting third-party drive writes.
- In `full-access`, account creation, refresh, set-main, folder creation, and share-save flows may run automatically.
- Ask before deleting accounts, deleting many files, or overwriting account secrets at scale.
