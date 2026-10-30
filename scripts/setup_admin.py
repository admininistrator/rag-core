"""Create an exclusive local admin hash config using hidden terminal input."""

import argparse
import getpass
import json
from pathlib import Path

from rag_core.admin.config import AdminConfig, hash_password


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--origin", default="https://localhost:8000")
    parser.add_argument("--allow-loopback-http", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new secret config path for rotation")
    password = getpass.getpass("Admin password (12 to 1024 characters): ")
    if password != getpass.getpass("Repeat admin password: "):
        parser.error("Passwords differ")
    try:
        config = AdminConfig(
            username=args.username,
            password_hash=hash_password(password),
            origin=args.origin,
            allow_loopback_http=args.allow_loopback_http,
        )
    except ValueError:
        parser.error("Invalid password or admin origin configuration")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    values = config.model_dump(mode="json")
    values["password_hash"] = config.password_hash.get_secret_value()
    # Exclusive creation, owner-only mode 0600 on POSIX/macOS.
    import os

    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(
        fd,
        "w",
        encoding="utf-8",
        newline="\n",
    ) as output:
        json.dump(values, output, indent=2)
        output.write("\n")
    os.chmod(args.output, 0o600)
    print("Admin configuration created; no credential values printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
