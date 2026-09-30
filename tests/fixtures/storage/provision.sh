#!/bin/sh
set -eu
mc alias set local http://minio:9000 "$(cat /run/secrets/minio_root_user)" "$(cat /run/secrets/minio_root_password)" >/dev/null
mc mb --ignore-existing local/rag-core-storage-test >/dev/null
mc version enable local/rag-core-storage-test >/dev/null
mc admin policy create local rag-core-t11-reader /fixture/reader.json >/dev/null
mc admin policy create local rag-core-t11-uploader /fixture/uploader.json >/dev/null
mc admin user add local "$(cat /run/secrets/minio_reader_user)" "$(cat /run/secrets/minio_reader_password)" >/dev/null
mc admin user add local "$(cat /run/secrets/minio_uploader_user)" "$(cat /run/secrets/minio_uploader_password)" >/dev/null
mc admin policy attach local rag-core-t11-reader --user "$(cat /run/secrets/minio_reader_user)" >/dev/null
mc admin policy attach local rag-core-t11-uploader --user "$(cat /run/secrets/minio_uploader_user)" >/dev/null
echo 'T11 isolated bucket and separate reader/uploader principals are ready.'
