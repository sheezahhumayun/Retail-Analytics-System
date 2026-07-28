# Module 10 — Event Architecture & Analytics Engine

Formalizes PRD §27 event types and a central Analytics Engine that consumes
them to produce occupancy, zone, dwell, and queue metrics.

## Event schema

```python
class AnalyticsEvent(BaseModel):
    event_type: str          # PERSON_DETECTED | ENTRY | EXIT | ...
    camera_id: str
    zone_id: str | None = None
    track_id: str | None = None
    timestamp: datetime
    metadata: dict = {}
```

## Event bus (MVP)

:class:`EventBus` is an in-process ``queue.Queue`` with synchronous subscriber
dispatch. Producers call ``publish()``; the Analytics Engine subscribes on
construction. Module 19 swaps this for Kafka/RabbitMQ without changing the
schema.

## Producers

| Module | Events on bus |
|--------|----------------|
| Detection | ``PERSON_DETECTED`` (sampled via :class:`PersonDetectionSampler`) |
| Counting | ``ENTRY``, ``EXIT`` |
| Zones | ``ZONE_ENTER``, ``ZONE_EXIT`` (via engine :meth:`process_zone_event`) |
| Dwell | ``DWELL_THRESHOLD`` |
| Queues | ``QUEUE_THRESHOLD`` |
| Video (RTSP) | ``CAMERA_OFFLINE`` when reconnect retries are exhausted |

``ZONE_PRESENCE`` stays internal to the zone detector → engine path (needed for
dwell thresholds; not a PRD §27 bus event).

## Analytics Engine

Single consumer for aggregated metrics:

- **Occupancy** — from ``ENTRY`` / ``EXIT``
- **Zone analytics** — from zone events (enter/exit/presence)
- **Dwell aggregates** — from zone events + ``DWELL_THRESHOLD`` alerts
- **Queue metrics** — from zone events + ``QUEUE_THRESHOLD`` alerts

## Pipeline wiring

```python
bus = EventBus()
engine = AnalyticsEngine(bus, AnalyticsEngineConfig(
    camera_ids=[camera_id],
    zones=zones,
    dwell_thresholds={"promo": 30.0},
    queue_length_thresholds={"lane_1": 5},
))
counter = LineCounter(line, event_bus=bus)
sampler = PersonDetectionSampler(bus, camera_id)

for frame, ts in frames:
    dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
    sampler.maybe_publish(dets)
    tracks = tracker.update(dets)
    for _ in counter.update(tracks):
        pass
    for ze in zone_detector.update(tracks):
        engine.process_zone_event(ze)
    engine.close_stale_dwell_sessions(ts)
```

## Tests

```powershell
python -m pytest tests/test_events.py -q
python tests/scripts/run-events-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json
```
