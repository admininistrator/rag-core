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
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --no-editable \
    && chown -R ragcore:ragcore /app
USER 10001:10001
# Parser subprocess entry point; Celery ingestion orchestration remains T19.
ENTRYPOINT ["python", "-m", "rag_core.adapters.parsers.worker"]

FROM worker AS ocr-test
USER root
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core=2.37-6 \
    && rm -rf /var/lib/apt/lists/*
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ingestion --group ocr-test --no-editable \
    && chown -R ragcore:ragcore /app
COPY --chown=ragcore:ragcore tests/integration/test_ocr.py tests/integration/test_text_parsers.py ./tests/integration/
USER 10001:10001
ENTRYPOINT []
CMD ["uv", "run", "--no-sync", "pytest", "tests/integration/test_ocr.py", "-v", "-s", "--tb=short", "--basetemp=/tmp/ocr-tests", "-o", "cache_dir=/tmp/pytest-cache"]
