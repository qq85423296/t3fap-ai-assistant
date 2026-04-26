---
name: t3mt-drive-ops
description: Use this skill to manage drive providers, accounts, scan login flows, files, shares, and transfer/download prerequisites across T3MT/T3FAP cloud plugins.
---

# T3MT Drive Ops

Use this skill for `drive.115`, `drive.139yun`, `drive.cloud189`, `drive.quark`, `drive.quark_tv`, and compatible third-party drive plugins.

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
- In `full-access`, account creation, refresh, set-main, folder creation, and share-save flows may run automatically.
- Ask before deleting accounts, deleting many files, or overwriting account secrets at scale.
