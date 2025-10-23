"""Minimal FastAPI app placeholder.

The previous project snapshot referenced ``web_app.main:app`` from
``run_server.py`` but the package had been removed during the rollback.  This
module reinstates a lightweight API surface that can be expanded once the
original endpoints are recovered.
"""

from __future__ import annotations

from fastapi import FastAPI


app = FastAPI(title="Eqratech Arabic Diana API", version="0.1.0")


@app.get("/health", tags=["status"])
def healthcheck() -> dict[str, str]:
    """Return a simple readiness indicator."""
    return {"status": "ok"}


@app.get("/ping", tags=["status"])
def ping() -> dict[str, str]:
    """Compatibility endpoint mirroring the historical service behaviour."""
    return {"message": "pong"}

