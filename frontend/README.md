# EvoNIDS React Frontend

React + TypeScript + Vite control-centre for the Windows IDS research prototype.

## Architecture

The browser talks only to the local EvoNIDS Python API:

```text
React / Vite :5173
      |
      +--> GET  /api/health
      +--> GET  /api/connections
      +--> POST /api/replay
                  |
                  +--> passive psutil telemetry
                  +--> saved sklearn IDS pipeline
```

The live-connection screen shows passive Windows socket/process telemetry. Model replay accepts CSV data compatible with the saved classifier pipeline. Raw socket telemetry is **not** silently treated as UNSW-NB15 feature data.

## 1. Start the Python API

From the repository root:

```bash
python -m uvicorn prototype.api:app --host 127.0.0.1 --port 8000 --reload
```

Check `http://127.0.0.1:8000/api/health`.

For replay mode, either create the included smoke-test model:

```bash
python -m prototype.train_demo_model --output models/demo_pipeline.joblib
```

or point the API at the real trained coursework pipeline:

### Git Bash

```bash
export EVONIDS_MODEL=models/ga_rf_pipeline.joblib
```

### PowerShell

```powershell
$env:EVONIDS_MODEL="models/ga_rf_pipeline.joblib"
```

## 2. Start React

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## 3. Production build

```bash
npm run build
```

Vite writes the static application to `frontend/dist/`.

## Views

- **Overview** — project architecture and headline GA/RF results.
- **Live Connections** — polls `/api/connections` every three seconds and falls back to clearly labelled demo rows when the local API is unavailable.
- **Model Replay** — reads a selected CSV in the browser and submits it to `/api/replay`; scoring remains server-side.
- **Research Results** — report-ready GA, BPSO, PSO, NSGA-II and baseline comparison.

## Safety and scientific validity

The prototype is passive. It does not block connections, modify Windows Firewall, terminate processes, scan external systems, or claim that ordinary Windows socket fields are equivalent to UNSW-NB15 engineered flow features.
