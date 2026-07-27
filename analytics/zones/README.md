# Module 6 — Zone Management & Zone Analytics

Polygon-based zones (Entrance, Electronics, Checkout, etc.) with zone
entry/exit/presence detection and analytics computed from those events
(PRD §14–§15). Generalizes Module 4's line-crossing pattern into arbitrary
regions — foundation for dwell-time (Module 7) and heatmaps (Module 8).

## Public API

```python
from analytics.zones import Zone, ZoneConfig, ZoneDetector, ZoneAnalytics, MultiZoneAnalytics

zone = Zone(
    zone_id="electronics",
    zone_name="Electronics",
    camera_id="store-floor",
    polygon_coordinates=((50, 100), (300, 100), (300, 350), (50, 350)),
    zone_type=ZoneType.ELECTRONICS,
)
detector = ZoneDetector([zone])  # pass all zones for the camera
analytics = ZoneAnalytics(zone)

for frame in pipeline:
    tracks = tracker.update(detections)
    for event in detector.update(tracks):
        snap = analytics.process(event)
        print(event.to_dict(), snap.to_dict())
```

### Event types

| Transition | Event |
|------------|-------|
| Outside → Inside | `ZONE_ENTER` |
| Inside → Outside | `ZONE_EXIT` |
| Remains inside | `ZONE_PRESENCE` (includes `dwell_delta` for Module 7) |

### Analytics (PRD §15)

| Metric | Source |
|--------|--------|
| Zone visitors | Distinct track IDs with `ZONE_ENTER` |
| Current occupancy | Entries − exits (via `OccupancyTracker`, scope `ZONE`) |
| Total visits | Count of `ZONE_ENTER` events |
| Avg / max / min dwell | Completed visit durations from ENTER→EXIT |
| Traffic by hour | `ZONE_ENTER` bucketed by local hour |

## Detection algorithm

1. **Foot-point** — bottom-center of bbox via `cv2.pointPolygonTest()`.
2. **Per frame** — for each track, evaluate **every** enabled zone on that
   camera (multiple overlapping zones are supported).
3. **History pairs** — same rolling-buffer scan as `LineCounter` (Module 4).
4. **Debounce** — per zone+track: after `ZONE_ENTER`, suppress duplicate
   enters until `ZONE_EXIT`.
5. **Hysteresis** — `hysteresis_frames` (default `2`) consecutive inside/outside
   readings required before confirming ENTER/EXIT. Reduces boundary flapping
   when a foot-point briefly straddles an edge.

## Verifying ENTER/EXIT on real footage

The default demo output is dominated by `ZONE_PRESENCE` (people already inside
zones). Use `--transitions-only` to see only ENTER/EXIT plus a per-track
timeline and flapping warnings:

```bash
python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --transitions-only
```

Raise `--hysteresis-frames` (e.g. `3` or `4`) if you see rapid ENTER↔EXIT
pairs flagged as boundary flapping. Lower to `1` for maximum sensitivity.

## Zone configuration

Coordinates are in **processed frame pixels** (Module 1's downscaled output,
640px long side by default).

### MVP polygon editor (OpenCV)

```bash
python -m analytics.zones.polygon_editor sample-data/store-floor.mp4 --camera-id store-floor --zone-id electronics --zone-name Electronics --output tests/videos/store_floor_zones.json
```

Click polygon vertices → right-click or `c` to close → `s` to save. Re-running
with the same `--zone-id` merges into the existing config file.

Load saved config:

```python
config = ZoneConfig.load_json("tests/videos/store_floor_zones.json")
detector = ZoneDetector(config.enabled_zones)
```

Full admin UI → Module 16.

## Not in scope (deferred)

- Individual dwell event records / session export → **Module 7**
- Heatmaps → **Module 8**
- Event bus / persistence → Modules 10–11
