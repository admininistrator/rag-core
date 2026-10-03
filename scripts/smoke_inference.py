"""Real HTTP/process/resource smoke, using only synthetic EN/VI text."""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from contextlib import suppress

import httpx
import psutil  # type: ignore[import-untyped]

from rag_core.adapters.models.http import HttpModelInference
from rag_core.domain.models import InferenceError, InferenceRequest


async def smoke(url: str, process: subprocess.Popen[bytes] | None) -> None:
    peak = 0
    stop = asyncio.Event()

    async def monitor() -> None:
        nonlocal peak
        while not stop.is_set():
            if process is not None:
                try:
                    owner = psutil.Process(process.pid)
                    peak = max(peak, sum(p.memory_info().rss for p in [owner, *owner.children(recursive=True)]))
                except psutil.Error:
                    pass
            await asyncio.sleep(0.05)

    watcher = asyncio.create_task(monitor())
    started = time.monotonic()
    try:
        async with httpx.AsyncClient(base_url=url, trust_env=False) as client:
            for _ in range(1200):
                if process is not None and process.poll() is not None:
                    raise RuntimeError("inference_process_exited")
                try:
                    response = await client.get("/health/ready", timeout=2)
                    response.raise_for_status()
                    ready = response.json()
                    break
                except httpx.HTTPError:
                    await asyncio.sleep(0.25)
            else:
                raise RuntimeError("inference_startup_timeout")
            print("READY", json.dumps(ready, sort_keys=True), flush=True)
            model = HttpModelInference(client, ready["fingerprint"])
            for operation in ("embed", "rerank"):
                begin = time.monotonic()
                request = InferenceRequest(operation=operation,
                    texts=["Hà Nội là thủ đô của Việt Nam.", "Cá sống ở đại dương."],
                    query="What is the capital of Vietnam?" if operation == "rerank" else None)
                result = await model.infer(request)
                assert len(result.embeddings if operation == "embed" else result.scores) == 2
                if operation == "rerank":
                    assert result.scores[0] > result.scores[1]
                print(f"HTTP {operation} latency_seconds={time.monotonic()-begin:.3f}", flush=True)
            # Multiple API client instances all use this single remote process/model pair.
            async def other_client():
                async with httpx.AsyncClient(base_url=url, trust_env=False) as other:
                    result = await HttpModelInference(other, ready["fingerprint"]).infer(
                        InferenceRequest(operation="embed", texts=["Thủ đô Việt Nam là Hà Nội."]))
                    assert len(result.embeddings) == 1
                    state = (await other.get("/health/ready")).json()
                    assert state["pid"] == ready["pid"]
                    return state["pid"]
            print("FOUR_CLIENT_SHARED_PID", await asyncio.gather(*(other_client() for _ in range(4))), flush=True)
            cancel_task = asyncio.create_task(model.infer(InferenceRequest(
                operation="embed", texts=["Hà Nội là thủ đô Việt Nam."]*32)))
            await asyncio.sleep(0.05)
            cancel_task.cancel()
            with suppress(asyncio.CancelledError):
                await cancel_task
            await model.infer(InferenceRequest(operation="embed", texts=["Hello Việt Nam."]))
            try:
                await model.infer(InferenceRequest(operation="embed", texts=["hello "*1000]))
                raise AssertionError("overlimit_was_accepted")
            except InferenceError as exc:
                assert exc.code == "model_token_limit"
            # Error validation must never echo caller text.
            response = await client.post("/internal/infer/00000000-0000-0000-0000-000000000001",
                                         json={"operation":"embed", "texts":["PRIVATE"], "user_id":"PRIVATE"})
            assert response.status_code == 422 and "PRIVATE" not in response.text
            assert (await client.post("/internal/infer/00000000-0000-0000-0000-000000000001",
                                      content=b"x"*(1024*1024+1))).status_code == 413
            final = (await client.get("/health/ready")).json()
            assert final["active_jobs"] == 0 and final["pid"] == ready["pid"]
            if ready["device"] != "cpu":
                import torch
                usage = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], text=True).strip()
                print("GPU_VRAM_USED_MIB", usage, "CUDA", torch.version.cuda, flush=True)
                assert int(usage.splitlines()[0]) <= 7168
                assert final["resources"]["vram_peak_reserved_bytes"] <= 7*1024**3
            print("FINAL_RESOURCES", json.dumps(final["resources"], sort_keys=True), flush=True)
            print(f"SMOKE PASS elapsed_seconds={time.monotonic()-started:.3f} "
                  f"peak_process_tree_rss_bytes={peak} final_rss_bytes={final['rss_bytes']}", flush=True)
    finally:
        stop.set()
        await watcher


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8080")
    parser.add_argument("--spawn", action="store_true")
    args = parser.parse_args()
    process = None
    if args.spawn:
        process = subprocess.Popen([sys.executable, "-m", "rag_core.inference"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   env=os.environ.copy())
    try:
        asyncio.run(smoke(args.url, process))
    finally:
        if process is not None:
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    main()
