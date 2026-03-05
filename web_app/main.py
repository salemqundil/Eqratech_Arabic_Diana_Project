"""
FastAPI application for FVAFK / Bayan Arabic NLP pipeline.

Run with:
    python run_server.py
    # or directly:
    uvicorn web_app.main:app --reload
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from fvafk.cli.main import MinimalCLI

app = FastAPI(
    title="FVAFK / Bayan — Arabic NLP API",
    description=(
        "REST API for the FVAFK Arabic NLP pipeline: "
        "encoding (C1), phonological gates (C2a), morphology (C2b)."
    ),
    version="0.1.0",
)

# Initialise once so gate setup cost is paid at startup, not per request.
_cli = MinimalCLI(verbose=False, json_output=True)


class AnalyseRequest(BaseModel):
    text: str = Field(..., min_length=1)
    morphology: bool = False


@app.get("/", response_class=HTMLResponse, summary="Web UI")
def root() -> str:
    """Serve a minimal HTML page for quick interactive checks."""
    return """<!DOCTYPE html>
<html lang="ar">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>بيان - FVAFK</title>
</head>
<body>
  <h1>بيان / FVAFK</h1>
  <p>خدمة فحص النص العربي جاهزة.</p>
</body>
</html>"""


@app.get("/health", summary="Health check (alias)")
def health() -> dict[str, str]:
    return {"status": "ok", "version": app.version}


def _normalize_analyze_response(payload: dict[str, Any]) -> dict[str, Any]:
    c2a = payload.get("c2a")
    if isinstance(c2a, dict):
        gates = c2a.get("gates")
        if isinstance(gates, list):
            normalized_gates: list[dict[str, Any]] = []
            for gate in gates:
                if isinstance(gate, dict):
                    item = dict(gate)
                    item.setdefault("gate", item.get("gate_id", ""))
                    normalized_gates.append(item)
                else:
                    normalized_gates.append({"gate": str(gate), "status": "ACCEPT"})
            c2a["gates"] = normalized_gates
    return payload


def _run_analysis(request: AnalyseRequest) -> dict[str, Any]:
    """
    Run the full FVAFK pipeline on the supplied Arabic text.

    - **text**: Arabic text to analyse (with or without diacritics)
    - **morphology**: also run the C2b morphological analyser
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")

    result: Optional[dict[str, Any]] = _cli.run(
        request.text,
        morphology=request.morphology,
    )
    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="analysis failed")
    return _normalize_analyze_response(result)


@app.post("/analyse", summary="Analyse Arabic text")
def analyse(request: AnalyseRequest) -> dict[str, Any]:
    return _run_analysis(request)


@app.post("/analyze", summary="Analyze Arabic text")
def analyze(request: AnalyseRequest) -> dict[str, Any]:
    return _run_analysis(request)
