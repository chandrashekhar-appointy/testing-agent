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
pip3 install --no-cache-dir -r requirements.txt && python3 jobs/db_maintenance.py
```

## Root Path guidance

- If `root_path = .`:
  - command should include subfolder path:
    - `python3 jobs/db_maintenance.py`
- If script is inside `jobs/` and you set `root_path = jobs`:
  - command becomes:
    - `python3 db_maintenance.py`
