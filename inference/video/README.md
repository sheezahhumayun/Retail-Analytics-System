# Video Ingestion Layer (Module 1)

A single frame-source abstraction over **files** (mp4/avi/mov), **RTSP CCTV
streams**, and **webcams**, so every downstream module (detection, tracking,
analytics) consumes one interface and never branches on where the frame came
from. This is the seam PRD §9 requires ("a common interface so analytics modules
do not depend directly on the input source").

## Public API

```python
from inference.video import create_video_source, CameraState
```

```python
class VideoSource:
    def open(self) -> None
    def read(self) -> tuple[bool, np.ndarray | None]
    def get_last_timestamp(self) -> float         # media time (files) or wall clock (live)
    def get_kept_frame_count(self) -> int
    def get_source_frame_index(self) -> int       # includes throttled/skipped frames
    def get_target_fps(self) -> float             # configured cap — not necessarily achieved
    def get_effective_fps(self) -> float          # measured wall-clock kept-frame rate
    def get_media_duration(self) -> float | None  # file sources only
    def get_fps(self) -> float                    # native source fps
    def get_source_resolution(self) -> tuple[int, int]  # native (w, h)
    def get_resolution(self) -> tuple[int, int]   # post-downscale (what you see)
    def get_state(self) -> CameraState            # PRD §8
    def is_live(self) -> bool                     # True for RTSP/webcam
    def release(self) -> None
    # also a context manager
```

`CameraState` mirrors PRD §8: `Disabled`, `Offline`, `Error`, `Processing`, `Online`.
The ingestion layer is the source of truth for the *true* state — the full
DB/UI camera management arrives in Module 16 and reads `get_state()`.

## Usage

```python
# File — develop against local footage
with create_video_source("sample-data/entrance.mp4") as src:
    ok, frame = src.read()   # already throttled + downscaled to 640px long side
    if ok:
        ts = src.get_last_timestamp()  # seconds from file start — use for all analytics

# Webcam — local demo
with create_video_source(0) as src:                 # device index
    ...

# RTSP — production CCTV (reconnect/backoff built in)
with create_video_source("rtsp://user:pass@10.0.0.5:554/stream") as src:
    ...
```

## What this layer owns (so nothing else has to)

1. **Target-FPS throttling** — `target_fps` (default 10, PRD §33's 10–15 fps
   target) vs source fps decides which frames to hand off (at 30fps source →
   process every 3rd). Skipped frames use `cv2.grab()` (cheap) instead of a full
   decode. Logic lives in `read()`, so downstream never re-implements it.
2. **Downscale** — frames are capped at 640px on the long side (configurable)
   before leaving this layer, using `cv2.INTER_AREA`. Detection never sees full
   1080p/4K. ("CPU reality check": decode + resize dominate cost before detection.)
3. **Reconnect** — RTSP sources back off and reopen after N consecutive failed
   reads; real CCTV/NVR streams drop intermittently and that is normal, not an
   edge case (PRD §8 "Error"/"Offline"). After a full reconnect cycle is
   exhausted, the source retries on a cooldown so a recovering NVR is picked up.
4. **Authoritative timestamps** — after each kept `read()`, call
   `get_last_timestamp()` for analytics. File sources use **media time**
   (`source_frame_index / source_fps`), not `kept_count / target_fps`. Live
   sources use wall-clock `time.time()`. `target_fps` only controls which
   frames are processed; faster GPU throughput must not stretch dwell times or
   hour buckets.

## Defaults

| Setting | Default | Why |
|---|---|---|
| `target_fps` | 10.0 | PRD §33 target rate (10–15 fps) |
| `target_long_side` | 640 | CPU reality check; long side of output frame |
| Source fps fallback | 30.0 | Stock footage / NVRs sometimes report 0 |

## Files

| File | Purpose |
|---|---|
| `base.py` | `VideoSource` ABC, `CameraState` enum, throttle/resize helpers |
| `file_source.py` | `FileVideoSource` (mp4/avi/mov via OpenCV/FFMPEG) |
| `rtsp_source.py` | `RTSPVideoSource` (FFMPEG backend + reconnect/backoff) |
| `webcam_source.py` | `WebcamVideoSource` (device index; `CAP_DSHOW` on Windows) |
| `factory.py` | `create_video_source(spec)` — routes by spec type |

## Verification

```bash
# inference/.venv must be active
python -m pytest tests/                      # 22 unit/integration tests
python tests/scripts/smoke_video_source.py sample-data/entrance.mp4
```

## Not in scope (deferred)

- DB persistence / camera-management UI → Module 16.
- Detection / tracking / zones → Modules 2+.
- Hardware/GPU decode acceleration → Module 17.
- If OpenCV's RTSP handling proves flaky on a specific NVR, swap the backend in
  `rtsp_source._build_capture()` to `CAP_GSTREAMER` or `ffmpeg-python` — no
  downstream module changes required.
