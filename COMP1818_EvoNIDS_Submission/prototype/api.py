from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from prototype.replay import score_csv
from prototype.telemetry import event_to_dict, snapshot_connections

app = FastAPI(
    title="EvoNIDS Windows IDS API",
    version="1.0.0",
    description="Local defensive API bridge for the EvoNIDS React dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _model_path() -> Path:
    return Path(os.environ.get("EVONIDS_MODEL", "models/demo_pipeline.joblib"))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "evonids-api"}


@app.get("/api/connections")
def connections() -> list[dict]:
    return [event_to_dict(event) for event in snapshot_connections()]


@app.post("/api/replay")
async def replay(request: Request) -> dict:
    model_path = _model_path()
    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model not found at {model_path}. "
                "Create the demo model or set EVONIDS_MODEL to a trained pipeline."
            ),
        )

    body = await request.body()
    if not body.strip():
        raise HTTPException(status_code=400, detail="CSV request body is empty.")

    try:
        preview = pd.read_csv(io.BytesIO(body))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}") from exc

    if preview.empty:
        return {"rows": [], "count": 0}

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
            temp.write(body)
            temp_path = temp.name
        scored = score_csv(temp_path, str(model_path))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Model scoring failed: {exc}") from exc
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)

    clean = scored.where(pd.notnull(scored), None)
    return {"rows": clean.to_dict(orient="records"), "count": int(len(clean))}
