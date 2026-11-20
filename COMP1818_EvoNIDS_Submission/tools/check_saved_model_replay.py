"""Acceptance check for an existing, trusted EvoNIDS sklearn pipeline.

No training, optimisation or changes to official experiment result files.
Run from COMP1818_EvoNIDS_Submission with a locally saved model and a
compatible CSV (for example the official UNSW-NB15 test partition).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from prototype.api import app


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", type=Path, required=True,
                   help="Trusted local .joblib pipeline created by this coursework")
    p.add_argument("--csv", type=Path, required=True,
                   help="CSV with all raw features required by the saved model")
    p.add_argument("--rows", type=int, default=20)
    p.add_argument("--features-json", type=Path,
                   help="Optional saved feature-name list to cross-check the model")
    args = p.parse_args()

    if args.rows < 1:
        p.error("--rows must be positive")
    if not args.model.is_file():
        p.error(f"model not found: {args.model}")
    if not args.csv.is_file():
        p.error(f"CSV not found: {args.csv}")

    # joblib uses pickle: only load a model you trained yourself or fully trust.
    model = joblib.load(args.model)
    if not hasattr(model, "feature_names_in_"):
        raise RuntimeError("Saved model lacks feature_names_in_; cannot verify feature schema")
    required = list(model.feature_names_in_)
    if args.features_json:
        expected = json.loads(args.features_json.read_text(encoding="utf-8"))
        if required != expected:
            raise RuntimeError("Saved feature-name list does not match pipeline order")

    sample = pd.read_csv(args.csv, nrows=args.rows)
    if sample.empty:
        raise RuntimeError("No records found")
    missing = [name for name in required if name not in sample.columns]
    if missing:
        raise RuntimeError(f"Missing model features: {missing}")
    sample_csv = sample.to_csv(index=False).encode("utf-8")

    # Independently compare direct inference to the actual HTTP API endpoint.
    direct = np.asarray(model.predict(sample[required]))
    previous = os.environ.get("EVONIDS_MODEL")
    os.environ["EVONIDS_MODEL"] = str(args.model.resolve())
    try:
        with TestClient(app) as client:
            health = client.get("/api/health")
            assert health.status_code == 200, health.text
            replay = client.post("/api/replay", content=sample_csv,
                                 headers={"content-type": "text/csv; charset=utf-8"})
            assert replay.status_code == 200, replay.text
            result = replay.json()
    finally:
        if previous is None:
            os.environ.pop("EVONIDS_MODEL", None)
        else:
            os.environ["EVONIDS_MODEL"] = previous

    assert result["count"] == len(sample), "API returned unexpected row count"
    returned = np.asarray([row["ids_prediction"] for row in result["rows"]])
    np.testing.assert_array_equal(returned.astype(str), direct.astype(str))
    print("PASS: saved pipeline feature schema and API replay")
    print(f"Model: {args.model}")
    print(f"Rows checked: {len(sample)}; selected raw features: {len(required)}")
    print("API predictions exactly match direct sklearn predictions.")
    print("This verifies integration, not predictive accuracy or deployment readiness.")


if __name__ == "__main__":
    main()
