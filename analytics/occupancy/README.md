# Module 5 — Occupancy Analytics

Computes dashboard occupancy metrics from Module 4 ENTRY/EXIT events (PRD §13).
First **pure analytics** module — no CV, preview of the Analytics Engine
(Module 10).

## Metrics

| Field | Meaning |
|-------|---------|
| `current_occupancy` | `total_entries − total_exits` (floored at 0 for MVP) |
| `today_visitors` | Cumulative ENTRY count since local midnight — only increases |
| `today_exits` | Cumulative EXIT count since local midnight |
| `peak_occupancy` | Highest `current_occupancy` seen today |
| `peak_occupancy_time` | Timestamp when peak occurred |

## Public API

```python
from analytics.counting import LineCounter
from analytics.occupancy import OccupancyTracker, StoreOccupancyAggregator

# Per camera (entrance line)
occupancy = OccupancyTracker("entrance", timezone="America/New_York")

for event in counter.update(tracks):
    snap = occupancy.process(event)
    print(snap.to_dict())

# Multi-camera store rollup
store = StoreOccupancyAggregator("store_1", ["entrance", "side_door"])
store_snap = store.process(event)  # routes by event.camera_id
```

Zone-level occupancy is reserved via `OccupancyScope.ZONE` for Module 6 — do
not hardcode single-camera-only assumptions in downstream consumers.

## Sample clips vs live cameras

**Offline sample videos** (`entrance.mp4`, etc.) are useful for testing event
pipelines, but **current occupancy is not ground truth** on random clips:

- People may already be inside when the clip starts → EXITS without prior
  ENTRYs are common.
- The tracker floors `current_occupancy` at **0** for MVP so the metric never
  goes negative.

**Reliable on clips:** `today_visitors`, `today_exits`, and peak (relative to
the clip's event sequence).

**Live installed cameras:** call `occupancy.reset()` when the stream starts on
an empty store (or at a known baseline) so `current_occupancy` tracks real
people inside via entries minus exits. Midnight rollover resets daily counters
automatically.

Persistence → Module 11. Event bus → Module 10.
