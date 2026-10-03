"""Explicit operator download from official pinned Hugging Face revisions."""

import argparse
import json
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen

from rag_core.adapters.models.artifacts import (
    DEFAULT_CACHE,
    DEFAULT_PINS,
    digest_file,
    load_pins,
    verify_cache,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--pins", type=Path, default=DEFAULT_PINS)
    args = parser.parse_args()
    spec = load_pins(args.pins)
    args.cache.mkdir(parents=True, exist_ok=True)
    for model in spec["models"]:
        folder = args.cache / model["role"]
        folder.mkdir(exist_ok=True)
        for artifact in model["files"]:
            path = folder / artifact["name"]
            if path.exists():
                if (path.stat().st_size != artifact["bytes"]
                    or digest_file(path, artifact["algorithm"]) != artifact["digest"]):
                    raise ValueError("existing_model_artifact_mismatch")
                continue
            url = (f"https://huggingface.co/{model['repo']}/resolve/"
                   f"{model['revision']}/{artifact['name']}")
            with tempfile.NamedTemporaryFile(dir=folder, delete=False) as output:
                staged = Path(output.name)
                try:
                    with urlopen(url, timeout=120) as response:
                        count = 0
                        while data := response.read(4 * 1024 * 1024):
                            count += len(data)
                            if count > artifact["bytes"]:
                                raise ValueError("model_download_size_mismatch")
                            output.write(data)
                except BaseException:
                    output.close()
                    staged.unlink(missing_ok=True)
                    raise
            try:
                if (staged.stat().st_size != artifact["bytes"]
                    or digest_file(staged, artifact["algorithm"]) != artifact["digest"]):
                    raise ValueError("model_download_digest_mismatch")
                os.replace(staged, path)
            finally:
                staged.unlink(missing_ok=True)
            print(f"DOWNLOADED {model['role']}/{artifact['name']} {artifact['bytes']}B", flush=True)
    (args.cache / "manifest.json").write_text(json.dumps(spec, indent=2) + "\n")
    verify_cache(args.cache, args.pins)
    print("MODEL CACHE VERIFIED", flush=True)


if __name__ == "__main__":
    main()
