"""Run one real provider over the authenticated public API on isolated Docker services."""

import argparse
import os
import subprocess
from pathlib import Path

from rag_core.adapters.llm.config import load_provider_settings
from rag_core.domain.llm import LlmError

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["deepseek", "anthropic"], required=True)
    args = parser.parse_args()
    try:
        config = load_provider_settings(args.provider)
    except LlmError as exc:
        print(f"BLOCKED {exc.code}; configure selected provider API_KEY/MODEL in ignored .env")
        return 2
    path = ROOT / ".local/t26-live.env"
    path.parent.mkdir(exist_ok=True)
    values = config.model_dump()
    values["api_key"] = config.api_key.get_secret_value()
    lines = [f"{args.provider.upper()}_{key.upper()}={value}" for key, value in values.items()]
    # Exclusive file prevents two runs from overwriting credentials or each other's smoke.
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("BLOCKED existing .local/t26-live.env; inspect prior smoke process before removing")
        return 2
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write("\n".join(lines) + "\n")
        command = [
            "docker",
            "compose",
            "-p",
            "rag-core-t26-test",
            "-f",
            "compose.ingestion-test.yaml",
            "-f",
            "compose.public-test.yaml",
            "-f",
            "compose.live-test.yaml",
            "run",
            "--rm",
            "-e",
            "RAG_LIVE_PROVIDER=" + args.provider,
            "live-smoke",
        ]
        return subprocess.run(command, cwd=ROOT, check=False).returncode
    finally:
        path.unlink()  # Only the exact ignored credential file created by this invocation.


if __name__ == "__main__":
    raise SystemExit(main())
