#!/usr/bin/env python3
import os
from datetime import datetime, timezone

import psycopg


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, default).strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def main() -> None:
    db_url = env("AGENTS_DATABASE_URL")
    task_name = os.getenv("AGENT_TASK_NAME", "nightly-maintenance").strip() or "nightly-maintenance"
    cleanup_days = int(os.getenv("AGENT_CLEANUP_DAYS", "30"))

    now = datetime.now(timezone.utc)
    print(f"[{now.isoformat()}] starting task={task_name}")

    with psycopg.connect(db_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            # 1) Schema bootstrap
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_runs (
                    id BIGSERIAL PRIMARY KEY,
                    task_name TEXT NOT NULL,
                    run_status TEXT NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_heartbeats (
                    task_name TEXT PRIMARY KEY,
                    last_success_at TIMESTAMPTZ NOT NULL,
                    run_count BIGINT NOT NULL DEFAULT 0,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )

            # 2) Business write: log current run
            cur.execute(
                """
                INSERT INTO agent_runs (task_name, run_status, payload)
                VALUES (%s, %s, %s::jsonb)
                """,
                (task_name, "success", '{"source":"bifrost-cron","op":"db-maintenance"}'),
            )

            # 3) Upsert heartbeat
            cur.execute(
                """
                INSERT INTO agent_heartbeats (task_name, last_success_at, run_count, updated_at)
                VALUES (%s, NOW(), 1, NOW())
                ON CONFLICT (task_name)
                DO UPDATE SET
                    last_success_at = EXCLUDED.last_success_at,
                    run_count = agent_heartbeats.run_count + 1,
                    updated_at = NOW();
                """,
                (task_name,),
            )

            # 4) Cleanup old records
            cur.execute(
                """
                DELETE FROM agent_runs
                WHERE created_at < NOW() - (%s::text || ' days')::interval;
                """,
                (cleanup_days,),
            )
            deleted_rows = cur.rowcount

            # 5) Read current totals for logs
            cur.execute("SELECT COUNT(*) FROM agent_runs WHERE task_name = %s", (task_name,))
            total_runs = cur.fetchone()[0]

        conn.commit()

    print(
        f"[{datetime.now(timezone.utc).isoformat()}] done task={task_name} "
        f"deleted_old_rows={deleted_rows} total_runs={total_runs}"
    )


if __name__ == "__main__":
    main()
