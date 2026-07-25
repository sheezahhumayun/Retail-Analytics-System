# Module 3 — Multi-Object Tracking

Assigns **temporary, anonymous track IDs** to detected people so the same
individual is recognized across consecutive frames (PRD §11). Every downstream
module (counting, dwell, zones, heatmaps) is built on track IDs, not raw
detections.

## Public API

```python
from inference.detection import create_detector
from inference.tracking import Tracker

tracker = Tracker(camera_id="entrance", track_buffer=30)

with create_detector() as det:
    detections = det.detect(frame, camera_id="entrance", timestamp=ts)
    tracks = tracker.update(detections)  # list[TrackedObject]
```

Each `TrackedObject` carries:

| Field | Purpose |
|---|---|
| `track_id` | Anonymous temporary ID (not stable across long occlusions) |
| `bbox` | Current bounding box |
| `class_id` / `class_name` | Detection class |
| `confidence` | Association confidence |
| `camera_id` / `timestamp` | Frame context |
| `position_history` | Last N centroids + bboxes (default 30) for line-cross / dwell |

## Algorithm

**ByteTrack** via the [`trackers`](https://github.com/roboflow/trackers) package
(Roboflow). It works purely on detection boxes + a Kalman filter — no extra
neural network — so CPU overhead on top of detection is negligible.

`supervision` is used for `Detections` conversion and IoU-based NMS before
tracking. The deprecated `supervision.ByteTrack` is **not** used; `trackers`
is the maintained successor.

## PRD §11 failure modes

| Concern | How it's handled |
|---|---|
| **Temporary occlusion** | `track_buffer` (default 30 frames) controls how long a lost track is remembered. Tune against footage where people walk behind shelving. At Module 1's 10fps throttle, 30 processed frames ≈ 3s of wall time. |
| **Track loss / re-ID** | ByteTrack may assign a **new ID** after a long occlusion. Full re-identification is a Phase 2 feature — documented here as a known MVP limitation, not solved in this module. |
| **Duplicate track reduction** | Pre-tracking confidence filter + IoU NMS; `min_confirmation_frames=2` suppresses single-frame flicker tracks before they are returned. |

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| `conf_threshold` | 0.4 | Matches Module 2 detector default |
| `nms_iou_threshold` | 0.5 | Pre-tracking NMS |
| `track_buffer` | 30 | Lost-track memory (frames) |
| `frame_rate` | 30.0 | Scales buffer for non-30fps sources |
| `min_confirmation_frames` | 2 | Tracks must appear 2 frames before output |
| `history_length` | 30 | Position buffer for Modules 4 & 7 |

## Lifecycle

Call `tracker.reset()` when switching cameras or starting a new video clip so
track IDs and history buffers don't bleed across sources.

## Known limitations (MVP)

1. **No cross-camera re-ID** — each `Tracker` instance is per-camera; the same
   person on two cameras gets two unrelated IDs.
2. **ID swap after long occlusion** — if someone is hidden for longer than
   `track_buffer` processed frames, they re-enter as a new track ID.
3. **Skipped frames** — Module 1's target-FPS throttle means the tracker sees
   every 3rd source frame at 10fps; motion between skipped frames is bridged
   by the Kalman filter but fast movement increases association errors.

## Not in scope (deferred)

- BoT-SORT / DeepSORT backends → future if ByteTrack accuracy is insufficient
- Appearance-based re-ID → Phase 2
- DB persistence of tracks → Module 11
