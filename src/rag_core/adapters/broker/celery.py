"""Bounded Celery producer; the parsing task itself is introduced in T19."""

import asyncio
from uuid import UUID

from celery import Celery  # type: ignore[import-untyped]


class CeleryJobPublisher:
    def __init__(self, broker_url: str) -> None:
        if not broker_url.startswith("redis://") and not broker_url.startswith("rediss://"):
            raise ValueError("Redis broker URL required")
        self.app = Celery("rag_core_dispatcher", broker=broker_url)
        self.app.conf.update(
            task_publish_retry=False,
            broker_connection_retry_on_startup=False,
            broker_transport_options={"socket_timeout": 2, "socket_connect_timeout": 2},
        )

    async def publish(self, event_id: UUID, job_id: UUID) -> None:
        await asyncio.to_thread(
            self.app.send_task,
            "rag_core.ingest",
            args=[str(job_id)],
            task_id=str(event_id),
            queue="rag_core_ingestion",
        )
