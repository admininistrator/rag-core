"""Run the transactional outbox publisher without loading parsers or models."""

import argparse
import asyncio
import os
import sys

from rag_core.adapters.broker.celery import CeleryJobPublisher
from rag_core.adapters.persistence.database import build_engine, database_url_from_env
from rag_core.adapters.persistence.registrations import OutboxDispatcher


async def _run(*, once: bool, interval: float) -> int:
    broker_url = os.environ.get("REDIS_URL", "")
    if not broker_url:
        raise ValueError("REDIS_URL is required")
    engine = build_engine(database_url_from_env())
    dispatcher = OutboxDispatcher(engine, CeleryJobPublisher(broker_url))
    try:
        while True:
            try:
                dispatched = await dispatcher.dispatch_one()
            except Exception:
                # No exception text: broker/DB exceptions can contain credentials.
                print("Outbox dispatch unavailable; event remains pending", file=sys.stderr)
                if once:
                    return 1
                await asyncio.sleep(interval)
                continue
            if once:
                return 0
            if not dispatched:
                await asyncio.sleep(interval)
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish committed ingestion outbox events")
    parser.add_argument("--once", action="store_true", help="Dispatch at most one event")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if not 0.1 <= args.interval <= 60:
        parser.error("interval must be between 0.1 and 60 seconds")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        return asyncio.run(_run(once=args.once, interval=args.interval))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
