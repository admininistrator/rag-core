"""One process-local query budget with bounded waiters and cancellation-safe leases."""

import asyncio


class QueryBusy(Exception):
    pass


class QueryLease:
    def __init__(self, admission: "QueryAdmission") -> None:
        self._admission = admission
        self._released = False

    def release(self) -> None:
        if not self._released:
            self._released = True
            self._admission.active -= 1
            self._admission._semaphore.release()


class QueryAdmission:
    def __init__(self, concurrency: int, queue_size: int, timeout: float) -> None:
        if not 1 <= concurrency <= 20 or not 0 <= queue_size <= 20 or not 0 < timeout <= 30:
            raise ValueError("invalid_query_admission")
        self._semaphore = asyncio.Semaphore(concurrency)
        self._queue_size = queue_size
        self._timeout = timeout
        self.active = 0
        self.waiting = 0

    async def acquire(self) -> QueryLease:
        if not self._semaphore.locked():
            await self._semaphore.acquire()
            self.active += 1
            return QueryLease(self)
        if self.waiting >= self._queue_size:
            raise QueryBusy
        self.waiting += 1
        try:
            try:
                async with asyncio.timeout(self._timeout):
                    await self._semaphore.acquire()
            except TimeoutError:
                raise QueryBusy from None
        finally:
            self.waiting -= 1
        self.active += 1
        return QueryLease(self)
