"""Seed or verify the synthetic Qdrant fixture used by T02 persistence checks."""

from __future__ import annotations

import argparse

import httpx

BASE_URL = "http://qdrant:6333"
COLLECTION = "t02_persistence_fixture"
MARKER = "rag-core-t02-persistence-v1"


def seed(client: httpx.Client) -> None:
    response = client.get(f"{BASE_URL}/collections/{COLLECTION}")
    if response.status_code == 404:
        response = client.put(
            f"{BASE_URL}/collections/{COLLECTION}",
            json={"vectors": {"size": 1, "distance": "Cosine"}},
        )
        response.raise_for_status()
    else:
        response.raise_for_status()
        vectors = response.json()["result"]["config"]["params"]["vectors"]
        if vectors["size"] != 1 or vectors["distance"] != "Cosine":
            raise RuntimeError("Existing Qdrant fixture collection has incompatible config")
    response = client.put(
        f"{BASE_URL}/collections/{COLLECTION}/points?wait=true",
        json={"points": [{"id": 1, "vector": [1.0], "payload": {"marker": MARKER}}]},
    )
    response.raise_for_status()


def verify(client: httpx.Client) -> None:
    response = client.post(
        f"{BASE_URL}/collections/{COLLECTION}/points",
        json={"ids": [1], "with_payload": True, "with_vector": False},
    )
    response.raise_for_status()
    points = response.json()["result"]
    if len(points) != 1 or points[0]["payload"]["marker"] != MARKER:
        raise RuntimeError("Qdrant persistence marker is missing or incorrect")
    print(MARKER)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "verify"))
    args = parser.parse_args()
    with httpx.Client(timeout=5) as client:
        if args.action == "seed":
            seed(client)
        verify(client)


if __name__ == "__main__":
    main()
