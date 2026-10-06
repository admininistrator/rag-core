"""Independent backend CLI: app-owned S3 upload, RAG lifecycle and app-owned history."""

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from uuid import uuid4

import boto3
import httpx
from pydantic import TypeAdapter

from rag_core.contracts.sse import SSEEvent, SSESequence
from rag_core.contracts.v1 import QueryResponse


async def read_answer(client, request):
    trace, fields, data = [], {}, []
    wire_bytes = 0
    async with client.stream("POST", "/v1/query/stream", json=request) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            wire_bytes += len(line.encode()) + 1
            if wire_bytes > 2 * 1024 * 1024:
                raise RuntimeError("stream_too_large")
            if line.startswith(":"):
                continue
            if line:
                key, _, value = line.partition(":")
                value = value.removeprefix(" ")
                if key == "data":
                    data.append(value)
                elif key in {"event", "id"}:
                    fields[key] = value
                continue
            if not fields:
                continue
            event = TypeAdapter(SSEEvent).validate_python(
                {
                    "event": fields["event"],
                    "id": int(fields["id"]),
                    "data": json.loads("\n".join(data)),
                }
            )
            if trace and event.id <= trace[-1].id:
                raise RuntimeError("invalid_event_order")
            trace.append(event)
            fields, data = {}, []
            if event.event == "error":
                SSESequence.model_validate(trace)
                raise RuntimeError(event.data.error.code)
            if event.event == "done":
                SSESequence.model_validate(trace)
                return event.data
    raise RuntimeError("incomplete_stream")


async def lifecycle(
    client,
    registration,
    *,
    question="What is the capital of Vietnam?",
    followup="Nó là thủ đô của quốc gia nào?",
    on_registered=None,
):
    response = await client.post(
        "/v1/sessions", json={"external_session_id": "demo-" + uuid4().hex}
    )
    response.raise_for_status()
    session = response.json()["session_id"]
    try:
        response = await client.post(
            f"/v1/sessions/{session}/documents",
            json=registration,
            headers={"Idempotency-Key": uuid4().hex},
        )
        response.raise_for_status()
        upload = response.json()
        if on_registered:
            await on_registered(upload)
        async with asyncio.timeout(120):
            while True:
                status = await client.get("/v1/jobs/" + upload["job"]["job_id"])
                status.raise_for_status()
                job = status.json()
                if job["state"] == "ready":
                    break
                if job["state"] in {"failed", "cancelled"}:
                    raise RuntimeError("ingestion_failed")
                await asyncio.sleep(0.1)
        request = {"session_id": session, "question": question}
        response = await client.post("/v1/query", json=request)
        response.raise_for_status()
        answer = QueryResponse.model_validate(response.json())
        history = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer.answer},
        ]
        final = await read_answer(
            client, {**request, "question": followup, "history": history, "answer_language": "vi"}
        )
        return {"session": session, "upload": upload, "answer": answer, "final": final}
    finally:
        deleted = await client.delete("/v1/sessions/" + session)
        deleted.raise_for_status()


async def demo(config):
    data = Path(config["fixture"]).read_bytes()
    uploader = boto3.client(
        "s3",
        endpoint_url=config["s3_endpoint"],
        region_name="us-east-1",
        aws_access_key_id=Path(config["uploader_key_file"]).read_text().strip(),
        aws_secret_access_key=Path(config["uploader_secret_file"]).read_text().strip(),
    )
    key = config["prefix"] + "demo-" + uuid4().hex + ".txt"
    version = await asyncio.to_thread(
        uploader.put_object, Bucket=config["bucket"], Key=key, Body=data
    )
    source = {
        "storage_alias": config["storage_alias"],
        "bucket": config["bucket"],
        "key": key,
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    if version.get("VersionId"):
        source["version_id"] = version["VersionId"]
    async with httpx.AsyncClient(
        base_url=config["api_url"],
        trust_env=False,
        timeout=130,
        headers={
            "Authorization": "Bearer " + Path(config["jwt_file"]).read_text().strip(),
            "X-RAG-Service-Key": Path(config["service_key_file"]).read_text().strip(),
        },
    ) as client:
        result = await lifecycle(
            client,
            {
                "external_upload_id": uuid4().hex,
                "source": source,
                "filename": "demo.txt",
                "content_type": "text/plain",
            },
        )
        retained = await asyncio.to_thread(
            uploader.get_object,
            Bucket=config["bucket"],
            Key=key,
            **({"VersionId": source["version_id"]} if "version_id" in source else {}),
        )
        if hashlib.sha256(retained["Body"].read()).hexdigest() != source["sha256"]:
            raise RuntimeError("source_changed")
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "json": result["answer"].answerability,
                    "sse": result["final"].answerability,
                    "usage": result["final"].usage.model_dump(),
                    "output": "[REDACTED]",
                    "session_deleted": True,
                    "source_retained": True,
                }
            )
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    try:
        asyncio.run(demo(json.loads(args.config.read_text(encoding="utf-8"))))
    except Exception:
        print("Demo failed; inspect safe API/job error codes. Credentials/output withheld.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
