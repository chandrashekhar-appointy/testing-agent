# testing-agent cron script

This repo contains a cron-friendly DB maintenance script:

- Script: `jobs/db_maintenance.py`
- Dependencies: `requirements.txt`

## Required env vars

- `AGENTS_DATABASE_URL` (required)
  - Example: `postgresql://admin:pass@34.40.10.74:5432/agents`

## Optional env vars

- `AGENT_TASK_NAME` (default: `nightly-maintenance`)
- `AGENT_CLEANUP_DAYS` (default: `30`)

## Command for Bifrost Cron Job (GitHub source)

```bash
sh jobs/run_db_maintenance.sh
```

## Root Path guidance

- If `root_path = .`:
  - use:
    - `sh jobs/run_db_maintenance.sh`
- If you set `root_path = jobs`:
  - command becomes:
    - `sh run_db_maintenance.sh`
