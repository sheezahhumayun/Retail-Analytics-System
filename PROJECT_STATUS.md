# Retail Analytics CV Platform — Project Status

**Last updated:** 2026-07-22
**Reference roadmap:** Retail_Analytics_Build_Roadmap.md

---

## Status Overview

| # | Module | Status |
|---|--------|--------|
| 0 | Environment & Repository Setup | ✅ Done |
| 1 | Video Ingestion Layer | ✅ Done |
| 2 | Person Detection | ⬜ Not started |
| 3 | Multi-Object Tracking | ⬜ Not started |
| 4 | Entry/Exit Counting Lines | ⬜ Not started |
| 5 | Occupancy Analytics | ⬜ Not started |
| 6 | Zone Management & Zone Analytics | ⬜ Not started |
| 7 | Dwell-Time Analytics | ⬜ Not started |
| 8 | Heatmap Generation | ⬜ Not started |
| 9 | Queue Analytics | ⬜ Not started |
| 10 | Event Architecture & Analytics Engine | ⬜ Not started |
| 11 | Database & Event Storage | ⬜ Not started |
| 12 | Backend REST API | ⬜ Not started |
| 13 | Frontend Web Dashboard | ⬜ Not started |
| 14 | Reports (CSV/PDF export) | ⬜ Not started |
| 15 | Alerting | ⬜ Not started |
| 16 | System Administration | ⬜ Not started |
| 17 | Dockerization & Deployment | ⬜ Not started |
| 18 | Testing, Evaluation & Accuracy Validation | ⬜ Not started |
| 19 | Scalability & Path to Multi-Camera/Multi-Store | ⬜ Not started |
| 20 | Final Demo Script | ⬜ Not started |

---

## ✅ Module 0 — Environment & Repository Setup — DONE

**Environment:** Windows, PowerShell, VS Code

### What was actually done

1. **Project folder created** at `retail-analytics/` (via `mkdir` + `cd`), confirmed with `pwd`.
2. **Git initialized** (`git init`), confirmed with `git status`.
3. **Folder structure created** exactly per plan:
   ```
   frontend/  backend/  inference/  analytics/  database/
   docker/    tests/    sample-data/  docs/
   ```
4. **README.md created** with a project structure table (module → purpose) and a simple architecture flow (Frontend → Backend API → Inference Engine → Analytics Engine → Database).
5. **.gitignore created**, covering Python (`__pycache__/`, `.venv/`), Node (`node_modules/`), `.env`, `.vscode/`, logs, and OS files (`.DS_Store`, `Thumbs.db`).
6. **Separate virtual environments created** (per the modularity/independent-maintainability reasoning from the roadmap):
   - `backend/.venv` — verified Python 3.11.x
   - `inference/.venv` — verified Python 3.11.x
7. **`inference/requirements.txt` created** with:
   ```
   opencv-python
   ultralytics
   numpy
   ```
   Installed inside `inference/.venv` via `pip install -r requirements.txt`. Confirmed via `pip list` that `opencv-python`, `numpy`, `ultralytics`, `torch`, and `torchvision` are present (torch/torchvision pulled in automatically as Ultralytics dependencies).
8. **Frontend scaffolded** with `npx create-next-app@latest .` inside `frontend/`, using:
   - TypeScript: Yes
   - ESLint: Yes
   - Tailwind: Yes
   - `src/` directory: No
   - App Router: Yes
   - Turbopack: Yes
   - Import alias: No
   Verified `npm run dev` serves the default app at `http://localhost:3000`.
