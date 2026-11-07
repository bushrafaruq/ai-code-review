"""HTTP API: the review workflow as modular FastAPI services (see reviewer/services/).

    uvicorn reviewer.api:app --port 8001        # interactive docs at http://localhost:8001/docs
    curl -X POST localhost:8001/review -H 'content-type: application/json' \
         --data "$(python -c 'import json,sys; print(json.dumps({"diff": sys.stdin.read()}))' < examples/sample.diff)"
"""

from __future__ import annotations

from fastapi import FastAPI

from .services import diff_service, review_service, static_service, tests_service

app = FastAPI(title="AI-Assisted Code Review", version="1.1.0")
app.include_router(diff_service.router)
app.include_router(static_service.router)
app.include_router(tests_service.router)
app.include_router(review_service.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
