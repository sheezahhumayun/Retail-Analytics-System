# Retail Analytics

## Project Structure

| Module | Purpose |
|----------|----------|
| frontend | Next.js Dashboard |
| backend | FastAPI REST API |
| inference | Detection and Tracking Service |
| analytics | Zone, Queue, Occupancy, Heatmaps |
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
