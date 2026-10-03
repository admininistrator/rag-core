"""Entrypoint deliberately fixes one model-owning process."""

import uvicorn

from rag_core.inference.app import create_app

if __name__ == "__main__":
    uvicorn.run(create_app(), host="0.0.0.0", port=8080, workers=1, access_log=False,
                limit_concurrency=64, timeout_keep_alive=5)
