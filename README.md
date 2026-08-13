# Retail Analytics

Computer-vision analytics for retail stores: detection, tracking, zones, dwell, heatmaps, queues, and a Next.js dashboard backed by FastAPI + PostgreSQL.

**Commands below assume Windows PowerShell at the repo root** unless noted. Linux/macOS users: use the same `docker compose` / `python` commands; swap path separators (`backend/.venv/bin/python` instead of `backend\.venv\Scripts\python`).

---

## Choose your setup

| Path | Best for | Postgres | App services |
|------|----------|----------|--------------|
| **[A — Fully Dockerized](#a--fully-dockerized-recommended)** | Fastest fresh clone, matches production layout | Docker | Docker (all four services) |
| **[B — Mixed mode](#b--mixed-mode-postgres-in-docker-native-venvs)** | Daily dev on Windows with hot reload | Docker | Native venvs + `npm run dev` |
| **[C — Fully native](#c--fully-native-no-docker)** | No Docker at all | Your own Postgres or skip DB features | Native venvs |

---

## A — Fully Dockerized (recommended)

One Compose stack runs **Postgres, backend, inference worker, and frontend**. Migrations run automatically when the backend container starts; **seeding is a separate manual step** (same as before).

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/macOS) or Docker Engine (Linux)
- Git

### 1. Clone and configure environment

```powershell
git clone <your-repo-url> retail-analytics
cd retail-analytics
copy .env.example .env
```

`.env.example` ships with working defaults (`POSTGRES_*`, `DATABASE_URL` for **host** access on port 5433, `STORE_TIMEZONE`, demo JWT secret). You do not need to edit `.env` for a first run. Compose overrides `DATABASE_URL` to `postgres:5432` inside containers.

### 2. Build and start all services

```powershell
docker compose -f docker/docker-compose.yml up --build -d
```

Wait until all containers are up:

```powershell
docker compose -f docker/docker-compose.yml ps
```

Expected: `postgres` **healthy**, `backend`, `inference`, and `frontend` **Up**. Ports **5433** (Postgres), **8000** (API), **3000** (dashboard).

### 3. Migrations (automatic)

On first start, the backend entrypoint runs:

```text
alembic -c database/alembic.ini upgrade head
```

Confirm in logs (verified):

```powershell
docker compose -f docker/docker-compose.yml logs backend --tail 30
```

Look for `Running upgrade ... -> 019_run_pending_cancel` then `Uvicorn running on http://0.0.0.0:8000`.

### 4. Seed the database (manual, required for login)

```powershell
# Recommended — multi-store dashboard with zones, lines, heatmaps
docker compose -f docker/docker-compose.yml exec backend python -m database.seed --demo

# Minimal — one org, three recorded cameras, no zones/lines
docker compose -f docker/docker-compose.yml exec backend python -m database.seed
```

`--demo` takes ~2 minutes (synthetic metrics + heatmap buckets). It is **not** run automatically on `docker compose up`.

### 5. Open the app

| What | URL |
|------|-----|
| Dashboard | http://localhost:3000 |
| Swagger API docs | http://127.0.0.1:8000/docs |
| Backend health (direct) | http://127.0.0.1:8000/health |

The frontend proxies `/api/*` to the backend via `BACKEND_INTERNAL_URL=http://backend:8000` (set in Compose). There is **no** `/api/health` route — use `/health` on the backend directly.

### 6. Log in

| Email | Password | Role |
|-------|----------|------|
| `admin@demo-retail.local` | `demo` | admin |
| `user@demo-retail.local` | `demo` | user |

With `--demo` seed, `analyst@demo-retail.local` / `demo` is also available (second store).

There is **no seeded superadmin account** — run `tests/scripts/seed_superadmin_manual_test.py` for `superadmin@test.local` / `superadmin-test-pass` if you need org-admin routes.

**Verify API through the frontend proxy** (verified on Windows PowerShell):

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"email":"admin@demo-retail.local","password":"demo"}'
```

### 7. Recorded-video processing (smoke test)

Demo seed includes recorded cameras (e.g. `town` → `sample-data/town.mp4`). Trigger processing and poll status:

```powershell
$login = Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/auth/login" `
  -Method POST -ContentType "application/json" `
  -Body '{"email":"admin@demo-retail.local","password":"demo"}'
$headers = @{ Authorization = "Bearer $($login.access_token)" }

Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/cameras/town/process" -Method POST -Headers $headers
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/cameras/town/process-status" -Headers $headers
```

Status flow: `pending` → `running` → `completed` (several minutes on CPU). Watch the inference poller:

```powershell
docker compose -f docker/docker-compose.yml logs inference --tail 40
```

Verified log lines include `Started recorded processing run run_... for camera town` and `Recorded-job poller started 1 job(s)`.

### 8. Image sizes (verified after build)

```powershell
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | Select-String "docker-"
```

Example output on this machine:

```text
docker-inference    latest    3.68GB
docker-frontend     latest    1.33GB
docker-backend      latest    1.72GB
```

CPU-only torch inside inference (verified):

```powershell
docker compose -f docker/docker-compose.yml exec inference python -c "import cv2, torch; print('opencv', cv2.__version__); print('torch', torch.__version__); print('cuda', torch.cuda.is_available())"
```

Example: `opencv 4.10.0`, `torch 2.13.0+cpu`, `cuda False`.

### Architecture notes (Docker)

- **Backend** enqueues recorded jobs (`processing_runs.status=pending`); it does **not** spawn inference subprocesses (`SPAWN_INFERENCE_SUBPROCESS=false`).
- **Inference** container runs `live_analytics_worker` (live cameras + recorded-job poller).
- **Volumes:** `retail_data` (`data/heatmaps`, `data/frame-previews`, `data/run`), `inference_models` (YOLO weights), `pgdata` (database).

---

## B — Mixed mode (Postgres in Docker, native venvs)

Same as the historical setup: only Postgres runs in Docker; backend, inference, and frontend run on the host for faster iteration (`--reload`, breakpoints).

### 1. Environment and Postgres

```powershell
copy .env.example .env
docker compose -f docker/docker-compose.yml up -d postgres
```

Keep `DATABASE_URL=...@localhost:5433/...` in `.env` (host port maps to the container).

### 2. Backend venv

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\pip install -r backend\requirements.txt -r database\requirements.txt
backend\.venv\Scripts\alembic -c database/alembic.ini upgrade head
backend\.venv\Scripts\python -m database.seed --demo
```

### 3. Inference venv

Still **required**. The backend spawns the live-analytics worker from `inference\.venv` by default (`SPAWN_INFERENCE_SUBPROCESS=true`). That worker also polls Postgres for **recorded-video jobs** (no separate `process_recorded` subprocess anymore).

```powershell
python -m venv inference\.venv
inference\.venv\Scripts\pip install -r inference\requirements.txt
```

First `pip install` pulls CPU `torch` via `ultralytics` (large download).

### 4. Start backend and frontend

```powershell
.\scripts\dev-backend.ps1
```

Swagger: http://127.0.0.1:8000/docs

```powershell
cd frontend
npm install
npm run dev
```

Dashboard: http://localhost:3000

### 5. Log in

Same credentials as [section A](#6-log-in).

### Environment variables (mixed / native)

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | `...@localhost:5433/...` when Postgres is in Docker |
| `STORE_TIMEZONE` | IANA name for rollups (read via `database.config.get_store_timezone()` and backend `Settings.store_timezone`) |
| `JWT_SECRET_KEY`, `API_DEFAULT_PASSWORD` | Auth |
| `SPAWN_INFERENCE_SUBPROCESS` | Default `true` — backend starts `inference/.venv` worker on startup |

---

## C — Fully native (no Docker)

Use if you already run PostgreSQL locally (adjust `DATABASE_URL` port/user accordingly).

```powershell
copy .env.example .env
# Edit DATABASE_URL if your Postgres is not on localhost:5433

python -m venv backend\.venv
backend\.venv\Scripts\pip install -r backend\requirements.txt -r database\requirements.txt
backend\.venv\Scripts\alembic -c database/alembic.ini upgrade head
backend\.venv\Scripts\python -m database.seed --demo

python -m venv inference\.venv
inference\.venv\Scripts\pip install -r inference\requirements.txt

.\scripts\dev-backend.ps1
# separate terminal:
cd frontend; npm install; npm run dev
```

---

## RTSP / live-camera setups

**No physical RTSP camera was tested inside Docker in this repo.** Demo seed includes placeholder `rtsp://demo.local/...` URLs — the inference container logs expected DNS failures for those. Recorded-file processing **was** verified in Docker.

### How to tell which situation you are in

| Your environment | Host networking | Typical RTSP approach |
|------------------|-----------------|------------------------|
| **Linux** + Docker Engine | `network_mode: host` supported | Override below (**untested** here) |
| **Windows** Docker Desktop | **Not** supported like Linux | Bridge, WSL2 workaround, or native inference |
| **macOS** Docker Desktop | **Not** supported like Linux | Same as Windows |
| **Mixed / native** on Windows | N/A (host OS sees LAN) | Run worker in `inference\.venv` (default with `dev-backend.ps1`) |

### Linux Docker — `network_mode: host` (untested)

Example override file: `docker/docker-compose.rtsp-linux.override.example.yml`

```powershell
docker compose -f docker/docker-compose.yml -f docker/docker-compose.rtsp-linux.override.example.yml up -d
```

This puts **only the inference service** on the host network so `rtsp://192.168.x.x/...` behaves like a native process. Postgres URL in the override points at `127.0.0.1:5433` because service DNS names are unavailable in host mode.

**Not verified** on a Linux host or with a real camera — validate before relying on it.

### Windows / macOS Docker Desktop

Host networking is **not** available the same way as on Linux. Realistic options:

1. **Default bridge networking** — may reach some LAN cameras over TCP RTSP (`rtsp_transport=tcp` is already the codebase default). **Unverified**; depends on NVR, subnet, and Docker Desktop networking.
2. **WSL2 + Linux Docker** — run the stack under WSL2 and use the Linux host-network override if your cameras are reachable from the WSL2 VM.
3. **Hybrid (often best on Windows)** — Postgres + backend + frontend in Compose; run inference **natively**:

   ```powershell
   docker compose -f docker/docker-compose.yml up -d postgres backend frontend
   # In .env for backend container: SPAWN_INFERENCE_SUBPROCESS=false (Compose sets this)
   # On host:
   inference\.venv\Scripts\python -m inference.pipeline.live_analytics_worker --reconcile-interval 30
   ```

   Ensure host `DATABASE_URL` uses `localhost:5433` and the worker loads the same `.env`.

### Optional RTSP integration test (host, not container)

```powershell
# Add to .env: RTSP_TEST_URL=rtsp://user:pass@10.0.0.5:554/stream
inference\.venv\Scripts\python -m pytest tests/ -m rtsp
```

Skipped unless `RTSP_TEST_URL` is set.

---

## Rebuilding after code changes

| Change | Command |
|--------|---------|
| Application code (Python/TS) | `docker compose -f docker/docker-compose.yml up --build -d` |
| Frontend only | `docker compose -f docker/docker-compose.yml up --build -d frontend` |
| Dependencies (`requirements.txt`, `package.json`) | `docker compose -f docker/docker-compose.yml build --no-cache <service>` then `up -d` |

### When `down -v` is required

```powershell
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up --build -d
docker compose -f docker/docker-compose.yml exec backend python -m database.seed --demo
```

Use a **clean volume wipe** when:

- Alembic migration changed (new revision under `database/alembic/versions/`) and you want a fresh DB
- Corrupted or inconsistent local data
- You need to reproduce a first-time clone

**Do not** use `down -v` for routine code edits — it deletes Postgres data, heatmaps, frame previews, and downloaded model weights (re-seed and re-download required).

Verified: `docker compose -f docker/docker-compose.yml down -v` followed by `up -d` brings up a fresh stack; migrations run automatically; seed must be re-run manually.

---

## Troubleshooting

### Container cannot reach Postgres

**Symptoms:** Backend or inference crash loops; logs show connection refused to `postgres` or `localhost`.

**Checks:**

```powershell
docker compose -f docker/docker-compose.yml ps
docker compose -f docker/docker-compose.yml logs postgres --tail 20
docker compose -f docker/docker-compose.yml logs backend --tail 30
```

- `postgres` must be **healthy** before backend/inference start.
- Inside containers, `DATABASE_URL` must use host **`postgres`** and port **`5432`** (set by Compose `environment:`). On the **host**, use `localhost:5433` in `.env` for native tools.

### Frontend cannot reach backend

**Symptoms:** Dashboard loads but API calls fail; network errors on `/api/...`.

**Checks:**

- Frontend container needs `BACKEND_INTERNAL_URL=http://backend:8000` (set in `docker-compose.yml`).
- Backend must be up: `curl.exe -s http://127.0.0.1:8000/health` → `{"status":"ok"}`.
- Test proxy + auth:

  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/auth/login" `
    -Method POST -ContentType "application/json" `
    -Body '{"email":"admin@demo-retail.local","password":"demo"}'
  ```

- Rebuild frontend after `next.config.mjs` changes: `docker compose -f docker/docker-compose.yml up --build -d frontend`.

### `cv2` / OpenCV errors in inference container

**Symptoms:** `ImportError: libGL.so...` or `import cv2` fails in inference.

**Verify:**

```powershell
docker compose -f docker/docker-compose.yml exec inference python -c "import cv2; print(cv2.__version__)"
```

The image installs `libgl1` and `libglib2.0-0` and runs this import at build time. If you changed the Dockerfile, rebuild:

```powershell
docker compose -f docker/docker-compose.yml build --no-cache inference
docker compose -f docker/docker-compose.yml up -d inference
```

### Recorded-video / inference poller status

There is **no** backend subprocess log for recorded jobs. Use:

**API (admin):**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/cameras/<camera_id>/process-status" -Headers $headers
```

**Inference container logs:**

```powershell
docker compose -f docker/docker-compose.yml logs inference --tail 100
docker compose -f docker/docker-compose.yml logs -f inference
```

Look for `Recorded-job poller started`, `Started recorded processing run`, or errors from `process_recorded`.

**Database:**

```powershell
docker compose -f docker/docker-compose.yml exec postgres psql -U retail -d retail_analytics `
  -c "SELECT id, camera_id, status, message, started_at, finished_at FROM processing_runs ORDER BY started_at DESC LIMIT 5;"
```

Statuses: `pending` → `running` → `completed` / `failed`.

### YOLO model weights

Weights are **not** in git. On first inference, ultralytics downloads `yolov8n.pt` into the `inference_models` volume. Requires outbound network from the inference container.

---

## A note on YOLO model weights

Model weights (`yolov8n.pt`) are **not committed to this repo**. The default `ultralytics` backend auto-downloads them on first inference run — this requires network access on first use. The alternative `--backend onnx` path has no auto-download; you'd need to export `inference/models/yolov8n.onnx` manually before using it.

## Project Structure

| Module | Purpose |
|----------|----------|
| frontend | Next.js Dashboard |
| backend | FastAPI REST API |
| inference | Detection and Tracking Service |
| analytics | Zone, Queue, Occupancy, Heatmaps, **Events / Analytics Engine** |
| database | PostgreSQL Schema and Migrations |
| docker | Dockerfiles and Compose |
| tests | Test scripts and datasets |
| sample-data | Development videos |
| docs | Documentation |

---

## Architecture

Frontend
↓

Backend API
↓

Inference Engine
↓

Analytics Engine
↓

Database

---

## Testing

All commands assume you are at the **repo root** with the Python venv active:

```powershell
cd C:\path\to\retail-analytics
.\inference\.venv\Scripts\Activate.ps1
```

Run demos and pytest from the repo root unless noted otherwise.

### Automated tests (`pytest`)

```powershell
# Full suite (excludes hardware-gated webcam/rtsp unless env is set)
python -m pytest tests/

# Fast unit tests only — skip model-weight integration tests
python -m pytest tests/ -m "not detection and not tracking and not counting and not occupancy and not zones and not dwell and not heatmaps and not slow"

# Skip slow full-video sweeps
python -m pytest tests/ -m "not slow"

# Per module
python -m pytest tests/test_video_source.py -q
python -m pytest tests/test_detection.py -q
python -m pytest tests/test_tracking.py -q
python -m pytest tests/test_counting.py -q
python -m pytest tests/test_occupancy.py -q
python -m pytest tests/test_zones.py -q
python -m pytest tests/test_dwell.py -q
python -m pytest tests/test_heatmaps.py -q
python -m pytest tests/test_demo_source.py -q
python -m pytest tests/test_queues.py -q

# Module 10 — Event bus & Analytics Engine
python -m pytest tests/test_events.py -q
python tests/scripts/run-events-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json

# Module 11 — Database & persistence (requires Postgres via Docker)
python -m pytest tests/test_database.py -q

# Module 12 — Backend REST API (requires Postgres; use backend venv)
python -m pytest tests/test_api.py -q

# Integration tests only (loads YOLO weights — slower)
python -m pytest tests/ -m detection
python -m pytest tests/ -m tracking
python -m pytest tests/ -m counting
python -m pytest tests/ -m occupancy
python -m pytest tests/ -m zones
python -m pytest tests/ -m dwell
python -m pytest tests/ -m heatmaps
python -m pytest tests/ -m queues

# Hardware-gated (opt-in; skipped by default in CI)
python -m pytest tests/ -m webcam
python -m pytest tests/ -m rtsp
# RTSP integration test reads RTSP_TEST_URL from .env when set
```

### Video source smoke test (Module 1)

Confirms frames flow before running detection or analytics.

```powershell
# File
python tests/scripts/smoke_video_source.py sample-data/entrance.mp4
python tests/scripts/smoke_video_source.py sample-data/checkout.mp4 --fps 15 --frames 50

# Webcam (device index 0)
python tests/scripts/smoke_video_source.py 0

# RTSP
python tests/scripts/smoke_video_source.py rtsp://user:pass@10.0.0.5:554/stream
```

### Draw counting lines (Module 4)

Interactive OpenCV editor on the **first frame** of a video (coordinates match the 640px-downscaled pipeline).

**Controls:** left-click endpoint 1 → endpoint 2 → point on the **inside** side of the store · `r` reset · `s` save · `q` / ESC quit

```powershell
python -m analytics.counting.line_editor sample-data/entrance.mp4 --camera-id entrance --output tests/videos/entrance_line.json

python -m analytics.counting.line_editor sample-data/CMMentrance.mp4 --camera-id CMMentrance --name main_entrance --output tests/videos/CMMentrance_line.json

python -m analytics.counting.line_editor sample-data/store-floor.mp4 --camera-id store-floor --output tests/videos/store_floor_line.json
```

### Draw zone polygons (Module 6)

Interactive OpenCV editor on the **first frame**. Saves a `ZoneConfig` JSON (merges into existing file if present).

**Controls:** left-click vertices · right-click or `c` close polygon (≥ 3 points) · `r` reset · `s` save · `q` / ESC quit

```powershell
python -m analytics.zones.polygon_editor sample-data/store-floor.mp4 --camera-id store-floor --zone-id floor_center --zone-name "Floor Center" --output tests/videos/store_floor_zones.json

python -m analytics.zones.polygon_editor sample-data/town.mp4 --camera-id town --zone-id main_street --zone-name "Main Street" --zone-type general --output tests/videos/town_zones.json

python -m analytics.zones.polygon_editor sample-data/town.mp4 --camera-id town --zone-id shop_front --zone-name "Shop Front" --zone-type promotional --output tests/videos/town_zones.json
```

`--zone-type` choices: `entrance`, `electronics`, `clothing`, `grocery`, `promotional`, `checkout`, `waiting`, `queue`, `general`

### Manual checkpoint demos

Every demo accepts **file**, **RTSP URL**, or **webcam index** (`0`) as `source`.

| Flag | Meaning |
|------|---------|
| `--camera-id` | Stable camera name (recommended for RTSP/webcam) |
| `--duration N` | Run N wall-clock seconds (live defaults to 120) |
| `--duration 0` | Run until Ctrl+C |
| `--target-fps` | Processing sample cap (default 10) |
| `--preview` | OpenCV live window (press `q` to stop early) |
| `--backend` | `ultralytics` (default) or `onnx` |

#### Module 2 — Detection

Writes annotated MP4 to `tests/videos/`. Logs FPS baseline to `tests/videos/detection_baseline.txt`.

```powershell
# All bundled sample videos
python tests/scripts/run-detection-demo.py
python tests/scripts/run-detection-demo.py --backend onnx

# Single source
python tests/scripts/run-detection-demo.py sample-data/entrance.mp4
python tests/scripts/run-detection-demo.py sample-data/store.mp4 --preview

# Live
python tests/scripts/run-detection-demo.py rtsp://10.0.0.5/stream --camera-id entrance --duration 60 --preview
python tests/scripts/run-detection-demo.py 0 --camera-id desk --duration 30 --preview
```

#### Module 3 — Tracking

Writes annotated MP4 to `tests/videos/tracking_{camera}_{backend}.mp4`.

```powershell
python tests/scripts/run-tracking-demo.py
python tests/scripts/run-tracking-demo.py sample-data/entrance3.mp4
python tests/scripts/run-tracking-demo.py sample-data/town.mp4 --backend onnx --preview
python tests/scripts/run-tracking-demo.py rtsp://10.0.0.5/stream --camera-id entrance --duration 60 --preview
python tests/scripts/run-tracking-demo.py 0 --camera-id desk --duration 30 --preview
```

#### Module 4 — Counting (line cross)

Requires a line JSON from `line_editor` (or uses bundled default if present).

```powershell
python tests/scripts/run-counting-demo.py sample-data/entrance.mp4
python tests/scripts/run-counting-demo.py sample-data/CMMentrance.mp4 --line-config tests/videos/CMMentrance_line.json
python tests/scripts/run-counting-demo.py rtsp://10.0.0.5/stream --camera-id entrance --line-config tests/videos/entrance_line.json --duration 120
python tests/scripts/run-counting-demo.py 0 --camera-id desk --duration 60 --preview
```

Occupancy (Module 5) is covered by `pytest tests/test_occupancy.py` and printed at the end of the counting demo when crossing events occur.

#### Module 6 — Zones

Requires a zone JSON from `polygon_editor` (or uses bundled default if present).

```powershell
python tests/scripts/run-zones-demo.py sample-data/store-floor.mp4
python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json
python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --transitions-only
python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --hysteresis-frames 3 --flap-window 5
python tests/scripts/run-zones-demo.py rtsp://10.0.0.5/stream --camera-id entrance --zone-config tests/videos/town_zones.json --duration 120 --preview
```

#### Module 7 — Dwell time

Requires `--zone-config` (draw zones first).

```powershell
python tests/scripts/run-dwell-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json
python tests/scripts/run-dwell-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --dwell-threshold 30
python tests/scripts/run-dwell-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --lost-track-timeout 5
python tests/scripts/run-dwell-demo.py rtsp://10.0.0.5/stream --zone-config tests/videos/town_zones.json --camera-id entrance --duration 300
python tests/scripts/run-dwell-demo.py 0 --zone-config tests/videos/town_zones.json --camera-id desk --duration 120 --preview
```

#### Module 8 — Heatmaps

Saves overlay PNG and hour buckets under `data/heatmaps/{camera_id}/`.

```powershell
python tests/scripts/run-heatmap-demo.py sample-data/store.mp4 -o tests/videos/store_heatmap.png
python tests/scripts/run-heatmap-demo.py sample-data/open.mp4 -o tests/videos/open_heatmap.png
python tests/scripts/run-heatmap-demo.py sample-data/town.mp4 --camera-id town -o tests/videos/town_heatmap.png

# Live — overlay refreshes every 30s; PNG saved at end
python tests/scripts/run-heatmap-demo.py rtsp://user:pass@10.0.0.5/stream --camera-id entrance --duration 120 --preview-every 30
python tests/scripts/run-heatmap-demo.py 0 --camera-id desk-cam --duration 60 --preview

# File replay hour-bucket anchor (optional; live uses wall clock)
python tests/scripts/run-heatmap-demo.py sample-data/store.mp4 --recording-start 2026-07-28T12:00:00+00:00
```

#### Module 9 — Queue analytics

Requires queue zones in config (`zone_type`: `queue`, `checkout`, or `waiting`). Draw with `polygon_editor` first.

```powershell
python -m analytics.zones.polygon_editor sample-data/checkout.mp4 --camera-id checkout --zone-id lane_1 --zone-name "Lane 1" --zone-type queue --output tests/videos/checkout_zones.json

python tests/scripts/run-queues-demo.py sample-data/checkout.mp4 --zone-config tests/videos/checkout_zones.json
python tests/scripts/run-queues-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --length-threshold 3 --duration-threshold 60
python tests/scripts/run-queues-demo.py rtsp://10.0.0.5/stream --zone-config tests/videos/checkout_zones.json --camera-id checkout --duration 120 --preview
```

#### Module 11 — Database & event storage

PostgreSQL stores aggregated metrics and analytics events. See [Getting Started](#choose-your-setup) for Postgres setup. Docker maps **host port 5433** (avoids conflict with a local PostgreSQL on 5432).

```powershell
# After Postgres is running and migrations applied (see sections A–C above)
backend\.venv\Scripts\python -m database.seed --demo
python tests/scripts/run-events-demo.py sample-data/town.mp4 `
  --camera-id town --zone-config tests/videos/town_zones.json --persist-db

pytest tests/test_database.py -v
docker compose -f docker/docker-compose.yml exec postgres psql -U retail -d retail_analytics `
  -c "SELECT hour, entries FROM visitor_metrics WHERE store_id='store_main' ORDER BY hour LIMIT 5;"
```

See `database/README.md` for schema, retention policy, and dashboard query examples.

#### Module 12 — Backend REST API

```powershell
# After Postgres + migrations + seed (see Getting Started)
.\scripts\dev-backend.ps1

# Tests
backend\.venv\Scripts\python -m pytest tests/test_api.py -v
```

### Suggested end-to-end workflow

1. `smoke_video_source.py` — confirm the source opens.
2. `line_editor` / `polygon_editor` — draw geometry on a representative frame.
3. Run the module demo with `--line-config` or `--zone-config`.
4. For live cameras: add `--camera-id`, `--duration`, and `--preview` as needed.
5. `python -m pytest tests/` — confirm automated tests still pass.

### Outputs

| Artifact | Location |
|----------|----------|
| Line / zone configs | `tests/videos/*.json` |
| Annotated detection / tracking videos | `tests/videos/` |
| Detection FPS baseline log | `tests/videos/detection_baseline.txt` |
| Heatmap overlays | `tests/videos/*_heatmap.png` (or `-o` path) |
| Heatmap hour buckets | `data/heatmaps/{camera_id}/{date}/{hour}.npz` |

## Known Limitations / Not Yet Implemented

- **Camera and processing status can lag in the UI.** Processing succeeds correctly in the backend, but the frontend doesn't always reflect current status immediately — under investigation.
- **Occupancy-style stat cards on the Live Cameras page are being removed** (grid view and camera detail view) — pending cleanup.
- **Superadmin account management has no UI or API.** The only way to create a superadmin account today is the seed script or the manual test script mentioned above — there's no create/edit/disable/delete flow yet.
- **The live-analytics worker assumes a single inference instance.** Running multiple inference containers would process cameras redundantly — no leader election yet.
- **`ONNX` detection backend requires a manually exported model file** (`inference/models/yolov8n.onnx`) — there's no automated export step in setup.
