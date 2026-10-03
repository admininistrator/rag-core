"""Pinned offline cache verification. No model download in request/runtime paths."""

import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_PINS = Path("configs/model-artifacts.json")
DEFAULT_CACHE = Path(".local/models")


def digest_file(path: Path, algorithm: str) -> str:
    digest = hashlib.sha256() if algorithm == "sha256" else hashlib.sha1()
    if algorithm == "git-sha1":
        digest.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as stream:
        while block := stream.read(4 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def load_pins(path: Path = DEFAULT_PINS) -> dict[str, Any]:
    return dict(json.loads(path.read_text(encoding="utf-8")))


def verify_cache(cache: Path, pins: Path = DEFAULT_PINS) -> dict[str, Any]:
    spec = load_pins(pins)
    for model in spec["models"]:
        folder = cache / model["role"]
        if folder.is_symlink() or not folder.is_dir():
            raise ValueError("model_cache_invalid_directory")
        for artifact in model["files"]:
            path = folder / artifact["name"]
            if (path.is_symlink() or not path.is_file()
                or path.stat().st_size != artifact["bytes"]
                or digest_file(path, artifact["algorithm"]) != artifact["digest"]):
                raise ValueError("model_artifact_mismatch")
        if {p.name for p in folder.iterdir()} != {f["name"] for f in model["files"]}:
            raise ValueError("model_cache_unexpected_files")
    if json.loads((cache / "manifest.json").read_text(encoding="utf-8")) != spec:
        raise ValueError("model_manifest_mismatch")
    return spec
