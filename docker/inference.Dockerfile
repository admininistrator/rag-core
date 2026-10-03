# syntax=docker/dockerfile:1.7@sha256:a57df69d0ea827fb7266491f2813635de6f17269be881f696fbfdf2d83dda33e
FROM ghcr.io/astral-sh/uv:0.11.16@sha256:440fd6477af86a2f1b38080c539f1672cd22acb1b1a47e321dba5158ab08864d AS uv
FROM python:3.12.13-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2 AS inference
ARG MODEL_GROUP=inference
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=2 \
    HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 MODEL_CACHE=/models MODEL_DEVICE=cpu \
    TOKENIZERS_PARALLELISM=false UV_CACHE_DIR=/tmp/uv-cache
WORKDIR /app
COPY --from=uv /uv /uvx /usr/local/bin/
RUN groupadd --gid 10001 ragcore && useradd --uid 10001 --gid ragcore --no-create-home --shell /usr/sbin/nologin ragcore
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ${MODEL_GROUP} --no-install-project
COPY src ./src
COPY configs/model-artifacts.json ./configs/model-artifacts.json
COPY scripts/setup_models.py ./scripts/setup_models.py
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ${MODEL_GROUP} --no-editable \
    && test -x /app/.venv/bin/python
USER 10001:10001
CMD ["python", "-m", "rag_core.inference"]

FROM inference AS inference-test
USER root
ARG MODEL_GROUP=inference
RUN --mount=type=cache,target=/root/.cache/uv UV_CACHE_DIR=/root/.cache/uv uv sync --locked --no-dev --group ${MODEL_GROUP} --group ocr-test --no-editable \
    && test -x /app/.venv/bin/python
COPY --chown=ragcore:ragcore tests/integration/test_model_inference.py ./tests/integration/
COPY --chown=ragcore:ragcore scripts/smoke_inference.py ./scripts/smoke_inference.py
USER 10001:10001
CMD ["uv", "run", "--no-sync", "pytest", "tests/integration/test_model_inference.py", "-v", "-s", "--tb=short", "--basetemp=/tmp/models", "-o", "cache_dir=/tmp/pytest-cache"]
