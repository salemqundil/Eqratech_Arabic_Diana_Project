"""
FVAFK/Bayan FastAPI web application.

Exposes the FVAFK Arabic NLP pipeline via a REST API.

Usage:
    python run_server.py [--host 127.0.0.1] [--port 8000] [--reload]
    # or directly:
    uvicorn web_app.main:app --host 127.0.0.1 --port 8000
"""
from __future__ import annotations

import sys
import os
import time
from typing import Any, Dict, Optional

# Allow imports from src/ when running outside the installed package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Bayan-FVAFK Arabic NLP API",
    description=(
        "Arabic NLP pipeline: phonology (C1/C2a), morphology (C2b), "
        "and syntax analysis via the FVAFK pipeline."
    ),
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Arabic text to analyze", min_length=1)
    morphology: bool = Field(False, description="Enable morphological analysis (C2b)")


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, summary="Health check")
def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/analyze", summary="Analyze Arabic text")
def analyze(request: AnalyzeRequest) -> Dict[str, Any]:
    """
    Run the FVAFK pipeline on the supplied Arabic text.

    - **text**: The Arabic text to process (with or without diacritics).
    - **morphology**: When ``true``, the C2b morphological layer is included.

    Returns a JSON object with ``c1``, ``c2a``, optional ``c2b``, and ``stats``
    keys — identical to the CLI ``--json`` output.
    """
    try:
        from fvafk.c1 import C1Encoder
        from fvafk.c2a import (
            GateDeletion,
            GateEpenthesis,
            GateFramework,
            GateHamza,
            GateIdgham,
            GateMadd,
            GateShadda,
            GateSukun,
            GateWasl,
        )
    except ImportError as exc:  # pragma: no cover
        raise HTTPException(
            status_code=503,
            detail=f"FVAFK library not available: {exc}",
        ) from exc

    start = time.perf_counter()

    # C1 encoding
    t0 = time.perf_counter()
    encoder = C1Encoder()
    units = encoder.encode(request.text)
    c1_ms = (time.perf_counter() - t0) * 1000

    # C2a phonological gates
    t0 = time.perf_counter()
    gates = [
        GateSukun(), GateShadda(), GateHamza(),
        GateIdgham(), GateMadd(), GateDeletion(),
        GateEpenthesis(), GateWasl(),
    ]
    framework = GateFramework(gates)
    gate_results = framework.apply(units)
    c2a_ms = (time.perf_counter() - t0) * 1000

    result: Dict[str, Any] = {
        "input": request.text,
        "c1": {"num_units": len(units)},
        "c2a": {
            "gates": [
                {"gate": r.gate_name, "status": r.status.value}
                for r in gate_results
            ],
        },
        "stats": {
            "c1_time_ms": round(c1_ms, 3),
            "c2a_time_ms": round(c2a_ms, 3),
            "total_time_ms": round((time.perf_counter() - start) * 1000, 3),
            "gates_count": len(gates),
        },
    }

    # Optional C2b morphological analysis
    if request.morphology:
        from fvafk.c2b import PatternMatcher, RootExtractor
        t0 = time.perf_counter()
        extractor = RootExtractor()
        matcher = PatternMatcher()
        root = extractor.extract(request.text)
        pattern = matcher.match(request.text)
        c2b_ms = (time.perf_counter() - t0) * 1000
        result["c2b"] = {
            "root": root.formatted if root else None,
            "pattern": pattern.template if pattern else None,
        }
        result["stats"]["c2b_time_ms"] = round(c2b_ms, 3)
        result["stats"]["total_time_ms"] = round(
            (time.perf_counter() - start) * 1000, 3
        )

    return result
