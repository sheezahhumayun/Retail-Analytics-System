# Module 7 — Dwell-Time Analytics

How long each tracked person remains inside a zone: individual dwell events,
aggregates (avg / median / max / distribution), and configurable threshold
alerts (PRD §16 / §27). Direct consumer of Module 6
`ZONE_ENTER` / `ZONE_EXIT` / `ZONE_PRESENCE` events.

## Public API

```python
from analytics.dwell import DwellTracker
from analytics.zones import ZoneDetector

dwell = DwellTracker(
    zones,
    dwell_thresholds={"electronics": 60.0},  # DWELL_THRESHOLD after 60s
    lost_track_timeout_seconds=5.0,
)

for event in zone_detector.update(tracks):
    result = dwell.process(event)
    if result.dwell_event:
        print(result.dwell_event.to_dict())
    if result.threshold_event:
        print(result.threshold_event.to_dict())  # fires once per visit

# End of each frame — close sessions whose track disappeared
dwell.close_stale_sessions(current_timestamp=frame_time)
print(dwell.all_snapshots())
```

## DwellEvent (PRD §31 DwellEvents entity)

Emitted on `ZONE_EXIT` (or track-loss timeout):

```json
{
  "camera_id": "store-floor",
  "zone_id": "electronics",
  "track_id": "7",
  "enter_timestamp": "2026-07-27T12:00:00+00:00",
  "exit_timestamp": "2026-07-27T12:01:30+00:00",
  "dwell_seconds": 90.0,
  "close_reason": "exit"
}
```

## Aggregates per zone

| Field | Meaning |
|-------|---------|
| `avg_dwell_seconds` | Mean of completed dwell events |
| `median_dwell_seconds` | Median of completed dwell events |
| `max_dwell_seconds` | Longest completed visit |
| `distribution` | Histogram: `0-30s`, `30-60s`, `1-3min`, `3-10min`, `10min+` |
| `active_sessions` | Open dwells not yet closed |

## Track-loss policy (approximation)

If a track has an open dwell but no zone event (including `ZONE_PRESENCE`) for
`lost_track_timeout_seconds` (default **5 s**), the session is closed using
`last_seen_timestamp` as the exit time with `close_reason: "track_lost"`.

This handles tracking failures without leaving dwells open forever. It is **not**
a real zone exit — document and tune the timeout for your camera FPS and
`track_buffer` setting.

Call `close_stale_sessions(current_timestamp)` once per processed frame.

## DWELL_THRESHOLD (PRD §27)

Per-zone `dwell_threshold_seconds` in `dwell_thresholds={zone_id: seconds}`.
When a currently-dwelling person exceeds the threshold, one `DwellThresholdEvent`
is emitted — **once per visit**, not every frame. Feeds Module 15 (Alerting).

## Not in scope (deferred)

- Alert UI / notification delivery → **Module 15**
- DB persistence of DwellEvents → **Module 11**
- Dashboard charts → **Module 13**
