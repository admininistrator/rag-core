#!/bin/sh
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SECRET_DIR="$REPO_ROOT/.local/secrets"

case "$SECRET_DIR" in
    "$REPO_ROOT"/.local/secrets) ;;
    *)
        echo "Refusing to create secrets outside repository" >&2
        exit 1
        ;;
esac

mkdir -p "$SECRET_DIR"
chmod 700 "$SECRET_DIR"

write_secret() {
    name="$1"
    val="$2"
    path="$SECRET_DIR/$name"
    if [ ! -e "$path" ]; then
        (
            umask 077
            printf "%s" "$val" > "$path"
        )
        chmod 600 "$path"
        echo "Created ignored local secret file: .local/secrets/$name"
    else
        echo "Kept existing ignored local secret file: .local/secrets/$name"
    fi
}

rand_hex_24() {
    python3 -c "import secrets; print(secrets.token_hex(24), end='')"
}

write_secret "postgres_password" "$(rand_hex_24)"
write_secret "minio_root_user" "ragcoreadmin"
write_secret "minio_root_password" "$(rand_hex_24)"

echo "Local Docker secret files are ready; values were not printed."

