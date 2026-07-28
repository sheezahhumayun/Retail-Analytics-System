# Module 9 — Queue Analytics

Queue length, wait-time estimates, and threshold alerts from Module 6 zone
events (PRD §19). A **queue zone is a zone** — draw a polygon with
``zone_type`` of ``queue``, ``checkout``, or ``waiting``.

## Public API

```python
from analytics.queues import QueueTracker, is_queue_zone
from analytics.zones import Zone, ZoneDetector, ZoneType

lane = Zone(
    zone_id="checkout_lane_1",
    zone_name="Checkout Lane 1",
    camera_id="checkout-cam",
    polygon_coordinates=((100, 200), (300, 200), (300, 400), (100, 400)),
    zone_type=ZoneType.QUEUE,
)
queues = QueueTracker(
    [lane],
    length_thresholds={"checkout_lane_1": 5},
    duration_thresholds={"checkout_lane_1": 120.0},
)
for event in zone_detector.update(tracks):
    result = queues.process(event)
```

## Metrics (PRD §19)

| Metric | Source |
|--------|--------|
| Current queue length | Zone occupancy (entries − exits), same as Module 5/6 |
| Average / max queue length | Samples of occupancy after each zone event |
| Estimated wait time | **MVP:** average completed dwell in the queue zone (historical). Phase 2: position-in-queue (PRD §37) |
| Queue duration | Continuous time the queue has been non-empty (current episode) |

## Threshold alerts (PRD §27)

``QUEUE_THRESHOLD`` events mirror Module 7's dwell-threshold pattern:

- **Length** — fires once when occupancy reaches ``queue_length_threshold``; resets when length drops below the threshold.
- **Duration** — fires once per non-empty episode when ``queue_duration_threshold`` seconds elapse; resets when the queue clears.

## Multi-lane checkout (one camera)

Draw **one polygon per lane** with distinct ``zone_id`` values. Each lane gets
independent metrics and thresholds. See Module 6 ``polygon_editor`` (merge zones
into one JSON per camera).

## Camera placement (PRD §34) — required reading

Queue zones need the **checkout or waiting area fully visible** in frame.

- People waiting **outside the polygon** (e.g. queue extends past the camera
  view) are **not counted** — this is expected geometry, not a detector bug.
- Wide-angle cameras: draw the polygon only over the visible lane(s); do not
  treat the whole frame as one queue unless the lane fills the view.
- Document this limitation in deployment guides for every install.

## Demo

```bash
python tests/scripts/run-queues-demo.py sample-data/checkout.mp4 --zone-config tests/videos/checkout_zones.json
python tests/scripts/run-queues-demo.py rtsp://10.0.0.5/stream --zone-config tests/videos/checkout_zones.json --camera-id checkout --duration 120
```

## Not in scope (deferred)

- Position-in-queue wait estimation → Phase 2 (PRD §37)
- Alert delivery UI → Module 15
- ``QueueMetrics`` DB persistence → Module 11
- ``GET /api/analytics/queues`` → Module 12
- Dashboard queue widgets → Module 13
