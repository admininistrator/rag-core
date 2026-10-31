"""T33 Local resource budget and concurrency load driver integration tests.

Verifies:
- Query admission concurrency budget and waiter queue limits.
- Load test harness execution under multi-user concurrency.
- Zero cross-session evidence leakage under active concurrent load.
- Resource telemetry sampling and budget verification.
"""

import asyncio
from pathlib import Path

import pytest

from rag_core.application.admission import QueryAdmission, QueryBusy
from scripts.load_test import (
    LoadTestHarness,
    get_system_info,
    sample_docker_memory,
)

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


async def test_query_admission_concurrency_and_waiter_bounds() -> None:
    """Verifies that QueryAdmission respects concurrency budget and rejects when queue is full."""
    admission = QueryAdmission(concurrency=2, queue_size=2, timeout=0.1)

    # 1. Acquire two active slots
    l1 = await admission.acquire()
    l2 = await admission.acquire()
    assert admission.active == 2
    assert admission.waiting == 0

    # 2. Third and fourth requests wait in queue
    waiter1 = asyncio.create_task(admission.acquire())
    waiter2 = asyncio.create_task(admission.acquire())
    await asyncio.sleep(0.01)
    assert admission.waiting == 2

    # 3. Fifth request exceeds queue_size and immediately raises QueryBusy (429)
    with pytest.raises(QueryBusy):
        await admission.acquire()

    # 4. Release active slot: waiter1 is immediately admitted
    l1.release()
    l3 = await waiter1
    assert admission.active == 2
    assert admission.waiting == 1

    # 5. Release second active slot: waiter2 is admitted
    l2.release()
    l4 = await waiter2
    assert admission.active == 2
    assert admission.waiting == 0

    # 6. Release all leases: active drops to 0
    l3.release()
    l4.release()
    assert admission.active == 0


async def test_system_info_and_docker_telemetry() -> None:
    """Verifies host environment telemetry and Docker memory sampling."""
    info = get_system_info()
    assert "os" in info and "Darwin" in info["os"]
    assert "cpu" in info
    assert "docker" in info

    mem = sample_docker_memory()
    # If containers are running, memory is positive; otherwise zero float
    assert isinstance(mem, float) and mem >= 0.0


async def test_load_harness_multi_user_concurrency_and_isolation(tmp_path: Path) -> None:
    """Verifies LoadTestHarness with 3 virtual users, checking zero cross-session leakage and slot release."""
    out_json = tmp_path / "load_test_quick.json"
    harness = LoadTestHarness(
        users=3,
        duration=3.0,
        requests_cap=3,
        mode="stub",
        provider="deepseek",
        concurrency=10,
        queue_size=10,
        simulated_latency=0.01,
        background_ingestion=True,
        output_file=out_json,
    )
    summary = await harness.run()

    assert summary.overall_pass is True
    assert summary.total_offered >= 3
    assert summary.successful_200 >= 3
    assert summary.errors_5xx == 0
    assert summary.rejected_429 == 0
    assert summary.admission_rate >= 0.95
    assert summary.accepted_success_rate >= 0.99
    assert summary.terminal_outcomes_100_percent is True
    assert summary.zero_cross_session_leakage is True
    assert summary.zero_admission_slot_leakage is True
    assert summary.zero_unbounded_queue is True
    assert summary.zero_oom_process_crash is True
    assert summary.docker_ram_budget_pass is True
    assert summary.vram_budget_pass is True
    assert out_json.is_file()
