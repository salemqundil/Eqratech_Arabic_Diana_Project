"""
Tests for the FVAFK/Bayan web application (web_app/main.py).

Covers:
- GET /           → HTML page served
- GET /health     → JSON health response
- POST /analyze   → C1 + C2a JSON response
- POST /analyze with morphology=True → includes C2b
- POST /analyze with empty text → 422 validation error
"""
from __future__ import annotations

import sys
import os

import pytest

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    from web_app.main import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "<!DOCTYPE html>" in r.text
    # Arabic content present
    assert "بيان" in r.text or "فحص" in r.text


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data


# ---------------------------------------------------------------------------
# POST /analyze
# ---------------------------------------------------------------------------

def test_analyze_basic(client):
    r = client.post("/analyze", json={"text": "كِتَابٌ", "morphology": False})
    assert r.status_code == 200
    data = r.json()
    assert data["input"] == "كِتَابٌ"
    assert "c1" in data
    assert data["c1"]["num_units"] > 0
    assert "c2a" in data
    assert isinstance(data["c2a"]["gates"], list)
    assert len(data["c2a"]["gates"]) > 0
    assert "stats" in data
    assert data["stats"]["gates_count"] > 0
    # No C2b when morphology=False
    assert "c2b" not in data or data.get("c2b") is None


def test_analyze_gate_shape(client):
    r = client.post("/analyze", json={"text": "الْكِتَابُ مُفِيدٌ", "morphology": False})
    assert r.status_code == 200
    gates = r.json()["c2a"]["gates"]
    for g in gates:
        assert "gate" in g
        assert "status" in g
        assert g["status"] in ("ACCEPT", "REPAIR", "REJECT")


def test_analyze_with_morphology(client):
    r = client.post("/analyze", json={"text": "كَتَبَ", "morphology": True})
    # Either 200 with C2b data, or 503 if C2b not available
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        data = r.json()
        assert "c2b" in data
        assert "c2b_time_ms" in data["stats"]


def test_analyze_empty_text_rejected(client):
    r = client.post("/analyze", json={"text": "", "morphology": False})
    assert r.status_code == 422


def test_analyze_missing_text_rejected(client):
    r = client.post("/analyze", json={"morphology": False})
    assert r.status_code == 422
