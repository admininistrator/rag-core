"""One bounded Celery consumer with late acknowledgements and PG-fenced attempts."""

import asyncio
import json
import os
from uuid import UUID

from celery import Celery  # type: ignore[import-untyped]

from rag_core.workers.runtime import load_config, run_job

config = load_config()
broker_url = os.environ.get("REDIS_URL", "")
if not broker_url.startswith(("redis://", "rediss://")):
    raise ValueError("Redis broker URL required")
app = Celery("rag_core_worker", broker=broker_url)
app.conf.update(
    task_serializer="json", accept_content=["json"], task_ignore_result=True,
    task_acks_late=True, task_reject_on_worker_lost=True, worker_prefetch_multiplier=1,
    worker_concurrency=1, worker_cancel_long_running_tasks_on_connection_loss=True,
    task_soft_time_limit=3610, task_time_limit=3630,
    broker_transport_options={"visibility_timeout": 3700, "socket_timeout": 5,
                              "socket_connect_timeout": 5},
    broker_connection_retry_on_startup=True,
)


@app.task(name="rag_core.ingest")  # type: ignore[untyped-decorator]
def ingest(job_id: str) -> None:
    try:
        result = asyncio.run(run_job(UUID(job_id), config))
        print(json.dumps({"job_id": job_id, "result": result}))
    except Exception:
        # Setup/DB failures before claim remain queued; watchdog replays after five minutes.
        # After claim, an expired lease recovers. Never log exception/config/input text.
        print('{"code":"ingestion_runtime_unavailable"}')
