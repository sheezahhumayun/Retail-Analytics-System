# Module 4 — Entry/Exit Counting Lines

Virtual counting lines administrators draw on the camera image. When a tracked
person crosses one, the system logs a structured **ENTRY** or **EXIT** event
(PRD §12). This is the platform's first structured analytics event — the same
pattern (geometry → crossing detection → emit event) is reused for zones
(Module 6) and queues (Module 9).

## Public API

```python
from analytics.counting import CountingLine, InsideSide, LineCounter

line = CountingLine(
    x1=120, y1=300, x2=520, y2=300,
    inside_side=InsideSide.RIGHT,
    camera_id="entrance",
    name="main_door",
)
counter = LineCounter(line)

for frame in pipeline:
    tracks = tracker.update(detections)
    for event in counter.update(tracks):
        print(event.to_dict())
```

### Event schema (PRD §27 seed)

```json
{
  "camera_id": "entrance",
  "track_id": "7",
  "event_type": "ENTRY",
  "timestamp": "2026-07-26T12:00:00+00:00"
}
```

- **Outside → Inside** = `ENTRY`
- **Inside → Outside** = `EXIT`

## Crossing algorithm

1. **Foot-point** — bottom-center of bbox `(cx, y2)`, not centroid. More
   accurate for angled CCTV where feet cross the threshold first.
2. **Segment test** — each frame, check whether the segment between the
   previous and current foot-point intersects the counting line.
3. **Direction** — compare inside/outside side before and after the crossing.
4. **Debounce** — per track: after `ENTRY`, suppress further `ENTRY` until
   `EXIT` fires (prevents jitter double-counts).

## Line configuration

Coordinates are in **processed frame pixels** (Module 1's downscaled output,
640px long side by default). The line editor downscales the first frame the
same way before display so you see the full image and clicks land in the
correct coordinate space.

### MVP line editor (OpenCV)

```bash
# PowerShell: use one line (bash \ continuation does not work in PS)
python -m analytics.counting.line_editor sample-data/entrance.mp4 --camera-id entrance --output tests/videos/entrance_line.json
```

A default `tests/videos/entrance_line.json` is checked in for smoke runs; replace it
after drawing a line tuned to your footage.

Click: line start → line end → a point on the **inside** of the store (the
store floor will be tinted **green** — if the wrong half lights up, press
``r`` and redo the inside click).

Load saved config:

```python
line = CountingLine.load_json("tests/videos/entrance_line.json")
```

Full admin UI → Module 16.

## Not in scope (deferred)

- Occupancy rollup (`entries - exits`) → Module 5
- Event bus / persistence → Modules 10–11
- Multi-line aggregation per camera → Module 16 / backend config
