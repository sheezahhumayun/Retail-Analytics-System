# Module 8 — Heatmap Generation

Visual heatmaps from person foot-points and tracking trajectories (PRD §17).
First purely visual analytics output — density gradient overlaid on a static
reference frame.

## Public API

```python
from analytics.heatmaps import HeatmapEngine, HeatmapStore

store = HeatmapStore("data/heatmaps", timezone="America/New_York")
engine = HeatmapEngine("store-floor", 640, 360, grid_scale=4, store=store)
engine.set_reference_frame(reference_bgr)  # empty-store still, same 640×360

for tracks in pipeline:
    engine.update(tracks, timestamp=wall_clock_seconds)

engine.flush()  # persist hour buckets

# Full day vs lunch hour — different overlays from summed buckets
full = engine.render(day_start, day_end, include_live=False)
lunch = engine.render(lunch_start, lunch_end, include_live=False)
```

## Pipeline

1. **Accumulate** — foot-point hits + trajectory segments on a 1/4-resolution
   grid (configurable via `grid_scale`).
2. **Bucket** — flush in-memory data into per-camera, per-hour `.npz` files.
3. **Query** — `HeatmapStore.merge_range(camera, start, end)` sums buckets.
4. **Render** — Gaussian blur → normalize 0–255 → `COLORMAP_JET` → alpha-blend
   over reference frame. Grid is upsampled to reference dimensions before blend
   (no offset/scaling mismatch). Trajectory layer uses `COLORMAP_HOT` at lower
   alpha.

## Reference frame

Use a **static empty-store** image per camera (not a live frame). Must match
processed frame size exactly (`width` × `height` passed to `HeatmapEngine`).

Capture once per camera; Module 16 admin UI will manage this.

## Demo (file / RTSP / webcam)

```bash
# File replay
python tests/scripts/run-heatmap-demo.py sample-data/store.mp4

# RTSP — defaults to 120s; refresh overlay every 30s
python tests/scripts/run-heatmap-demo.py rtsp://user:pass@10.0.0.5/stream \
  --camera-id entrance --duration 120 --preview-every 30

# Webcam index 0 — run until Ctrl+C
python tests/scripts/run-heatmap-demo.py 0 --camera-id desk --duration 0 --preview
```

Live sources use wall-clock timestamps from `VideoSource.get_last_timestamp()`.
File replays use `--recording-start` + media time for hour-bucket keys.

- Customer flow analytics → Phase 2 (PRD §18 / §37)
- Dashboard heatmap widget → **Module 13**
- DB persistence → **Module 11** (file-backed hour buckets for MVP)