9. **Backend placeholder created**: `backend/app/` with `api/`, `models/`, `services/`, `schemas/` subfolders and an empty `main.py`.
10. **Analytics skeleton created**: `analytics/zones/`, `analytics/dwell/`, `analytics/occupancy/`, `analytics/queues/`, `analytics/heatmaps/`.
11. **Database skeleton created**: `database/migrations/`, `database/schema/`.
12. **Docker folder created** with empty placeholders: `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.inference`, `Dockerfile.frontend` (not yet filled in — that's Module 17).
13. **Tests folder created**: `tests/scripts/`, `tests/videos/`.
14. **Sample videos added** to `sample-data/`:
    - `entrance.mp4`
    - `store-floor.mp4`
    - `checkout.mp4`
    - **⚠️ Note: all three sample videos are 30fps.** Flagging this now because it matters downstream:
      - Module 1 (Video Ingestion) frame-skipping/throttling logic should be calibrated against this actual 30fps source rate, not assumed.
      - Module 2's CPU Reality Check assumed a target processing rate of ~10fps — at 30fps source, that means skipping roughly every 3rd frame (process 1 of every 3).
      - If any sample video turns out to be variable frame rate (common with downloaded stock footage), confirm actual fps with `cv2.VideoCapture(...).get(cv2.CAP_PROP_FPS)` per file rather than trusting metadata alone, since Module 1's throttle logic reads this value directly.
15. **First commit made**: `git commit -m "Module 0: Initial project structure"`.
16. **Pushed to GitHub**: remote added, pushed to `main`.

### Deviations from the roadmap's original Module 0 instructions

- Roadmap originally suggested either per-service venvs or a single shared venv as an option — **per-service venvs were used** (`backend/.venv`, `inference/.venv`), consistent with the updated Module 0 guidance in the roadmap doc.
- Frontend was scaffolded with **Next.js** (App Router, Turbopack) as per the roadmap/PRD's recommended stack — no deviation here.
- No `analytics/.venv` was created separately; analytics code will run inside the same process/environment as `inference/` for now (this wasn't explicitly specified either way in Module 0 — worth deciding explicitly before Module 6).

### ✅ Test Checkpoint 0 — Verified

- [x] `git log` shows the initial commit with full folder structure.
- [x] `python --version` inside `inference/.venv` shows 3.11.x.
- [x] Sample video opens successfully via OpenCV (`cv2.VideoCapture`) — returns `True` and a valid frame shape.

---

## ✅ Module 1 — Video Ingestion Layer — DONE

A single `VideoSource` abstraction over files / RTSP / webcam so every downstream
module (detect, track, analytics) consumes one interface and never branches on
where the frame came from. This is the seam PRD §9 mandates.

### What was actually done

1. **`inference/video/` package** with a clean separation of concerns:
   - `base.py` — `VideoSource` ABC, `CameraState` enum (PRD §8), and the two
     cross-cutting helpers the task demanded live *here, not downstream*:
     - **Target-FPS throttling** — `compute_frame_interval(source_fps, target_fps)`
       picks which frames to hand off (30fps source / 10fps target → keep every
       3rd). Skipped frames use cheap `cv2.grab()` instead of a full decode.
     - **Downscale** — `resize_long_side(frame, 640)` via `cv2.INTER_AREA`.
   - `file_source.py` — `FileVideoSource` (mp4/avi/mov, `cv2.CAP_FFMPEG`,
     optional `loop=True` for dev).
   - `rtsp_source.py` — `RTSPVideoSource` with the full reconnect state machine:
     N consecutive failed reads → exponential backoff reopen → state
     `ONLINE→ERROR→PROCESSING→ONLINE`; after a full cycle is exhausted, retries
     on a cooldown so a recovering NVR is picked up. FFMPEG timeout options set
     so a dead NVR fails a read instead of hanging the pipeline. `read()` never
     raises on transient drops (real CCTV/NVR behavior, per PRD §8).
   - `webcam_source.py` — `WebcamVideoSource` (device index; `CAP_DSHOW` on
     Windows for faster opens).
   - `factory.py` — `create_video_source(spec)` routes by spec type (int →
     webcam, `rtsp(s)://`/`rtmp://` → RTSP, else → file). Downstream code never
     branches on source type.
   - `__init__.py` + `README.md` (public API + usage examples).

2. **Tests** — `tests/test_video_source.py` + `tests/conftest.py`, **22 passed,
   1 skipped** (the live-RTSP test is gated behind an `RTSP_TEST_URL` env var
   since there's no NVR hardware here). Covers: known fps/resolution per sample
   file, downscale contract (long side ≤ 640, aspect preserved), throttle
   cadence (kept indices differ by exactly `interval`), factory routing, the
   `OFFLINE→PROCESSING→ONLINE→OFFLINE` state machine, EOF semantics, context
   manager, and the RTSP reconnect state machine (recover-from-drops,
   stays-in-error-on-exhaustion, recovers-after-cooldown, open-failure-raises).
   RTSP reconnect is unit-tested against an injected fake `VideoCapture` — no
   network needed.

3. **Smoke script** — `tests/scripts/smoke_video_source.py` (CLI over any
   source: file path / device index / `rtsp://` URL; prints fps, source vs
   output resolution, state transitions, mean/p95 read latency, effective fps).

4. **`inference/requirements.txt`** — added `pytest`.

### Verified against the real sample videos (not just unit tests)

| Video | Source fps | Source res | Output res (640 cap) | read() mean |
|---|---|---|---|---|
| entrance.mp4 | 29.97 | 2560×1440 | 640×360 | ~70 ms |
| store-floor.mp4 | 30.00 | 1920×1080 | 640×360 | ~37 ms |
| checkout.mp4 | 30.00 | 1920×1080 | 640×360 | ~34 ms |

Throttle scaling confirmed empirically: `--fps 5` (every 6th frame) → read()
mean ~74 ms; `--fps 30` (every frame) → read() mean ~14 ms.

### Decisions made

- **Target FPS default = 10** (PRD §33 says 10–15; chose the conservative end).
  At the verified ~30fps source rate, that's **process every 3rd frame** —
  exactly the heuristic flagged in Module 0's notes.
- **Long-side downscale default = 640px** (CPU reality check). `entrance.mp4`'s
  1440p and the 1080p clips all come out at 640×360, well under detection's
  needs and cheap to decode.
- **FFMPEG backend** for both file and RTSP sources — confirmed working in
  Module 0 and consistent across source types. If RTSP proves flaky on a real
  NVR, only `RTSPVideoSource._build_capture()` needs to swap to `CAP_GSTREAMER`
  or `ffmpeg-python`; no downstream module changes.
- **RTSP transport = TCP** by default (avoids UDP packet-loss tearing over
  Wi-Fi); 15s read timeout so a dead NVR can't hang the pipeline.
- **`CameraState` enum mirrors PRD §8** exactly (`Disabled/Offline/Error/
  Processing/Online`). The ingestion layer is the source of truth for the
  *true* state; Module 16's DB/UI will read `get_state()`.
- **Source-fps fallback = 30.0** when a stream reports 0/NaN (stock footage and
  some NVR exports do this).

### Deviations from the original Module 1 instructions

- Added a `retry_after_exhaustion` cooldown to RTSP: the task said "attempt to
  reopen with backoff" on N failures, but stopping permanently after one
  exhausted cycle would leave a briefly-offline NVR stuck in `Error` forever.
  Added a periodic post-exhaustion retry so a recovering NVR is picked up.
  Behavior is covered by `test_rtsp_recovers_after_exhaustion_cooldown`.
- Exposed `get_source_resolution()` in addition to the specified
  `get_resolution()` — downstream still sees the downscaled frame via the
  latter, but diagnostics / zone config (Module 6) will want the native size.

### Not in scope (deferred)

- DB persistence / full camera management UI → Module 16.
- Detection / tracking / zones → Modules 2+.
- Hardware/GPU decode acceleration → Module 17.

### ✅ Test Checkpoint 1 — Verified

- [x] `python -m pytest tests/` → 22 passed, 1 skipped.
- [x] Smoke script reads all 3 sample videos end to end (frames flow, correct
      fps/resolution, `Processing → Online` transition).
- [x] RTSP reconnect state machine unit-tested with no network (4 dedicated tests).

---

## Next Up: Module 2 — Person Detection

The ingestion layer now hands off throttled, downscaled frames via a stable
interface, so detection can be developed entirely against local footage:

```python
from inference.video import create_video_source
with create_video_source("sample-data/entrance.mp4") as src:
    ok, frame = src.read()   # 640×360, ~10fps, ready for detect(frame)
```

Before starting Module 2, decide:
- Detector family (YOLO vs RT-DETR per PRD §10) and model size.
- Whether `analytics/` gets its own venv or shares `inference/`'s environment
  (still open from Module 0 — worth resolving before Module 6).

