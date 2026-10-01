"""Explicit operator download; ingestion and tests use a local verified artifact."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen

from rag_core.adapters.tokenizer import (
    BGE_MODEL,
    BGE_REVISION,
    BGE_SHA256,
    DEFAULT_TOKENIZER_PATH,
    TOKENIZERS_VERSION,
    BgeM3Tokenizer,
)


def main() -> None:
    path = DEFAULT_TOKENIZER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        url = f"https://huggingface.co/{BGE_MODEL}/resolve/{BGE_REVISION}/tokenizer.json"
        with urlopen(url, timeout=60) as response:
            data = response.read(32 * 1024 * 1024 + 1)
        if len(data) > 32 * 1024 * 1024 or hashlib.sha256(data).hexdigest() != BGE_SHA256:
            raise ValueError("tokenizer_download_checksum_mismatch")
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as staged:
            staged_path = Path(staged.name)
            staged.write(data)
        try:
            os.replace(staged_path, path)
        finally:
            staged_path.unlink(missing_ok=True)
    tokenizer = BgeM3Tokenizer(path)
    manifest = {
        "model": BGE_MODEL,
        "revision": BGE_REVISION,
        "sha256": BGE_SHA256,
        "bytes": path.stat().st_size,
        "runtime": f"tokenizers=={TOKENIZERS_VERSION}",
    }
    path.with_name("manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"VERIFIED {tokenizer.fingerprint}; bytes={manifest['bytes']}")


if __name__ == "__main__":
    main()
