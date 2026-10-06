# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e
FROM ghcr.io/astral-sh/uv:0.11.16@sha256:440fd6477af86a2f1b38080c539f1672cd22acb1b1a47e321dba5158ab08864d AS uv
FROM python:3.12.13-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2 AS worker
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_THREAD_LIMIT=1 \
    HF_HUB_OFFLINE=1 UV_CACHE_DIR=/tmp/uv-cache
WORKDIR /app
COPY --from=uv /uv /uvx /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr=5.3.0-2 tesseract-ocr-eng=1:4.1.0-2 \
    tesseract-ocr-vie=1:4.1.0-2 tesseract-ocr-osd=1:4.1.0-2 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 ragcore \
    && useradd --uid 10001 --gid ragcore --no-create-home --shell /usr/sbin/nologin ragcore
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --no-editable
USER 10001:10001
CMD ["celery", "-A", "rag_core.workers.celery:app", "worker", "-Q", "rag_core_ingestion", "--concurrency=1", "--prefetch-multiplier=1", "--loglevel=WARNING", "--without-gossip", "--without-mingle"]

FROM worker AS ocr-test
USER root
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core=2.37-6 \
    && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --group ocr-test --no-editable
COPY --chown=ragcore:ragcore tests/integration/test_ocr.py tests/integration/test_text_parsers.py ./tests/integration/
USER 10001:10001
ENTRYPOINT []
CMD ["uv", "run", "--no-sync", "pytest", "tests/integration/test_ocr.py", "-v", "-s", "--tb=short", "--basetemp=/tmp/ocr-tests", "-o", "cache_dir=/tmp/pytest-cache"]

FROM ocr-test AS ingestion-test
USER root
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --group ingestion-test --no-editable
COPY --chown=ragcore:ragcore tests/integration/conftest.py tests/integration/test_ingestion_pipeline.py ./tests/integration/
COPY --chown=ragcore:ragcore alembic.ini ./
COPY --chown=ragcore:ragcore migrations ./migrations
USER 10001:10001
CMD ["uv", "run", "--no-sync", "pytest", "tests/integration/test_ingestion_pipeline.py", "-v", "-s", "--tb=short", "--basetemp=/tmp/ingestion-tests", "-o", "cache_dir=/tmp/pytest-cache"]

FROM ingestion-test AS public-test
USER root
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --group ingestion-test --group api --no-editable
COPY --chown=ragcore:ragcore tests ./tests
COPY --chown=ragcore:ragcore scripts/demo_app.py ./scripts/demo_app.py
USER 10001:10001
CMD ["uv", "run", "--no-sync", "pytest", "tests/e2e/test_public_api.py", "-v", "-s", "--tb=short", "--basetemp=/tmp/public-tests", "-o", "cache_dir=/tmp/pytest-cache"]
