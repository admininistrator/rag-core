"""T25 shares isolated real PG fixture helpers and Windows selector I/O."""

import asyncio

from tests.integration.conftest import pg_url

__all__ = ["pg_url"]


def pytest_asyncio_loop_factories():
    return {"selector": asyncio.SelectorEventLoop}
