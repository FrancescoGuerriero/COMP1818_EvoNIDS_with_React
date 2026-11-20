"""Dataset-free API integration tests for the EvoNIDS prototype.

These exercise the real FastAPI request/replay path using a synthetic,
clearly-labelled demonstration pipeline; they do not evaluate UNSW-NB15.
"""
from __future__ import annotations

import sys

import pandas as pd
from fastapi.testclient import TestClient

from prototype import train_demo_model
from prototype.api import app


def test_api_health_and_passive_connections():
    with TestClient(app) as client:
        health = client.get("/api/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok", "service": "evonids-api"}
        connections = client.get("/api/connections")
        assert connections.status_code == 200
        assert isinstance(connections.json(), list)


def test_api_replay_requires_a_model(monkeypatch, tmp_path):
    monkeypatch.setenv("EVONIDS_MODEL", str(tmp_path / "absent.joblib"))
    with TestClient(app) as client:
        response = client.post("/api/replay", content=b"service,sbytes\\nhttp,42\\n",
                               headers={"content-type": "text/csv"})
        assert response.status_code == 503
        assert "Model not found" in response.json()["detail"]


def test_api_synthetic_csv_replay_and_validation(monkeypatch, tmp_path):
    model = tmp_path / "demo.joblib"
    rows = tmp_path / "demo_rows.csv"
    monkeypatch.setattr(sys, "argv", ["train_demo_model",
        "--output", str(model), "--csv-output", str(rows)])
    train_demo_model.main()
    monkeypatch.setenv("EVONIDS_MODEL", str(model))

    with TestClient(app) as client:
        empty = client.post("/api/replay", content=b"")
        assert empty.status_code == 400

        malformed = client.post("/api/replay", content=b"\\xff\\xfe")
        assert malformed.status_code in (400, 422)

        response = client.post("/api/replay", content=rows.read_bytes(),
                               headers={"content-type": "text/csv; charset=utf-8"})
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["count"] == len(pd.read_csv(rows)) == 20
        assert len(payload["rows"]) == 20
        assert all(int(row["ids_prediction"]) in (0, 1) for row in payload["rows"])
        assert all(0 <= float(row["attack_probability"]) <= 1 for row in payload["rows"])

        incomplete = client.post("/api/replay", content=b"service,sbytes\\nhttp,42\\n")
        assert incomplete.status_code == 422
        assert "missing model features" in incomplete.json()["detail"]
